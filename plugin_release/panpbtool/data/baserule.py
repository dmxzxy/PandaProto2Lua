#!/usr/bin/env python
# -*- encoding:utf8 -*-

class baserule(object):
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
        context = self.context
        namespace = self.get_namespace(context)
        name = module_desc.package[(len(namespace)+1):]
        if len(name) == 0:
            return "global"
        return name

    def is_protocol(self, message_desc):
        return False

    def get_protocol_id(self, message_desc):
        return -1

    def get_protocol_category(self, message_desc):
        return "Request"