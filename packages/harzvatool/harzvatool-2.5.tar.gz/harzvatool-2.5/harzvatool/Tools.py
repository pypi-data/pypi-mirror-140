
import logging
import torch.distributed as dist
import time
from datetime import datetime
import os
import pickle
from until import collect_env as collect_base_env
from pynvml import *
import platform 
class Tools:
    """
    print with time
    get_xdir(cls,filename,x=1)
    mk_dir(_path_or_file)


    nvmlInit()
    logger.info( f"Driver Version: {}")#显卡驱动版本)
    # deviceCount = nvmlDeviceGetCount()#几块显卡
    # for i in range(deviceCount):
    logger.info(f'Device{nvmlDeviceGetName(nvmlDeviceGetHandleByIndex(0))}')
    nvmlShutdown()
    """

    def computer_info():
        nvmlInit()
        deviceCount = nvmlDeviceGetCount()
        gpu_info={}
        # print("Driver Version:", nvmlSystemGetDriverVersion())
        gpu_info["driver_veision"]=nvmlSystemGetDriverVersion()
        
        for i in range(deviceCount):
            temp_list=[]
            handle = nvmlDeviceGetHandleByIndex(i)
            # print("Device", i, ":", nvmlDeviceGetName(handle)) #具体是什么显卡
            meminfo = nvmlDeviceGetMemoryInfo(handle)
            temp_list.append((meminfo.total/1024**2,meminfo.used/1024**2,meminfo.free/1024**2))
            gpu_info[f"{i}"]=temp_list
            # gpu_info[f"free_{i}"]=meminfo.free#第二块显卡剩余显存大小
            # gpu_info[f"used_M_{i}"]= meminfo.used/1024**2#这里是字节bytes，所以要想得到以兆M为单位就需要除以1024**2
            # gpu_info[f"total_{i}"]=meminfo.total#第二块显卡总的显存大小
        platform_info={}
        platform_info["uname"]=platform.uname() 
        platform_info["python_version"]=platform.python_version()
        platform_info["python_compiler"]=platform.python_compiler()
        return gpu_info,platform_info




    @staticmethod
    def str2bool(str):
        return True if str.lower() == 'true' else False
    @staticmethod
    def collect_env():
        env_info=collect_base_env()
        return env_info

    @classmethod
    def print(cls, info=None, txt_path=None):
        info = "" if info is None else "{} {}".format(cls.get_format_time(), info)
        print(info)

        if txt_path is not None:
            cls.write_to_txt(txt_path, "{}\n".format(info), reset=False)
            pass
        pass

    @staticmethod
    def get_format_time():
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    @staticmethod
    def write_to_txt(_path, _txt, reset=False):
        with open(_path, "w" if reset else "a") as f:
            f.writelines(_txt)
        pass

    # 保存文件
    @staticmethod
    def write_to_pkl(_path, _data):
        with open(_path, "wb") as f:
            pickle.dump(_data, f)
        pass

    # 读取文件
    @staticmethod
    def read_from_pkl(_path):
        with open(_path, "rb") as f:
            return pickle.load(f)
        pass

    @staticmethod 
    def makedirs(_path_or_file):
        if "." in os.path.basename(_path_or_file):
            new_dir = os.path.split(_path_or_file)[0]
        else:
            new_dir = _path_or_file
            pass
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
            pass
        return _path_or_file
    @staticmethod 
    def mkdir(_path_or_file):
        if "." in os.path.basename(_path_or_file):
            new_dir = os.path.split(_path_or_file)[0]
        else:
            new_dir = _path_or_file
            pass
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)
            pass
        return _path_or_file

    pass
    @classmethod
    def get_xdir(cls,filename,x=1):
        if x>1:
            filename=os.path.dirname(filename)
            return cls.get_xdir(filename,x-1)
        else:
            filename=os.path.basename(filename)
            return os.path.basename(filename)
    
    
    @classmethod
    def get_logger(cls,name='', log_file=None, mode='w',log_level=logging.INFO,show_level=False):
        logger_initialized = {}
        """Initialize and get a logger by name.

        If the logger has not been initialized, this method will initialize the
        logger by adding one or two handlers, otherwise the initialized logger will
        be directly returned. During initialization, a StreamHandler will always be
        added. If `log_file` is specified and the process rank is 0, a FileHandler
        will also be added.

        Args:
            name (str): Logger name.
            log_file (str | None): The log filename. If specified, a FileHandler
                will be added to the logger.
            log_level (int): The logger level. Note that only the process of
                rank 0 is affected, and other processes will set the level to
                "Error" thus be silent most of the time.

        Returns:
            logging.Logger: The expected logger.
        """
        logger = logging.getLogger(name)
        if name in logger_initialized:
            return logger
        # handle hierarchical names
        # e.g., logger "a" is initialized, then logger "a.b" will skip the
        # initialization since it is a child of "a".
        for logger_name in logger_initialized:
            if name.startswith(logger_name):
                return logger

        stream_handler = logging.StreamHandler()
        handlers = [stream_handler]

        if dist.is_available() and dist.is_initialized():
            rank = dist.get_rank()
        else:
            rank = 0

        # only rank 0 will add a FileHandler
        if rank == 0 and log_file is not None:
            file_handler = logging.FileHandler(log_file, mode)
            handlers.append(file_handler)
        # time_=cls.get_format_time()
        # formatter = logging.Formatter(
        #     '%(time_) - %(name)s - %(levelname)s - %(message)s') 

        formatter =logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') if show_level \
        else logging.Formatter('%(asctime)s - %(name)s - %(message)s') 

        for handler in handlers:
            handler.setFormatter(formatter)
            handler.setLevel(log_level)
            logger.addHandler(handler)

        if rank == 0:
            logger.setLevel(log_level)
        else:
            logger.setLevel(logging.ERROR)

        logger_initialized[name] = True

        return logger

    @classmethod
    def print_log(cls,msg, logger=None, level=logging.INFO):
        """Print a log message. 可以套用logger

        Args:
            msg (str): The message to be logged.
            logger (logging.Logger | str | None): The logger to be used.
                Some special loggers are:
                - "silent": no message will be printed.
                - other str: the logger obtained with `get_root_logger(logger)`.
                - None: The `print()` method will be used to print log messages.
            level (int): Logging level. Only available when `logger` is a Logger
                object or "root".
        """
        if logger is None:
            print(msg)
        elif isinstance(logger, logging.Logger):
            logger.log(level, msg)
        elif logger == 'silent':
            pass
        elif isinstance(logger, str):
            _logger = cls.get_logger(logger)
            _logger.log(level, msg)
        else:
            raise TypeError(
                'logger should be either a logging.Logger object, str, '
                f'"silent" or None, but got {type(logger)}')



    # def get_root_logger(name='',log_file=None, log_level=logging.INFO):
    #     """Get root logger.

    #     Args:
    #         log_file (str, optional): File path of log. Defaults to None.
    #         log_level (int, optional): The level of logger.
    #             Defaults to logging.INFO.

    #     Returns:
    #         :obj:`logging.Logger`: The obtained logger
    #     """
    # logger = get_logger(name=name, log_file=log_file, log_level=log_level)





if __name__ == '__main__':
    gpu_info,platform_info=Tools.computer_info()
    print(gpu_info)
    print(platform_info)