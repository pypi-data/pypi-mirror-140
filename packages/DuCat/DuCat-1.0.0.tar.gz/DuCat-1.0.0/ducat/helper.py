#!/usr/bin/python -u

"""
Copyright (C) 2017 Jacksgong(jacksgong.com)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from distutils import errors
import os
import re
import sys

from os import environ, getcwd

from os.path import exists

__author__ = 'JacksGong'

LOG_LEVELS = 'VDIWEF'
LOG_LEVELS_MAP = dict([(LOG_LEVELS[i], i) for i in range(len(LOG_LEVELS))])

NO_HOME_PATH = re.compile(r'~/(.*)')
HOME_PATH = environ['HOME']


# get the home case path
def handle_home_case(path):
    path = path.strip()
    if path.startswith('~/'):
        path = HOME_PATH + '/' + NO_HOME_PATH.match(path).groups()[0]
    return path


def is_path(path):
    if path.startswith('/') or path.startswith('~/') or path.startswith('./'):
        return True

    if exists(path):
        return True
    return False


def get_conf_path(conf_name):
    if not conf_name.endswith('.yml'):
        conf_name = conf_name + '.yml'

    cur_path_yml = '%s/%s' % (getcwd(), conf_name)
    if exists(cur_path_yml):
        result = cur_path_yml
    else:
        result = '~/.okcat/' + conf_name

    print('using config on %s' % result)
    return result


def print_unicode(line):
    if sys.version_info >= (3, 0):
        print(bytes.decode(line))
    else:
        print(line)

def line_rstrip(line):
    if sys.version_info >= (3, 0):
        return line.rstrip()
    else:
        return line.decode('utf-8', errors='ignore').rstrip()
def init_baseyml():
    config_path = HOME_PATH
    config_path = os.path.join(config_path, ".okcat")
    if not os.path.exists(config_path):
        os.makedirs(config_path)
    if os.path.isdir(config_path):
        # init base.yml
        print("init base yml")
        
        with open(os.path.join(config_path, "base.yml"), 'w') as baseyml:
            baseyml.write("tag-keyword-list:")
            baseyml.write("\n")
            baseyml.write("  'AndroidRuntime': W,E")
            baseyml.write("\n")
            baseyml.write("  'ActivityManager': E")
            baseyml.write("\n")
            baseyml.write("  'DEBUG': F")
            baseyml.write("\n")
            baseyml.write('log-line-regex: \'date,time,process,thread,level,tag,message = "(.\S*) *(.\S*) *(\d*) *(\d*) *([A-Z]) *([^:]*):\s*(.*)$"\'')
            baseyml.write("\n")
            baseyml.write('trans-msg-map:')
            baseyml.write("\n")
            baseyml.write('  \'event=SEND_EVENT.*name":"(\w*)\': "上报事件"')
            baseyml.write("\n")
            baseyml.write('  \'^((?!FinishHandleDirectives)\w*)\s*receive directive:\': "收到指令"')
            baseyml.write("\n")
            baseyml.write('  \'Start proc (\d+):([\w\.]+)\': "启动进程"')
            baseyml.write("\n")
            baseyml.write('  \'eventType:ACTIVITY_RESUMED, packageName:([\w\.]+)\': "页面进前台"')
            baseyml.write("\n")
            baseyml.write('  \'eventType:ACTIVITY_PAUSED, packageName:([\w\.]+)\': "页面进后台"')
            baseyml.write("\n")
            baseyml.write('  \'FATAL EXCEPTION:\': "Java崩溃"')
            baseyml.write("\n")
            baseyml.write('  \'START u\d+ \{flg=0x[01]+ cmp=([\w\.]+)\': "启动页面"')
            baseyml.write("\n")
            baseyml.write('  \'Fatal signal \d+\s+.*pid\s+(\d+)\s+(.*)\': "Native崩溃"')
            baseyml.write("\n")
            baseyml.write('  \'ANR in ([\w\.]+)\': "无响应ANR"')
            baseyml.write("\n")
            baseyml.flush()
            baseyml.close()
        
    else:
        print("init base yml fail, ~/.okcat is not dir")
        