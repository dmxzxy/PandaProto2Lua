#!/usr/bin/env python
# -*- encoding:utf8 -*-

import os

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from panpbtool import panpbtool
from panpbtool.utils import compileproto
from proto_config import customrule

import google.protobuf.compiler.plugin_pb2 as plugin_pb2

def main():    
    out_dir = os.path.dirname(os.path.abspath(__file__)) + "/protocol"
    project = panpbtool.read(out_dir, customrule)
    panpbtool.write(os.path.dirname(os.path.realpath(__file__)) + "/export", project)

if __name__ == "__main__":
	main()