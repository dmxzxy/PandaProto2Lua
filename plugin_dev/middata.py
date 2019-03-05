
# required string name
# required string namespace
# required string fullname 
# required string location
class BaseData(object):
    name = None
    fullname = None
    namespace = None
    location = None

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    def __repr__(self):
        return '<{0} {1} {2} {3}>'.format(self.name, self.fullname, self.namespace, self.location)

# required int number
class EnumValue(BaseData):
    number = None

    def __repr__(self):
        str = '<{0} {1}>'.format(self.__class__.__name__, self.number)
        return str + super(EnumValue, self).__repr__() 

# repeated EnumValue values
class Enum(BaseData):
    values = None

    def __init__(self, **kw):
        self.values = []
        super(Enum, self).__init__(**kw)

    def add_enumvalue(self, **kw):
        enumvalue = EnumValue(**kw)
        self.values.append(enumvalue)
        return enumvalue

class ProtocolType():
    id = None
    name = None
    is_basic = True

    def __init__(self, id, name, is_basic):
        self.id = id
        self.name = name
        self.is_basic = is_basic

# required int label
# required int proto_type
# required int number
class MessageField(BaseData):
    label = None
    proto_type = None
    number = None

# repeated MessageField fields
# repeated Message nested_messages 
# repeated Enum nested_enums
class Message(BaseData):
    fields = None
    nested_messages = None
    nested_enums = None

    def __init__(self, **kw):
        self.fields = []
        self.nested_enums = []
        self.nested_messages = []
        super(Message, self).__init__(**kw)

    def add_field(self, **kw):
        field = MessageField(**kw)
        self.fields.append(field)
        return field

    def add_message(self, **kw):
        msg = Message(**kw)
        self.nested_messages.append(msg)
        return msg

    def add_enum(self, **kw):
        enum = Enum(**kw)
        self.nested_enums.append(enum)
        return enum

# required int id
class Protocol(Message):
    id = None
    category = None
    
# repeated Message messages 
# repeated Enum enums 
# repeated Protocol protocols
class Module(BaseData):
    messages = None
    enums = None
    protocols = None

    def __init__(self, **kw):
        self.messages = []
        self.enums = []
        self.protocols = []
        super(Module, self).__init__(**kw)

    def add_message(self, **kw):
        msg = Message(**kw)
        self.messages.append(msg)
        return msg
    
    def add_enum(self, **kw):
        enum = Enum(**kw)
        self.enums.append(enum)
        return enum
    
    def add_protocol(self, **kw):
        enum = Protocol(**kw)
        self.protocols.append(enum)
        return enum

# required string path
# required string content
class Comment():
    path = None
    content = None
    def __init__(self, path, content):
        self.path = path
        self.content = content
    
    def __repr__(self):
        str = '<{0} {1}:{2}>'.format(self.__class__.__name__, self.path, self.content)
        return str

# repeated Module modules  
# repeated Comment comments
class Project():
    modules = None
    comments = None

    def __init__(self):
        self.modules = []
        self.comments = {}

    def add_module(self, **kw):
        module = Module(**kw)
        self.modules.append(module)
        return module

    def add_comment(self, path, content):
        comment = Comment(path, content)
        self.comments[path] = comment
        return comment

    def get_module(self, **kw):
        for module in self.modules:
            isFind = True
            for k, v in kw.items():
                if getattr(module, k) != v:
                    isFind = False
            if isFind:
                return module
        return None

    def get_comment(self, location):
        location = str(location)
        if location not in self.comments:
            return ""

        comment = self.comments[location]
        if comment == None:
            return ""
        return comment.content