#!/usr/bin/env python
# -*- encoding:utf8 -*-
import os
import utils

def compile_proto(context, proto_path, out_dir):
    compile_binpath = os.path.dirname(os.path.realpath(__file__)) + "/" + "bin/win32/protoc.exe"
    proto_dir = os.path.dirname(proto_path)
    proto_name = os.path.basename(proto_path)
    proto_name = proto_name.split('.')[0]
    cmd = '%s --proto_path="%s" --descriptor_set_out="%s/%s.pb" "%s"'%(compile_binpath, proto_dir, out_dir, proto_name, proto_path)
    utils.cmd_call(cmd)
