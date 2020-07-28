#!/usr/bin/env python
# -*- encoding:utf8 -*-

# 这个文件是根据项目来更改的文件 

import sys
import re

from panpbtool.conf import protolabel
from panpbtool.data.baserule import baserule

class customrule(baserule):
    context = None
    def __init__(self, context):
        self.context = context

    def get_namespace(self):
        context = self.context
        raw_data = context.raw_data
        if not hasattr(context, "namespace"):
            project_namespace = ""
            for proto_file in raw_data.proto_file:
                project_namespace = proto_file.package
                index = project_namespace.rfind('.')
                if index != -1:
                    project_namespace = project_namespace[0:index]
                break
            context.namespace = project_namespace
        return context.namespace

    def get_module_name(self, module_desc):
        namespace = self.get_namespace()
        name = module_desc.package[(len(namespace)+1):]
        if len(name) == 0:
            return "global"
        return name

    def is_protocol(self, message_desc):
        message_name = message_desc.name

        if message_name.startswith('C2S'):
            return True
            
        if message_name.startswith('S2C'):
            return True

        return False

    def get_protocol_id(self, message_desc):
        context = self.context

        message_name = message_desc.name
        proto_ids = {
            "C2STestHelloWorldProto" : 1000,
            "S2CTestHelloWorldRetProto" : 1000,
            "S2CTestHelloWorldNotify" : 1001,
        }
        if message_name in proto_ids:
            _id = proto_ids[message_name]
            if _id is not None:
                return int(_id)
        else:
            print(message_name + " can not find id/n")
            return -1

        return -1

    def get_protocol_category(self, message_desc):
        message_name = message_desc.name

        if message_name.startswith('C2S'):
            return "Request"

        if message_name.startswith('S2C'):
            return "Response"

        return "Notification"