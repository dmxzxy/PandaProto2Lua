#!/usr/bin/env python
# -*- encoding:utf8 -*-

import os

file_indent = '    '

class ProtocolType:
    TYPE_DOUBLE         = 1
    TYPE_FLOAT          = 2
    TYPE_INT64          = 3
    TYPE_UINT64         = 4
    TYPE_INT32          = 5
    TYPE_FIXED64        = 6
    TYPE_FIXED32        = 7
    TYPE_BOOL           = 8
    TYPE_STRING         = 9
    TYPE_GROUP          = 10
    TYPE_MESSAGE        = 11
    TYPE_BYTES          = 12
    TYPE_UINT32         = 13
    TYPE_ENUM           = 14
    TYPE_SFIXED32       = 15
    TYPE_SFIXED64       = 16
    TYPE_SINT32         = 17
    TYPE_SINT64         = 18

ProtocolName = {
    ProtocolType.TYPE_DOUBLE   : 'double',
    ProtocolType.TYPE_FLOAT    : 'float',
    ProtocolType.TYPE_INT64    : 'int64',
    ProtocolType.TYPE_UINT64   : 'uint64',
    ProtocolType.TYPE_INT32    : 'int32',
    ProtocolType.TYPE_FIXED64  : 'fixed64',
    ProtocolType.TYPE_FIXED32  : 'fixed32',
    ProtocolType.TYPE_BOOL     : 'bool',
    ProtocolType.TYPE_STRING   : 'string',
    ProtocolType.TYPE_GROUP    : '',
    ProtocolType.TYPE_MESSAGE  : '',
    ProtocolType.TYPE_BYTES    : 'bytes',
    ProtocolType.TYPE_UINT32   : 'uint32',
    ProtocolType.TYPE_ENUM     : '',
    ProtocolType.TYPE_SFIXED32 : 'sfixed32',
    ProtocolType.TYPE_SFIXED64 : 'sfixed64',
    ProtocolType.TYPE_SINT32   : 'sint32',
    ProtocolType.TYPE_SINT64   : 'sint64',
}

class LabelType:
    LABEL_OPTIONAL      = 1
    LABEL_REQUIRED      = 2
    LABEL_REPEATED      = 3

LabelName = {
    LabelType.LABEL_OPTIONAL   : 'optional',
    LabelType.LABEL_REQUIRED   : 'required',
    LabelType.LABEL_REPEATED   : 'repeated',
}

def write_comment(comment, indent=''):
    if comment != None and len(comment) > 0:
        return indent + '// ' + comment.encode('utf-8') + '\n'
    return '\n'

def write_enum(enum, indent=''):
    enum_str = ''
    enum_str += write_comment(enum.comment, indent)
    enum_str += indent + 'enum '+ enum.name.encode('utf-8') + ' {\n'

    values = enum.values
    for value in values:
        segIndent = indent + file_indent
        enum_str += segIndent+'%s = %d;' % (value.name.encode('utf-8'), value.number)
        enum_str += write_comment(value.comment, '      ')

    enum_str += indent+'};\n'
    enum_str += '\n'
    return enum_str

def write_message(message, indent=''):
    content = ''
    content += write_comment(message.comment, indent)
    content += indent + 'message '+ message.name.encode('utf-8') + ' {\n'

    nested_enums = message.nested_enums
    for enum in nested_enums:
        content += write_enum(enum, file_indent + indent)

    nested_messages = message.nested_messages
    for msg in nested_messages:
        content += write_message(msg, file_indent + indent)

    fields = message.fields
    for field in fields:
        segIndent = indent + file_indent
        if field.protoType == ProtocolType.TYPE_ENUM:
            names = field.protoTypeName.split('.')
            protocolName = names[len(names)-1].encode('utf-8')
        elif field.protoType == ProtocolType.TYPE_MESSAGE:
            names = field.protoTypeName.split('.')
            protocolName = names[len(names)-1].encode('utf-8')
        else:
            protocolName = ProtocolName[field.protoType]
        content += segIndent + '%s %s %s = %d;' % (LabelName[field.labelType], protocolName, field.name.encode('utf-8'), field.number)
        content += write_comment(field.comment, '      ')

    content += indent+'};\n'
    content += '\n'
    return content

def do_export(context):
    project = context.project
    for module in project.modules:
        proto_file_path = "export/" + module.name + '.proto'
        file_proto = open(proto_file_path, 'w')
        file_proto.write('syntax = "proto2";\n\n')

        file_proto.write('package %s;\n' % (module.fullname))
        file_proto.write('\n')

        for enum in module.enums:
            file_proto.write(str(write_enum(enum)))
        
        for msg in module.messages:
            file_proto.write(str(write_message(msg)))
            
        for protocol in module.protocols:
            file_proto.write(str(write_message(protocol)))

        file_proto.close()