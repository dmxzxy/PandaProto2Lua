#!/usr/bin/env python
# -*- encoding:utf8 -*-
import os
import utils
from panpbtool.conf import globalsetting

def compile_proto(context, proto_path, out_dir):
    compile_binpath = globalsetting.BASE_DIR + "/" + "utils/bin/win32/protoc.exe"
    proto_dir = os.path.dirname(proto_path)
    proto_name = os.path.basename(proto_path)
    proto_name = proto_name.split('.')[0]
    cmd = '%s --proto_path="%s" --descriptor_set_out="%s/%s.pb" "%s"'%(compile_binpath, proto_dir, out_dir, proto_name, proto_path)
    utils.cmd_call(cmd)
