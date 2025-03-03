# -*- coding: utf-8 -*-
# @Time    : 2020/6/19 16:41
# @Author  : Jeffery Paul
# @File    : mylogger.py

"""
2023/10/05, 添加 setup_logging(), 使用配置文件进行 logging 的配置.

"""

import logging
import logging.config
import datetime
import os
import json


def setup_logging(
        default_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "logconfig.json"),
        default_level=logging.DEBUG
):
    # _p_old_chdir = os.getcwd()
    # 修改当前路径至 PATH_ROOT，因为 logconfig.json 按照此路径写相对路径
    # os.chdir(PATH_ROOT)

    path = os.path.abspath(default_path)
    print(f'配置 logging config, {path}')
    if os.path.exists(path):
        with open(path, "r") as f:
            config: dict = json.load(f)
        # 创建 logs 文件输出目录
        if 'handlers' in config.keys():
            for _handler_key in config['handlers'].keys():
                if 'filename' in config['handlers'][_handler_key]:
                    _p_file = os.path.abspath(config['handlers'][_handler_key]['filename'])
                    _p_file_folder = os.path.dirname(_p_file)
                    if not os.path.isdir(_p_file_folder):
                        os.makedirs(_p_file_folder)
                        print(f'创建文件夹, {_p_file_folder}')
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

    # 恢复当前路径
    # os.chdir(_p_old_chdir)


"""
下面的弃用
"""


# logger计数
class MsgCounterHandler(logging.Handler):
    level2count = {}

    def __init__(self, *args, **kwargs):
        super(MsgCounterHandler, self).__init__(*args, **kwargs)
        self.level2count = {}

    def emit(self, record):
        l = record.levelname
        if l not in self.level2count:
            self.level2count[l] = 0
        self.level2count[l] += 1


class MyLogger(logging.Logger):
    def __init__(
            self, name, level=logging.INFO,
            is_file=True, output_root=None,
            file_name='log.txt', file_backup_count=15, file_level=logging.INFO,
            format_string='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            file_format_string='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ):
        self.name = name
        self.level = level
        logging.Logger.__init__(self, self.name, self.level)
        # (1)stream handler
        self.__setStreamHandler__(format_string=format_string, level=level)
        # (2)file handler
        if is_file:
            # 输出文件夹
            if output_root:
                path_file_output_root = os.path.abspath(output_root)
            else:
                path_file_output_root = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    'logs'
                )
            if not os.path.isdir(path_file_output_root):
                os.makedirs(path_file_output_root)
            self.__setFileHandler__(output_root=path_file_output_root,
                                    format_string=file_format_string,
                                    level=file_level, backup_count=file_backup_count)
        # (3)count handler
        self.__setMsgCountHandler__()

    # console输出
    def __setStreamHandler__(self, format_string, level):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(format_string))
        stream_handler.setLevel(level)
        self.addHandler(stream_handler)

    # 文件输出
    def __setFileHandler__(self, output_root, format_string, level, backup_count):
        # log 文件输出会冲突，隔日时
        # file_handler = handlers.TimedRotatingFileHandler(
        #     filename=file_name, backupCount=backup_count, when='D', encoding='utf-8'
        # )
        path_file = os.path.join(output_root, 'log_%s.txt' % datetime.datetime.today().strftime('%Y%m%d'))
        file_handler = logging.FileHandler(
            path_file, mode='a', encoding='gb2312'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(format_string))
        self.addHandler(file_handler)

    # 统计状态个数
    def __setMsgCountHandler__(self):
        self._mch = MsgCounterHandler()
        self.addHandler(self._mch)

    @property
    def count(self) -> dict:
        return self._mch.level2count
