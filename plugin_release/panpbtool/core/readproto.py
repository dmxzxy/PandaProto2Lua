#!/usr/bin/env python
# -*- encoding:utf8 -*-

import sys
import base64
from panpbtool.conf import globalsetting
from panpbtool.utils import compileproto

from panpbtool.data import baserule
from panpbtool.data import baseadapter

def do_read(context):
    out_dir = context.write_path
    compileproto.create_proto_descriptor(out_dir, out_dir)

    protodesc_filepath = out_dir + "/" + globalsetting.PROTO_DESCRIPTOR_TXT
    raw_data = compileproto.load_proto_descripter(protodesc_filepath)
    context.raw_data = raw_data

    adapter = context.adapter
    if adapter == None:
        adapter = baseadapter.baseadapter()
    
    rule = context.rule
    if rule == None:
        rule = baserule.baserule(context)
    else:
        context.rule = context.rule(context)

    project = adapter.translate(context)
    context.project = project