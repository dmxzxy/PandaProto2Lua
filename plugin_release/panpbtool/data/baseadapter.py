
from panpbtool.data import middata
from panpbtool.conf import prototype

class baseadapter(object):
    def iterator_enums(self, enums, belong):
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
    
    def iterator_messages(self, messages, belong):
        rule = self.rule
        for message_index in range(0, len(messages)):
            message_desc = messages[message_index]

            message = None
            if rule.is_protocol(message_desc):
                message = belong.add_protocol(
                    id = rule.get_protocol_id(message_desc),
                    category = rule.get_protocol_category(message_desc),
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
                type_name = prototype.get_name(field_desc.type, field_desc.type_name)
                is_basic = prototype.get_is_basic(field_desc.type)
                message.add_field(
                    name = field_desc.name, 
                    fullname = message.fullname + '.' + field_desc.name,
                    namespace = message.fullname,
                    proto_type = middata.ProtocolType(field_desc.type, type_name, is_basic),
                    label = field_desc.label,
                    number = field_desc.number,
                    location = message.location + [2, field_index]
                )
            self.iterator_enums(message_desc.enum_type, message)
            self.iterator_messages(message_desc.nested_type, message)

    def translate(self, context):
        self.context = context

        rule = context.rule
        self.rule = rule

        raw_data = context.raw_data
        namespace = rule.get_namespace()

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
                    name = rule.get_module_name(proto_file),
                    fullname = proto_file.package,
                    namespace = namespace,
                    location = [str(proto_file.name)]
                )
            self.iterator_enums(proto_file.enum_type, module)
            self.iterator_messages(proto_file.message_type, module)

        return project