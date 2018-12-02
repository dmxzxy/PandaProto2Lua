

class Project:
	namespace = ""
	modules = []

class Module:
	name = ""
	namespace = ""
	comments = ""
	protocols = []
	messages = []
	enums = []

class EnumValue:
	name = ""
	namespace = ""
	comments = ""
	number = 0

class Enum:
	name = ""
	namespace = ""
	values = []

class MessageField:
	name = ""
	namespace = ""
	comments = ""
	proto_type = 0
	proto_type_name = "" #only proto_type == enum message
	number = 0
	default_value = 0
	packed = False

class Message:
	name = ""
	namespace = ""
	comments = ""
	fields = []
	nested_messages = []
	nested_enums = []

class Protocol(Message):
	id = 0
