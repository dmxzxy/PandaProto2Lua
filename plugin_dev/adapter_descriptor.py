#!/usr/bin/env python
# -*- encoding:utf8 -*-

# translate descriptor to models
# the descriptor input in many different ways 

import models

class AdapterPbDescriptor:
    context = None
    def __init__(self, context):
        self.context = context

    def parse_namespace(self):
        code_gen_req = self.context.code_gen_req
        project_namespace = ""
        if not hasattr(self.context, "namespace"):
            for proto_file in code_gen_req.proto_file:
                project_namespace = proto_file.package
                index = project_namespace.rfind('.')
                if index != -1:
                    project_namespace = project_namespace[0:index]
                break
        else:
            project_namespace = self.context.namespace
        return project_namespace
    
    def iterator_enums(self, enums, belong):
        for enum_index in range(0, len(enums)):
            enum_desc = enums[enum_index]
            enum = models.Enum(
                name = enum_desc.name,
                fullname = belong.fullname + '.' + enum_desc.name,
                namespace = belong.fullname,
                localtion = belong.localtion + [5, enum_index])
            enum.save(belong)

            for enumvalue_index in range(0, len(enum_desc.value)):
                enumvalue_desc = enum_desc.value[enumvalue_index]
                enumvalue = models.EnumValue(
                    name = enumvalue_desc.name, 
                    fullname = enum.fullname + '.' + enumvalue_desc.name,
                    namespace = enum.fullname,
                    localtion = enum.localtion + [2, enumvalue_index])
                enumvalue.save(enum)
            
    def iterator_messages(self, messages, belong):
        for message_index in range(0, len(messages)):
            message_desc = messages[message_index]
                
            message = models.Message(
                name = message_desc.name,
                fullname = belong.fullname + '.' + message_desc.name,
                namespace = belong.fullname,
                localtion = belong.localtion + [4, message_index])
            message.save(belong)

            for field_index in range(0, len(message_desc.field)):
                field_desc = message_desc.field[field_index]
                field = models.MessageField(
                    name = field_desc.name, 
                    fullname = message.fullname + '.' + field_desc.name,
                    namespace = message.fullname,
                    number = field_desc.number,
                    protoType = field_desc.type,
                    protoTypeName = field_desc.type_name,
                    labelType = field_desc.label,
                    localtion = message.localtion + [2, field_index])
                field.save(message)
                
            self.iterator_enums(message_desc.enum_type, message)
            self.iterator_messages(message_desc.nested_type, message)

    def translate(self):
        code_gen_req = self.context.code_gen_req

        project = models.Project(namespace = self.parse_namespace())
        for proto_file in code_gen_req.proto_file:
            # comments 
            for location in proto_file.source_code_info.location:
                path = [str(proto_file.name)]
                for pathNode in location.path:
                    path.append(pathNode)
                comment = models.Comment(
                    path = str(path), 
                    content = (location.leading_comments+' '+location.trailing_comments).strip().replace("\n", "")
                )
                comment.save()

            module = models.get_object(models.Module, fullname = proto_file.package)
            if module == None:
                module = models.Module(
                    name = proto_file.package[(len(project.namespace)+1):len(proto_file.package)],
                    fullname = proto_file.package,
                    namespace = project.namespace,
                )
                module.save(project)
            module.localtion = [str(proto_file.name)]

            self.iterator_enums(proto_file.enum_type, module)
            self.iterator_messages(proto_file.message_type, module)
        return project
    
