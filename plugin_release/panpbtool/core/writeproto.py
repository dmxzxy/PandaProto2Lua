#!/usr/bin/env python
# -*- encoding:utf8 -*-

import os
from panpbtool.conf import globalsetting
from panpbtool.conf import protolabel
from panpbtool.conf import prototype
from panpbtool.utils import compileproto

file_indent = '    '

def write_comment(comment, indent=''):
    if comment != None and len(comment) > 0:
        return indent + '// ' + comment.encode('utf-8') + '\n'
    return '\n'

def write_enum(project, enum, indent=''):
    enum_str = ''
    enum_str += write_comment(enum.comment, indent)
    enum_str += indent + 'enum '+ enum.name.encode('utf-8') + ' {\n'

    values = enum.values
    for value in values:
        segIndent = indent + file_indent
        enum_str += segIndent+'%s = %d;' % (value.name.encode('utf-8'), value.number)
        enum_str += write_comment(value.comment, '      ')

    enum_str += indent+'};\n'
    return enum_str

def write_message(project, message, indent=''):
    content = ''
    content += write_comment(project.get_comment(message.location), indent)
    content += indent + 'message '+ message.name.encode('utf-8') + ' {\n'

    nested_enums = message.nested_enums
    for enum in nested_enums:
        content += write_enum(project, enum, file_indent + indent)

    nested_messages = message.nested_messages
    for msg in nested_messages:
        content += write_message(project, msg, file_indent + indent)

    fields = message.fields
    for field in fields:
        segIndent = indent + file_indent
        names = field.proto_type.name.split('.')
        protocolName = names[len(names)-1].encode('utf-8')
        content += segIndent + '%s %s %s = %d;' % (protolabel.get_name(field.label), protocolName, field.name.encode('utf-8'), field.number)
        content += write_comment(project.get_comment(field.location), '      ')

    content += indent+'};\n'
    return content

def do_export(context):
    project = context.project

    write_dir = context.write_path + "/" + globalsetting.PROTO_RAW_OUTPUT_FOLDER
    if not os.path.exists(write_dir):
        os.mkdir(write_dir)

    out_dir = context.write_path + "/" + globalsetting.LUA_OUTPUT_FOLDER
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    for module in project.modules:
        proto_name = module.name
        proto_file_path = write_dir + "/" + proto_name + '.proto'
        file_proto = open(proto_file_path, 'w')
        file_proto.write('//gen by auto, do not write\n\n')
        file_proto.write('syntax = "proto2";\n\n')

        file_proto.write('package %s;\n' % (module.fullname))
        file_proto.write('\n')

        for enum in module.enums:
            file_proto.write(str(write_enum(project, enum)))
        
        for msg in module.messages:
            file_proto.write(str(write_message(project, msg)))
            
        for protocol in module.protocols:
            file_proto.write(str(write_message(project, protocol)))

        file_proto.close()

        compileproto.compile_proto(proto_file_path, out_dir)