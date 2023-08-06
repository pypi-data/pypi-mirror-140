#!/usr/bin/python -u
# -*- coding:utf-8 -*-

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
from operator import le
import re
from unittest import result

from ducat.helper import line_rstrip
from ducat.logregex import LogRegex
from ducat.logseparator import LogSeparator
from ducat.terminalcolor import allocate_color, colorize, TAGTYPES, termcolor, BLACK, RESET
from ducat.trans import Trans

__author__ = 'JacksGong'

TIME_WIDTH = 12
THREAD_WIDTH = 7
TAG_WIDTH = 23

width = -1
# noinspection PyBroadException
try:
    # Get the current terminal width
    import fcntl, termios, struct

    h, width = struct.unpack('hh', fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack('hh', 0, 0)))
except:
    pass

header_size = TAG_WIDTH + 1 + 3 + 1  # space, level, space


def indent_wrap(message):
    return message


def keywords_regex(content, keywords):
    return any(re.match(r'.*' + t + r'.*', content) for t in map(str.strip, keywords))
    
# tag过滤器，支持制定tag和level进行过滤，level包括：V,D,I,W,E
def tagwords_regex(tag, level, tagmap):
    result = False
    for key in tagmap:
        key = str.strip(key)
        result = result or (tagmap[key] is None or level in tagmap[key]) and re.match(r'.*' + key + r'.*', tag)
    return result



class LogProcessor:
    hide_same_tags = None
    trans = None
    tag_keywords = None
    line_keywords = None
    separator = None
    regex_parser = None
    highlight_list = None
    # target_time = None

    # tmp
    last_msg_key = None
    last_tag = None

    def __init__(self, hide_same_tags):
        self.hide_same_tags = hide_same_tags

    def setup_trans(self, trans_msg_map, trans_tag_map, hide_msg_list):
        self.trans = Trans(trans_msg_map, trans_tag_map, hide_msg_list)

    def setup_separator(self, separator_rex_list):
        if separator_rex_list is not None:
            self.separator = LogSeparator(separator_rex_list)

    def setup_highlight(self, highlight_list):
        self.highlight_list = highlight_list

    def setup_condition(self, tag_keywords, line_keywords=None):
        self.tag_keywords = tag_keywords
        self.line_keywords = line_keywords

    def setup_regex_parser(self, regex_exp):
        self.regex_parser = LogRegex(regex_exp)

    def process(self, origin_line):
        origin_line = line_rstrip(origin_line)

        if len(origin_line.strip()) <= 0:
            return None, None, False

        if self.regex_parser is None:
            return None, None, False

        date, time, level, tag, process, thread, message = self.regex_parser.parse(origin_line)
        if message is None:
            message = origin_line

        return self.process_decode_content(origin_line, date, time, level, tag, process, thread, message)

    # noinspection PyUnusedLocal
    def process_decode_content(self, line, date, time, level, tag, process, thread, message):

        match_condition = False
        rawmessage = message

        # filter
        if self.tag_keywords is not None and tag is not None:
            if tagwords_regex(tag, level, self.tag_keywords):
                match_condition = True



        if self.line_keywords is not None:
            if keywords_regex(line, self.line_keywords):
                match_condition = True

        msgkey = None
        # the handled current line
        linebuf = ''

        # date 
        if date is not None:
            date = date [-TIME_WIDTH:].rjust(TIME_WIDTH)
            linebuf += date 
            linebuf += ' '
        elif self.regex_parser.is_contain_date():
            linebuf += ' ' * TIME_WIDTH
            linebuf += ' '

        # time
        if time is not None:
            time = time[-TIME_WIDTH:].rjust(TIME_WIDTH)
            linebuf += time
            linebuf += ' '
        elif self.regex_parser.is_contain_time():
            linebuf += ' ' * TIME_WIDTH
            linebuf += ' '

        # process
        if process is not None:
            process = process .strip()
            process = process[-THREAD_WIDTH:].rjust(THREAD_WIDTH)
            linebuf += process 
            linebuf += ' '
        elif self.regex_parser.is_contain_process():
            linebuf += ' ' * THREAD_WIDTH
            linebuf += ' '

        # thread
        if thread is not None:
            thread = thread.strip()
            thread = thread[-THREAD_WIDTH:].rjust(THREAD_WIDTH)
            linebuf += thread
            linebuf += ' '
        elif self.regex_parser.is_contain_thread():
            linebuf += ' ' * THREAD_WIDTH
            linebuf += ' '

        # tag
        if tag is not None and (not self.hide_same_tags or tag != self.last_tag):
            self.last_tag = tag
            tag = tag.strip()
            color = allocate_color(tag)
            tag = tag.strip()
            tag = tag[-TAG_WIDTH:].rjust(TAG_WIDTH)
            linebuf += colorize(tag, fg=color)
            linebuf += ' '
        elif self.regex_parser.is_contain_tag():
            linebuf += ' ' * TAG_WIDTH
            linebuf += ' '

        # level
        if level is not None:
            if level in TAGTYPES:
                linebuf += TAGTYPES[level]
            else:
                linebuf += ' ' + level + ' '
            linebuf += ' '
        elif self.regex_parser.is_contain_level():
            linebuf += ' '
            linebuf += ' '

        # message
        # -separator
        if self.separator is not None:
            msgkey = self.separator.process(message)
            match_condition = msgkey is not None or match_condition

        # -trans
        if self.trans is not None:
            message,trans_msg_result = self.trans.trans_msg(message)
            message = self.trans.hide_msg(message)
            message,trans_tag_result = self.trans.trans_tag(tag, message)
            match_condition = trans_tag_result or trans_msg_result or match_condition

        if self.highlight_list is not None:
            for highlight in self.highlight_list:
                # highlight 可能是正则表达式，所以需要把所有匹配结果高亮替换
                hl_result = re.findall(highlight, rawmessage, re.IGNORECASE)
                if hl_result:
                    for match_hl in hl_result:
                        match_condition = True
                        message = message.replace(match_hl,
                                              termcolor(fg=BLACK, bg=allocate_color(match_hl)) + match_hl + RESET)

        linebuf += message

        return msgkey, linebuf, match_condition
