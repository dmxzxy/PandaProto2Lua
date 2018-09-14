import os
import time
import traceback, sys
from protocal.utils import cmd_call
from protocal.utils import get_file_list
from string import strip
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

import json
from protocal.models import *


PROTOC_BIN_NAME = 'win32/protoc.exe'
proto_parse_plugin_path = 'proto_parse_plugin'
proto_parse_plugin_exe = 'runparse.bat'
proto_parse_plugin_outputpath = 'protocal/proto_parse_output'

#// 0 is reserved for errors.
#// Order is weird for historical reasons.
#TYPE_DOUBLE         = 1;
#TYPE_FLOAT          = 2;
#// Not ZigZag encoded.  Negative numbers take 10 bytes.  Use TYPE_SINT64 if
#// negative values are likely.
#TYPE_INT64          = 3;
#TYPE_UINT64         = 4;
#// Not ZigZag encoded.  Negative numbers take 10 bytes.  Use TYPE_SINT32 if
#// negative values are likely.
#TYPE_INT32          = 5;
#TYPE_FIXED64        = 6;
#TYPE_FIXED32        = 7;
#TYPE_BOOL           = 8;
#TYPE_STRING         = 9;
#TYPE_GROUP          = 10;  // Tag-delimited aggregate.
#TYPE_MESSAGE        = 11;  // Length-delimited aggregate.

# New in version 2.
#TYPE_BYTES          = 12;
#TYPE_UINT32         = 13;
#TYPE_ENUM           = 14;
#TYPE_SFIXED32       = 15;
#TYPE_SFIXED64       = 16;
#TYPE_SINT32         = 17;  // Uses ZigZag encoding.
#TYPE_SINT64         = 18;  // Uses ZigZag encoding.

class FieldType:
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

FName = {
    FieldType.TYPE_DOUBLE   : 'double',
    FieldType.TYPE_FLOAT    : 'float',
    FieldType.TYPE_INT64    : 'int64',
    FieldType.TYPE_UINT64   : 'uint64',
    FieldType.TYPE_INT32    : 'int32',
    FieldType.TYPE_FIXED64  : 'fixed64',
    FieldType.TYPE_FIXED32  : 'fixed32',
    FieldType.TYPE_BOOL     : 'bool',
    FieldType.TYPE_STRING   : 'string',
    FieldType.TYPE_GROUP    : '',
    FieldType.TYPE_MESSAGE  : '',
    FieldType.TYPE_BYTES    : 'bytes',
    FieldType.TYPE_UINT32   : 'uint32',
    FieldType.TYPE_ENUM     : '',
    FieldType.TYPE_SFIXED32 : 'sfixed32',
    FieldType.TYPE_SFIXED64 : 'sfixed64',
    FieldType.TYPE_SINT32   : 'sint32',
    FieldType.TYPE_SINT64   : 'sint64',
}

class LabelType:
    LABEL_OPTIONAL      = 1;
    LABEL_REQUIRED      = 2;
    LABEL_REPEATED      = 3;

LName = {
    LabelType.LABEL_OPTIONAL   : 'optional',
    LabelType.LABEL_REQUIRED   : 'required',
    LabelType.LABEL_REPEATED   : 'repeated',
}
class cls_context:
    project = None
    setting = None
    def __str__(self):
        return self.project.title

def parse_proto_files(context):
    proto_sync_path = context.proto_sync_path + 'protocol'
    l = get_file_list(proto_sync_path,['proto'])
    cmdHead = "%s -I=%s --parse_out=%s --plugin=protoc-gen-parse=%s "%(context.bin_path+PROTOC_BIN_NAME, proto_sync_path, proto_parse_plugin_outputpath, context.bin_path+proto_parse_plugin_path+'/'+proto_parse_plugin_exe)

    cmd = cmdHead
    for f in l:
    	cmd += f
    	cmd += ' '
    cmd_call(cmd)

def doSyncEnumValues(context, module, enum, enumvalues):
    EnumSegList = []
    for value in enumvalues:
        segment_name = value['name']
        segment_desc = value['desc']
        if len(segment_desc) == 0:
            segment_desc = segment_name
        segment_namespace = value['fullname']
        segment_value = value['number']
        EnumSegList.append(EnmuSegment(name = strip(segment_name),
                                    namespace = segment_namespace,
                                    value = segment_value,
                                    desc = segment_desc,
                                    belong = enum,))
    return EnumSegList


#inner_type 0:global 1:protocal 2:customtype
def doSyncEnum(context, module, message, enums, inner_type = 0):
    cur_project = context.cur_project
    inner_protocal = None;
    inner_customtype = None;
    if inner_type == 1:
        inner_protocal = message;
    elif inner_type == 2:
        inner_customtype = message;

    SegTypeList = []
    for enum_dict in enums:
        enum_name = enum_dict['name']
        enum_desc = enum_dict['desc']
        if len(enum_desc) == 0:
            enum_desc = enum_name
        enum_namespace = enum_dict['fullname']

        seg = SegmentType(name = strip(enum_namespace),
                           desc = enum_desc,
                           module = module,
                           protocal = inner_protocal,
                           is_basic = False,
                           project = cur_project,
                           provider_type = 1,
                           )

        SegTypeList.append(seg)

    SegmentType.objects.bulk_create(SegTypeList)

    EnumList = []
    for enum_dict in enums:
        enum_name = enum_dict['name']
        enum_desc = enum_dict['desc']
        if len(enum_desc) == 0:
            enum_desc = enum_name
        enum_namespace = enum_dict['fullname']

        seg = get_object_or_404(SegmentType, name = enum_namespace)
        enum = Enum(name = strip(enum_name),
                    desc = enum_desc,
                    type = seg,
                    module = module,
                    namespace = enum_namespace,
                    belong = inner_protocal,
                    belong_ct = inner_customtype,)
        EnumList.append(enum)

    Enum.objects.bulk_create(EnumList)

    EnumSegList = []
    for enum_dict in enums:
        enum_namespace = enum_dict['fullname']
        enum = get_object_or_404(Enum, namespace = enum_namespace)
        EnumSegList += doSyncEnumValues(context, module, enum, enum_dict['valuelist'])
    EnmuSegment.objects.bulk_create(EnumSegList)

def doSyncCustomTypeField(context, module, message, fields):
    SegList = []
    for field_dict in fields:
        customtype_segment_name = field_dict['name']
        customtype_segment_desc = field_dict['desc']
        if len(customtype_segment_desc) == 0:
            customtype_segment_desc = customtype_segment_name
        customtype_segment_namespace = field_dict['fullname']
        customtype_segment_protocal_type_id = field_dict['label']
        customtype_segment_type_type = field_dict['type']

        customtype_segment_type = None
        customtype_segment_default_enum_segment = None
        if customtype_segment_type_type == FieldType.TYPE_ENUM:
            segment_type_name = field_dict['type_name'][1:]
            customtype_segment_type = get_object_or_404(Enum, namespace=segment_type_name).type
            if field_dict.has_key('default_value'):
                default_value_namespace = segment_type_name + '.' + field_dict['default_value']
                customtype_segment_default_enum_segment = get_object_or_404(EnmuSegment, namespace=default_value_namespace)
        elif customtype_segment_type_type == FieldType.TYPE_MESSAGE:
            segment_type_name = field_dict['type_name'][1:]
            customtype_segment_type = get_object_or_404(CustomType, namespace=segment_type_name).type
        else:
            customtype_segment_type = get_object_or_404(SegmentType, name=FName[customtype_segment_type_type])


        customtype_segment_protocal_type = get_object_or_404(SegmentProtoType, name=LName[customtype_segment_protocal_type_id]) 
        SegList.append(CustomTypeSegment(name = strip(customtype_segment_name),
                                        namespace = customtype_segment_namespace,
                                        desc = customtype_segment_desc,
                                        belong = message,
                                        protocal_type = customtype_segment_protocal_type,
                                        type = customtype_segment_type,
                                        defaultEnum = customtype_segment_default_enum_segment))
    CustomTypeSegment.objects.bulk_create(SegList)


def doSyncCustomType(context, module, message, messages, inner_type = 0):
    cur_project = context.cur_project
    inner_protocal = None;
    inner_customtype = None;
    if inner_type == 1:
        inner_protocal = message;
    elif inner_type == 2:
        inner_customtype = message;

    SegTypeList = []
    for message_dict in messages:
        customtype_name = message_dict['name']
        customtype_desc = message_dict['desc']
        if len(customtype_desc) == 0:
            customtype_desc = customtype_name
        customtype_namespace = message_dict['fullname']
        SegTypeList.append(SegmentType(name = strip(customtype_namespace),
                                       desc = customtype_desc,
                                       module = module,
                                       protocal = inner_protocal,
                                       is_basic = False,
                                       project = cur_project,
                                       provider_type = 2,
                                       ))
    SegmentType.objects.bulk_create(SegTypeList)

    CustomTypeList = []
    for message_dict in messages:
        customtype_name = message_dict['name']
        customtype_desc = message_dict['desc']
        if len(customtype_desc) == 0:
            customtype_desc = customtype_name
        customtype_namespace = message_dict['fullname']
        seg = get_object_or_404(SegmentType, name = customtype_namespace)
        CustomTypeList.append(CustomType(name = strip(customtype_name),
                                        desc = customtype_desc,
                                        type = seg,
                                        module = module,
                                        namespace = customtype_namespace,
                                        belong = inner_protocal,
                                        belong_ct = inner_customtype,
                                        ))
    CustomType.objects.bulk_create(CustomTypeList)


    for message_dict in messages:
        customtype_namespace = message_dict['fullname']
        customtype = get_object_or_404(CustomType, namespace = customtype_namespace)

        enumlist = message_dict['enumlist'];
        doSyncEnum(context, module, customtype, enumlist, 2);

        nestedtypelist = message_dict['nestedtypelist'];
        doSyncCustomType(context, module, customtype, nestedtypelist, 2)

        fieldlist = message_dict['fieldlist'];
        doSyncCustomTypeField(context, module, customtype, fieldlist)

def doSyncMessageField(context, module, message, fields):
    SegList = []
    SegPackedList = []
    for field_dict in fields:
        segment_name = field_dict['name']
        segment_desc = field_dict['desc']
        if len(segment_desc) == 0:
            segment_desc = segment_name
        segment_type_type = field_dict['type']

        segment_protocal_type_id = field_dict['label']
        segment_namespace = message.namespace + '.' + segment_name

        segment_type = None
        segment_default_enum_segment = None
        if segment_type_type == FieldType.TYPE_ENUM:
            segment_type_name = field_dict['type_name'][1:]
            segment_type = get_object_or_404(Enum, namespace=segment_type_name).type
            if field_dict.has_key('default_value'):
                default_value_namespace = segment_type_name + '.' + field_dict['default_value']
                segment_default_enum_segment = get_object_or_404(EnmuSegment, namespace=default_value_namespace)
        elif segment_type_type == FieldType.TYPE_MESSAGE:
            segment_type_name = field_dict['type_name'][1:]
            segment_type = get_object_or_404(CustomType, namespace=segment_type_name).type
        else:
            segment_type = get_object_or_404(SegmentType, name=FName[segment_type_type])

        segment_extra_type1 = None
        segment_extra_type2 = None
        segment_protocal_type = get_object_or_404(SegmentProtoType, name=LName[segment_protocal_type_id]) 

        SegList.append(Segment(name = strip(segment_name),
                                desc = segment_desc,
                                protocal = message,
                                protocal_type = segment_protocal_type,
                                type = segment_type,
                                extra_type1 = segment_extra_type1,
                                extra_type2 = segment_extra_type2,
                                namespace = strip(segment_namespace),
                                defaultEnum = segment_default_enum_segment
                                ))

        if field_dict.has_key('packed'):
            is_packed = field_dict['packed']
            SegPackedList.append(SegmentPackedOption(segment_namespace = strip(segment_namespace), is_packed = is_packed))
    Segment.objects.bulk_create(SegList)
    SegmentPackedOption.objects.bulk_create(SegPackedList)

def doSyncMessage(context, module, message_dict):
    cur_project = context.cur_project
    protocal_name = message_dict['name'];
    protocal_desc = message_dict['desc'];
    if len(protocal_desc) == 0:
        protocal_desc = protocal_name
    protocal_namespace = module.namespace + '.' + protocal_name
    protocal_protocal_id = message_dict['id'];
    protocal_protocal_unique_id = cur_project.id + protocal_protocal_id
    protocal_type = get_object_or_404(ProtocalType, pk=1) 

    start_CPU = time.clock()
    message = get_object_or_404(Protocal, namespace = strip(protocal_namespace))

    enumlist = message_dict['enumlist'];
    doSyncEnum(context, module, message, enumlist, 1);

    nestedtypelist = message_dict['nestedtypelist'];
    doSyncCustomType(context, module, message, nestedtypelist, 1)

    fieldlist = message_dict['fieldlist'];
    doSyncMessageField(context, module, message, fieldlist)

    end_CPU = time.clock()
    print '+++++++++++++ Protocal :',protocal_protocal_unique_id, ' ', protocal_name, ' ',end_CPU-start_CPU


def doSyncModule(context, module_dict):
    cur_project = context.cur_project
    namespace = context.namespace;
    module_namespace = module_dict['package'];
    module_modulename = module_namespace.replace(namespace+'.','');
    module_name = module_modulename
    module_desc = module_modulename

    if namespace == module_namespace:
        start_CPU = time.clock()
        print '\n------------- sync Module : ', 'global', ' --------------'

        global_module = Module(
                        id = 0,
                        name = 'global',
                        namedesc = 'global',
                        desc = '',
                        project = cur_project,
                        namespace = cur_project.namespace)


        enumlist = module_dict['enumlist']
        doSyncEnum(context, global_module, None, enumlist)
            
        customtypes = module_dict['customtypes']
        doSyncCustomType(context, global_module, None, customtypes)

        protocals = module_dict['protocals']
        for m in protocals:
            doSyncMessage(context, global_module, m);

        end_CPU = time.clock()
        print '+++++++++++++ sync Module : ', global_module.name, ' ', end_CPU-start_CPU, '++++++++++++++'
    else:
        start_CPU = time.clock()
        print '\n------------- sync Module : ', module_modulename, '--------------'

        module = get_object_or_404(Module, namespace = module_namespace)

        enumlist = module_dict['enumlist']
        doSyncEnum(context, module, None, enumlist);

        customtypes = module_dict['customtypes']
        doSyncCustomType(context, module, None, customtypes)

        protocals = module_dict['protocals']
        for m in protocals:
            doSyncMessage(context, module, m);

        end_CPU = time.clock()
        print '+++++++++++++ sync Module : ', module_modulename, ' ', end_CPU-start_CPU, '++++++++++++++'

def doSyncAll(context):
    cur_project = context.cur_project
    namespace = context.namespace;
    proto_parse_dict = context.proto_parse_dict
    ModuleList = []
    for module_dict in proto_parse_dict['modulelist']:
        module_namespace = module_dict['package'];
        messagelist = module_dict['messagelist']
        protocals = []
        customtypes = []
        for message_dict in messagelist:
            if message_dict.has_key('id'):
                protocals.append(message_dict)
            else:
                customtypes.append(message_dict)
        module_dict['protocals'] = protocals
        module_dict['customtypes'] = customtypes

        if namespace == module_namespace:
            pass
        else:
            namespace = context.namespace;
            module_modulename = module_namespace.replace(namespace+'.','');
            module_name = module_modulename
            module_desc = module_modulename
            ModuleList.append(Module(name = module_modulename,
                    namedesc = strip(module_name),
                    desc = module_desc,
                    project = cur_project,
                    namespace = module_namespace))
    Module.objects.bulk_create(ModuleList)


    ProtocalList = []
    for module_dict in proto_parse_dict['modulelist']:
        module_namespace = module_dict['package'];
        module = None
        if namespace == module_namespace:
            module = Module(id = 0,
                            name = 'global',
                            namedesc = 'global',
                            desc = '',
                            project = cur_project,
                            namespace = cur_project.namespace)
        else:
            module = get_object_or_404(Module, namespace = module_namespace)

        protocallist = module_dict['protocals']
        for message_dict in protocallist:
            protocal_name = message_dict['name'];
            protocal_desc = message_dict['desc'];
            if len(protocal_desc) == 0:
                protocal_desc = protocal_name
            protocal_namespace = module.namespace + '.' + protocal_name
            protocal_protocal_id = message_dict['id'];
            protocal_protocal_unique_id = cur_project.id + protocal_protocal_id
            protocal_type = get_object_or_404(ProtocalType, pk=1) 

            message = Protocal(name = strip(protocal_name),
                                desc = protocal_desc,
                                module = module,
                                protocal_id = protocal_protocal_id,
                                protocal_unique_id = protocal_protocal_unique_id,
                                type = protocal_type,
                                namespace = strip(protocal_namespace),
                                relate_protocal = None,
                                )
            ProtocalList.append(message)

            try:
                protocalExt = ProtocalExtension.objects.get(protocal_id = protocal_protocal_id)
            except ObjectDoesNotExist:
                protocalExt = None

            if protocalExt == None:
                strip_protocal_name = strip(protocal_name).decode('unicode')
                if strip_protocal_name.endwith("Request"):
                    protocal_type = get_object_or_404(ProtocalType, pk=1) 
                elif strip_protocal_name.endwith("Response"):
                    protocal_type = get_object_or_404(ProtocalType, pk=2) 
                elif strip_protocal_name.endwith("Notify"):
                    protocal_type = get_object_or_404(ProtocalType, pk=3) 

                protocalExt = ProtocalExtension(module = module,
                                                protocal_name = strip(protocal_name),
                                                protocal_id = protocal_protocal_id,
                                                protocal_ref = None,
                                                protocal_type = protocal_type,
                                                )
                protocalExt.save()
            else:
                protocalExt.module = module
                protocalExt.save()

    Protocal.objects.bulk_create(ProtocalList)

    for module_dict in proto_parse_dict['modulelist']:
        doSyncModule(context, module_dict)
            
GIT_CMD_PATH = 'D:/Program Files/Git/bin/'
GIT_SSH_CMD = 'set GIT_SSH_COMMAND=ssh -i "D:/Key/id_rsa" -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no '
GIT_CHECKOUT_PATH = 'D:/Work/Yuyu/program/protocol/'

def do_test_git_update(context):
    proto_sync_path = context.proto_sync_path
    if not os.path.exists(proto_sync_path):
        return True

    export_git_foler = os.path.join(proto_sync_path, 'protocol/')
    if not os.path.exists(export_git_foler):
        cmd = 'cd "%s" && D: && %s && "%sgit" clone yyh@119.15.139.102:protocol.git' % (proto_sync_path, GIT_SSH_CMD, GIT_CMD_PATH)
        cmd_call(cmd)

    cmd = 'cd "%s" && D: && %s && "%sgit" fetch origin develop:temp' % (export_git_foler, GIT_SSH_CMD, GIT_CMD_PATH)
    ret = cmd_call(cmd)

    cmd = 'cd "%s" && D: && %s && "%sgit" diff temp' % (export_git_foler, GIT_SSH_CMD, GIT_CMD_PATH)
    ret = cmd_call(cmd)

    if len(ret[0]) > 0:
       return True

    return False

def do_pull_git(context):
    proto_sync_path = context.proto_sync_path
    
    if not os.path.exists(proto_sync_path):
        os.mkdir(proto_sync_path) 
    export_git_foler = os.path.join(proto_sync_path, 'protocol/')
    if not os.path.exists(export_git_foler):
        cmd = 'cd "%s" && D: && %s && "%sgit" clone yyh@119.15.139.102:protocol.git' % (proto_sync_path, GIT_SSH_CMD, GIT_CMD_PATH)
        cmd_call(cmd)
        
    cmd = 'cd "%s" && D: && %s && "%sgit" pull origin develop:master' % (export_git_foler, GIT_SSH_CMD, GIT_CMD_PATH)
    cmd_call(cmd)

def doDeleteAll(project):
    start_CPU = time.clock()

    enums = Enum.objects.all()
    typeids = []
    for enum in enums:
        typeids.append(enum.type.id)
    enums.delete()
    SegmentType.objects.filter(pk__in = typeids).delete()

    custometypes = CustomType.objects.all()
    typeids = []
    for customtype in custometypes:
        typeids.append(customtype.type.id)
    custometypes.delete()
    SegmentType.objects.filter(pk__in = typeids).delete()

    Protocal.objects.all().delete()
    Module.objects.all().delete()
    SegmentPackedOption.objects.all().delete()

    end_CPU = time.clock()
    print '\n+++++++++++++ delete all : ', end_CPU-start_CPU, '++++++++++++++'


def doSync(project):
    start_CPU = time.clock()
    context = cls_context()
    context.namespace = project.namespace
    context.cur_project = project
    context.proto_sync_path = GIT_CHECKOUT_PATH
    bin_path = os.path.dirname(__file__)
    context.bin_path = os.path.join(bin_path, 'export_bin/' )
    #step 1: git download server proto files
    #step 2: parse proto files get module{ add, del, update }
    #step 3: for add edit sql
    #step 4: for del edit sql
    #step 4: for update edit sql
    if do_test_git_update(context):
        do_pull_git(context)

        parse_proto_files(context)

        doDeleteAll(project)

        with open(proto_parse_plugin_outputpath+'/'+'parse.json','r') as load_f:
            proto_parse_dict = json.load(load_f);
            context.proto_parse_dict = proto_parse_dict;
            doSyncAll(context)
    

    end_CPU = time.clock()
    print '\n+++++++++++++ sync Total : ', end_CPU-start_CPU, '++++++++++++++'

def doForceSync(project):
    start_CPU = time.clock()
    context = cls_context()
    context.namespace = project.namespace
    context.cur_project = project
    context.proto_sync_path = GIT_CHECKOUT_PATH
    bin_path = os.path.dirname(__file__)
    context.bin_path = os.path.join(bin_path, 'export_bin/' )

    do_pull_git(context)

    parse_proto_files(context)

    doDeleteAll(project)

    with open(proto_parse_plugin_outputpath+'/'+'parse.json','r') as load_f:
        proto_parse_dict = json.load(load_f);
        context.proto_parse_dict = proto_parse_dict;
        doSyncAll(context)

    end_CPU = time.clock()
    print '\n+++++++++++++ sync Total : ', end_CPU-start_CPU, '++++++++++++++'

def testUpdate(project):
    context = cls_context()
    context.namespace = project.namespace
    context.cur_project = project
    context.proto_sync_path = GIT_CHECKOUT_PATH
    bin_path = os.path.dirname(__file__)
    context.bin_path = os.path.join(bin_path, 'export_bin/' )
    return do_test_git_update(context);
