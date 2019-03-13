#!/usr/bin/env python
# -*- encoding:utf8 -*-

import subprocess
import traceback, sys
import base64

def cmd_call(cmd):
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

def load_binery_file_base64(fullPath):
    file_pb = open(fullPath, 'rb')
    bdata = file_pb.read()
    blen = file_pb.tell()
    file_pb.close()
    data = base64.b64encode(bdata)
    return data, blen