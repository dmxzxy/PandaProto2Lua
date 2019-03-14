#!/usr/bin/env python
# -*- encoding:utf8 -*-

import os

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from panpbtool import panpbtool
from panpbtool.utils import compileproto
from data_adapter import ProtoFileInputAdapter

import google.protobuf.compiler.plugin_pb2 as plugin_pb2
class Context():
    pass

def main():
    context = Context()

    out_dir = os.path.dirname(os.path.abspath(__file__)) + "/protocol"
    compileproto.create_proto_descriptor(out_dir, out_dir)

    adapter = ProtoFileInputAdapter(context)
    project = adapter.translate()
    panpbtool.write(os.path.dirname(os.path.realpath(__file__)) + "/export", project)

if __name__ == "__main__":
	main()