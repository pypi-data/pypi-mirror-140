# -*- coding:utf-8 -*-
#
# Copyright (C) 2019-2020 Alibaba Group Holding Limited


from __future__ import print_function

from aostools import *


class Exportall(Command):
    common = True
    helpSummary = "Export file to aos_sdk dir"
    helpUsage = """
%prog [option]
"""
    helpDescription = """
Display the detailed compilation information of the current solution.
"""

    def _Options(self, p):
        p.add_option('-b', '--board',
                     dest='board_name', action='store', type='str', default=None,
                     help='show configuration of selected board')


    def Execute(self, opt, args):
        yoc = YoC()
        solution = yoc.getSolution(opt.board_name)
        if solution == None:
            put_string("The current directory is not a solution!")
            exit(-1)
        solution.install() 
        return 0
