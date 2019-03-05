#!/usr/bin/env python
# -*- encoding:utf8 -*-

import sys
import time
import os
import os.path as path

import json
import google.protobuf.compiler.plugin_pb2 as plugin_pb2
import google.protobuf.descriptor_pb2 as descriptor_pb2

FDP = descriptor_pb2.FieldDescriptorProto

# Windows will mangle our line-endings unless we do this.
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

from adapter_descriptor import AdapterPbDescriptor
import export_to_pb
import export_to_lua
class Context:
	pass

def main():
	fp = open("test.bin", 'rb')
	plugin_require_bin = fp.read()
	fp.close()

	fp = open("protomsg.go", "r")
	id_descript_data = fp.read()
	fp.close()

	code_gen_req = plugin_pb2.CodeGeneratorRequest()
	code_gen_req.ParseFromString(plugin_require_bin)

	context = Context()
	context.raw_data = code_gen_req
	context.id_descript_data = id_descript_data
	context.compile_binpath = "E:/workspace/PandaProto2Lua/bin/protoc.exe"
	context.proto_path = "E:/workspace/PandaProto2Lua/plugin_dev/export/raw/"
	if not os.path.exists(context.proto_path):
		os.mkdir(context.proto_path) 
	context.output_path = "E:/workspace/PandaProto2Lua/plugin_dev/export/lua/"
	if not os.path.exists(context.output_path):
		os.mkdir(context.output_path) 

	adapter = AdapterPbDescriptor(context)
	context.project = adapter.translate()
	export_to_pb.do_export(context)

	export_to_lua.do_export(context)

if __name__ == "__main__":
	main()
