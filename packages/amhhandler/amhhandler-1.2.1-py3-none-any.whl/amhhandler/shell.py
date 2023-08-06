#!/usr/bin/env python3
# -*- coding:utf-8 -*-
'''
@time   : 2020/10/20 19:13
@file   : shell.py
@author : 
@desc   : 
@exec   : 
'''
import subprocess


def run(exec_cmd, is_exit=0):
    """
    传入shell脚本，默认执行报错不退出当前执行脚本。
    :param exec_cmd:
    :param is_exit:
    :return:
    """
    r_shell = subprocess.Popen(
        exec_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = r_shell.communicate()
    r_code = r_shell.returncode
    if r_code == 0:
        return stdout, r_code
    else:
        err_msg = 'exit\nerror info:{err}\nexec shell failed: {cmd}'.format(
            err=stderr, cmd=exec_cmd)
        if is_exit:
            exit(err_msg)
        else:
            return err_msg, r_code
