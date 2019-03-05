
def isSameType(t1, t2):
	return t1.__name__ == t2.__name__

def get_object(t, **kw):
	database = ProjectDatabase()
	if isSameType(t, Module):
		for module in database.allModules:
			isFind = True
			for k, v in kw.items():
				if getattr(module, k) != v:
					isFind = False
			if isFind:
				return module
	elif isSameType(t, Enum):
		for enum in database.allEnums:
			isFind = True
			for k, v in kw.items():
				if getattr(enum, k) != v:
					isFind = False
			if isFind:
				return enum
	elif isSameType(t, Protocol):
		for protocol in database.allProtocols:
			isFind = True
			for k, v in kw.items():
				if getattr(protocol, k) != v:
					isFind = False
			if isFind:
				return protocol
	elif isSameType(t, Message):
		for msg in database.allMessages:
			isFind = True
			for k, v in kw.items():
				if getattr(msg, k) != v:
					isFind = False
			if isFind:
				return msg
	elif isSameType(t, Comment):
		if kw['pk'] in database.allComments:
			return database.allComments[kw['pk']]
		return None

	return None

def add_object(object):
	database = ProjectDatabase()
	if isinstance(object, Module):
		# print("---> create module: %s"%object.fullname)
		database.allModules.append(object)
		return len(database.allModules) - 1
	elif isinstance(object, Enum):
		# print("---> create enum: %s"%object.fullname)
		database.allEnums.append(object)
		return len(database.allEnums) - 1
	elif isinstance(object, Message):
		# print("---> create message: %s"%object.fullname)
		database.allMessages.append(object)
		return len(database.allMessages) - 1
	elif isinstance(object, Protocol):
		# print("---> create protocol: %s"%object.fullname)
		database.allProtocols.append(object)
		return len(database.allProtocols) - 1
	elif isinstance(object, Comment):
		if object.content and len(object.content) > 0:
			# print("---> create comment: %s %s"%(object.path,object.content))
			database.allComments[object.path] = object
		return object.path
	return -1

class BaseData(object):
	pk = -1
	def __init__(self, **kw):
		for k, v in kw.items():
			setattr(self, k, v)

	def save(self, data = None):
		if data == None:
			self.pk = add_object(self)
		else:
			self.pk = data.recive(self)
	
	def recive(self, data):
		return -1

class ProjectDatabase(object):
	allModules = []
	allEnums = []
	allMessages = []
	allProtocols = []
	allComments = {}

class Comment(BaseData):
	path = ""
	content = ""

class Project(BaseData):
	namespace = ""
	modules = None
	database = ProjectDatabase()

	def __init__(self, **kw):
		self.__module_reflist = []
		super(Project, self).__init__(**kw)

	def recive(self, data):
		if isinstance(data, Module):
			ref_id = add_object(data)
			self.__module_reflist.append(ref_id)
			return ref_id
		return -1
			
	def __getattribute__(self, key):
		if key == "modules":
			modules = []
			for	i in range(0, len(self.__module_reflist)):
				ref_id = self.__module_reflist[i]
				modules.append(get_object(Module, pk = ref_id))
			return modules
		return super(Project, self).__getattribute__(key)


class Module(BaseData):
	name = ""
	fullname = ""
	namespace = ""
	comment = None
	protocols = None
	messages = None
	enums = None
	localtion = None

	def __init__(self, **kw):
		self.__protocol_reflist = []
		self.__message_reflist = []
		self.__enum_reflist = []
		super(Module, self).__init__(**kw)
		
	def recive(self, data):
		if isinstance(data, Enum):
			ref_id = add_object(data)
			self.__enum_reflist.append(ref_id)
			return ref_id
		elif isinstance(data, Message):
			ref_id = add_object(data)
			self.__message_reflist.append(ref_id)
			return ref_id
		elif isinstance(data, Protocol):
			ref_id = add_object(data)
			self.__protocol_reflist.append(ref_id)
			return ref_id
		return -1

	def __getattribute__(self, key):
		if key == "protocols":
			objects = []
			for	i in range(0, len(self.__protocol_reflist)):
				ref_id = self.__protocol_reflist[i]
				objects.append(get_object(Protocol, pk = ref_id))
			return objects
		elif key == "messages":
			objects = []
			for	i in range(0, len(self.__message_reflist)):
				ref_id = self.__message_reflist[i]
				objects.append(get_object(Message, pk = ref_id))
			return objects
		elif key == "enums":
			objects = []
			for	i in range(0, len(self.__enum_reflist)):
				ref_id = self.__enum_reflist[i]
				objects.append(get_object(Enum, pk = ref_id))
			return objects
		elif key == "comment":
			obj = get_object(Comment, pk = str(self.localtion))
			if obj:
				return obj.content
			return ''
		return super(Module, self).__getattribute__(key)

class EnumValue(BaseData):
	name = ""
	fullname = ""
	namespace = ""
	comment = None
	number = 0
	localtion = None
	def __getattribute__(self, key):
		if key == "comment":
			obj = get_object(Comment, pk = str(self.localtion))
			if obj:
				return obj.content
			return ''
		return super(EnumValue, self).__getattribute__(key)

class Enum(BaseData):
	name = ""
	fullname = ""
	namespace = ""
	comment = None
	values = None
	localtion = None

	def __init__(self, **kw):
		self.values = []
		super(Enum, self).__init__(**kw)
		
	def recive(self, data):
		if isinstance(data, EnumValue):
			self.values.append(data)

	def __getattribute__(self, key):
		if key == "comment":
			obj = get_object(Comment, pk = str(self.localtion))
			if obj:
				return obj.content
			return ''
		return super(Enum, self).__getattribute__(key)

class MessageField(BaseData):
	name = ""
	fullname = ""
	namespace = ""
	comment = None
	labelType = 1
	protoType = 0
	protoTypeName = "" #only proto_type == enum message
	number = 0
	default_value = 0
	packed = False
	localtion = None

	def __getattribute__(self, key):
		if key == "comment":
			obj = get_object(Comment, pk = str(self.localtion))
			if obj:
				return obj.content
			return ''
		return super(MessageField, self).__getattribute__(key)

class Message(BaseData):
	name = ""
	fullname = ""
	namespace = ""
	fields = None
	comment = None
	nested_messages = None
	nested_enums = None
	localtion = None

	def __init__(self, **kw):
		self.fields = []
		self.__nested_messages_reflist = []
		self.__nested_enums_reflist = []
		super(Message, self).__init__(**kw)
		
	def recive(self, data):
		if isinstance(data, Message):
			ref_id = add_object(data)
			self.__nested_messages_reflist.append(ref_id)
			return ref_id
		elif isinstance(data, Enum):
			ref_id = add_object(data)
			self.__nested_enums_reflist.append(ref_id)
			return ref_id
		elif isinstance(data, MessageField):
			self.fields.append(data)
		return -1

	def __getattribute__(self, key):
		if key == "nested_messages":
			objects = []
			for	i in range(0, len(self.__nested_messages_reflist)):
				ref_id = self.__nested_messages_reflist[i]
				objects.append(get_object(Message, pk = ref_id))
			return objects
		elif key == "nested_enums":
			objects = []
			for	i in range(0, len(self.__nested_enums_reflist)):
				ref_id = self.__nested_enums_reflist[i]
				objects.append(get_object(Enum, pk = ref_id))
			return objects
		elif key == "comment":
			obj = get_object(Comment, pk = str(self.localtion))
			if obj:
				return obj.content
			return ''

		return super(Message, self).__getattribute__(key)

class Protocol(Message):
	id = 0
