#!/usr/bin/env python
# -*- encoding:utf8 -*-
import os
import sys
from utils import utils
import base64
from panpbtool.conf import globalsetting
import google.protobuf.compiler.plugin_pb2 as plugin_pb2

PROTOC_EXE_NAME = "protoc.exe"

def fix_line_ending():
    if sys.platform == "win32":
        import os
        import msvcrt  # pylint: disable=import-error

        msvcrt.setmode(sys.stdout.fileno(),
                       os.O_BINARY)  # pylint: disable=E1103 ; the Windows version of os has O_BINARY
        msvcrt.setmode(sys.stderr.fileno(),
                       os.O_BINARY)  # pylint: disable=E1103 ; the Windows version of os has O_BINARY
        msvcrt.setmode(sys.stdin.fileno(),
                       os.O_BINARY)  # pylint: disable=E1103 ; the Windows version of os has O_BINARY

fix_line_ending()

def compile_proto(proto_path, out_dir):
    compile_binpath = globalsetting.BASE_DIR + "/" + "utils/bin/win32/" + PROTOC_EXE_NAME
    proto_dir = os.path.dirname(proto_path)
    proto_name = os.path.basename(proto_path)
    proto_name = proto_name.split('.')[0]
    cmd = '%s --proto_path="%s" --descriptor_set_out="%s/%s.pb" "%s"'%(compile_binpath, proto_dir, out_dir, proto_name, proto_path)
    utils.cmd_call(cmd)

def create_proto_descriptor(proto_path, out_dir):
    fileList = utils.get_file_list(proto_path, ['proto'])
    compile_binpath = globalsetting.BASE_DIR + "/" + "utils/bin/win32/" + PROTOC_EXE_NAME
    plugin_binpath = globalsetting.BASE_DIR + "/" + "utils/bin/win32/plugin/" + "run.bat"
    cmdHead = "%s -I=%s --makedesc_out=%s --plugin=protoc-gen-makedesc=%s "%(compile_binpath, proto_path, out_dir, plugin_binpath)
    cmd = cmdHead
    for f in fileList:
    	cmd += f
    	cmd += ' '
    utils.cmd_call(cmd)

def load_proto_descripter(filepath):
    fp = open(filepath, 'rb')
    raw_data = plugin_pb2.CodeGeneratorRequest()
    raw_data.ParseFromString(base64.b64decode(fp.read()))
    fp.close()
    return raw_data