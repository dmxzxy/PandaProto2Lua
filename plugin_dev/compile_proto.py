#!/usr/bin/env python
# -*- encoding:utf8 -*-

import subprocess
import traceback, sys
import base64

def __cmd_call(cmd):
    print 'Executing cmd:[%s]'%cmd
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)  
    (stdoutput,erroutput) = p.communicate()
    p.wait()
    rc = p.returncode
    if rc <> 0:
        erroutput = erroutput.decode(sys.getfilesystemencoding())
        stdoutput = stdoutput.decode(sys.getfilesystemencoding())
        if erroutput == u'':
            raise Exception(stdoutput.encode('utf-8'))
        else:
            raise Exception(erroutput.encode('utf-8'))
    return (stdoutput,erroutput)

def compile_proto(context, proto_name):
    compile_binpath = context.compile_binpath
    proto_path = context.proto_path
    output_path = context.output_path
    cmd = '%s --proto_path="%s" --descriptor_set_out="%s%s.pb" "%s.proto"'%(compile_binpath, proto_path, output_path, proto_name, proto_path + proto_name)
    __cmd_call(cmd)

def load_compile_proto(context, proto_name):
    output_path = context.output_path
    print(proto_name)
    file_pb_path = output_path + proto_name + '.pb'
    file_pb = open(file_pb_path,'rb')
    bdata = file_pb.read()
    blen = file_pb.tell()
    file_pb.close()
    data = base64.b64encode(bdata)
    return data,blen