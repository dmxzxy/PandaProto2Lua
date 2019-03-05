
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

ProtocolTypeName = {
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

def get_is_basic_type(type):
    if type == ProtocolType.TYPE_MESSAGE:
        return False

    if type == ProtocolType.TYPE_ENUM:
        return False

    if type == ProtocolType.TYPE_GROUP:
        return False

    return True


def get_type_name(id, typename):
    if id == ProtocolType.TYPE_MESSAGE:
        return typename[1:]
    
    if id == ProtocolType.TYPE_ENUM:
        return typename[1:]
        
    if type == ProtocolType.TYPE_GROUP:
        return typename[1:]

    return ProtocolTypeName[id]