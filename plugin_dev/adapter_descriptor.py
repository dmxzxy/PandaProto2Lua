#!/usr/bin/env python
# -*- encoding:utf8 -*-

# translate descriptor to models
# the descriptor input in many different ways 

import models
import middata
import protocol_type
import protocol_config

class AdapterPbDescriptor:
    context = None
    def __init__(self, context):
        self.context = context

    def iterator_enums2(self, enums, belong):
        for enum_index in range(0, len(enums)):
            enum_desc = enums[enum_index]
            enum = belong.add_enum(
                name = enum_desc.name,
                fullname = belong.fullname + '.' + enum_desc.name,
                namespace = belong.fullname,
                location = belong.location + [5, enum_index]
            )
            for enumvalue_index in range(0, len(enum_desc.value)):
                enumvalue_desc = enum_desc.value[enumvalue_index]
                enum.add_enumvalue(
                    name = enumvalue_desc.name, 
                    fullname = enum.fullname + '.' + enumvalue_desc.name,
                    namespace = enum.fullname,
                    location = enum.location + [2, enumvalue_index]
                )
    
    def iterator_messages2(self, messages, belong):
        for message_index in range(0, len(messages)):
            message_desc = messages[message_index]

            message = None
            if protocol_config.is_protocol(self.context, message_desc):
                message = belong.add_protocol(
                    id = protocol_config.get_protocol_id(self.context, message_desc),
                    category = protocol_config.get_protocol_category(self.context, message_desc),
                    name = message_desc.name,
                    fullname = belong.fullname + '.' + message_desc.name,
                    namespace = belong.fullname,
                    location = belong.location + [4, message_index]
                )
            else:
                message = belong.add_message(
                    name = message_desc.name,
                    fullname = belong.fullname + '.' + message_desc.name,
                    namespace = belong.fullname,
                    location = belong.location + [4, message_index]
                )
                
            for field_index in range(0, len(message_desc.field)):
                field_desc = message_desc.field[field_index]
                type_name = protocol_type.get_type_name(field_desc.type, field_desc.type_name)
                is_basic = protocol_type.get_is_basic_type(field_desc.type)
                message.add_field(
                    name = field_desc.name, 
                    fullname = message.fullname + '.' + field_desc.name,
                    namespace = message.fullname,
                    proto_type = middata.ProtocolType(field_desc.type, type_name, is_basic),
                    label = field_desc.label,
                    number = field_desc.number,
                    location = message.location + [2, field_index]
                )
            self.iterator_enums2(message_desc.enum_type, message)
            self.iterator_messages2(message_desc.nested_type, message)


    def translate(self):
        raw_data = self.context.raw_data

        protocol_config.init(self.context)

        namespace = protocol_config.get_namespace(self.context)

        project = middata.Project()
        for proto_file in raw_data.proto_file:
            # comments 
            for location in proto_file.source_code_info.location:
                path = [str(proto_file.name)]
                for pathNode in location.path:
                    path.append(pathNode)

                content = (location.leading_comments+' '+location.trailing_comments).strip().replace("\n", "")
                project.add_comment(str(path), content)
            
            module = project.get_module(fullname = proto_file.package)
            if module == None:
                module = project.add_module(
                    name = protocol_config.get_module_name(self.context, proto_file),
                    fullname = proto_file.package,
                    namespace = namespace,
                    location = [str(proto_file.name)]
                )
            self.iterator_enums2(proto_file.enum_type, module)
            self.iterator_messages2(proto_file.message_type, module)

        return project