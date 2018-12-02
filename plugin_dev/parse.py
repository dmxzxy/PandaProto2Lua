#!/usr/bin/env python
# -*- encoding:utf8 -*-

import sys
import time
import os.path as path

import json
import google.protobuf.compiler.plugin_pb2 as plugin_pb2
import google.protobuf.descriptor_pb2 as descriptor_pb2

FDP = descriptor_pb2.FieldDescriptorProto

if sys.platform == "win32":
    import msvcrt, os
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

class Project:
	def __init__(self):
		self.modulelist = []

	def getModule(self,package):
		for m in self.modulelist:
			if m['package'] == package:
				return m
		return None

class Module:
	def __init__(self):
		self.package = ''
		self.messagelist = []
		self.enumlist = []
		self.path = []

class Message:
	def __init__(self):
		self.name = ''
		self.fullname = ''
		self.fieldlist = []
		self.enumlist = []
		self.nestedtypelist = []
		self.path = []
		self.desc = ''

	def searchId(self, proto_file, module):
		for field in self.fieldlist:
			if field['name'] == 'id' and field['type'] == FDP.TYPE_ENUM:
				for enum in module['enumlist']:
					if '.'+enum['fullname'] == field['type_name']:
						for evalue in enum['valuelist']:
							if evalue['name'] == field['default_value']:
								return evalue['number']
				for enum in self.enumlist:
					if '.'+enum['fullname'] == field['type_name']:
						for evalue in enum['valuelist']:
							if evalue['name'] == field['default_value']:
								return evalue['number']
		return None

class Enum:
	def __init__(self):
		self.name = ''
		self.fullname = ''
		self.valuelist = []
		self.path = []
		self.desc = ''

class EnumValue:
	def __init__(self, enumvalue_desc):
		self.name = enumvalue_desc.name
		self.fullname = ''
		self.number = enumvalue_desc.number
		self.path = []
		self.desc = ''

class Field:
	def __init__(self, field_desc):
		self.name = field_desc.name
		self.fullname = ''
		self.number = field_desc.number
		self.label = field_desc.label
		self.type = field_desc.type
		self.path = []
		self.desc = ''
		if field_desc.HasField("default_value"):
			value = field_desc.default_value
			self.default_value = value
		if field_desc.HasField("type_name"):
			self.type_name = field_desc.type_name
		if field_desc.HasField("options"):
			if field_desc.options.HasField("packed"):
				self.packed = field_desc.options.packed

class File:
	pass


def get_path_comments(pfile, path):
	return pfile.all_comments[str(path)]

def export_message(pfile, msg, msg_desc):

	field_index=0
	for field_desc in msg_desc.field:
		field = Field(field_desc)
		field.fullname = msg.fullname + '.' + field.name
		for p in msg.path:
			field.path.append(p);
		field.path.append(2);
		field.path.append(field_index);
		field.desc = get_path_comments(pfile, field.path)
		msg.fieldlist.append(field.__dict__)
		field_index += 1
	sorted(msg.fieldlist, key=lambda d:d['number'])

	msg_index = 0
	for msg_nested_desc in msg_desc.nested_type:
		nested_msg = Message()
		nested_msg.name = msg_nested_desc.name
		nested_msg.fullname = msg.fullname + '.' + nested_msg.name
		for p in msg.path:
			nested_msg.path.append(p);
		nested_msg.path.append(3);
		nested_msg.path.append(msg_index);
		nested_msg.desc = get_path_comments(pfile, nested_msg.path)
		export_message(pfile, nested_msg, msg_nested_desc)
		msg.nestedtypelist.append(nested_msg.__dict__)
		msg_index += 1;

	enum_index = 0
	for msg_enum_desc in msg_desc.enum_type:
		enum = Enum()
		enum.name = msg_enum_desc.name
		enum.fullname = msg.fullname + '.' + enum.name
		for p in msg.path:
			enum.path.append(p);
		enum.path.append(4);
		enum.path.append(msg_index);
		enum.desc = get_path_comments(pfile, enum.path)
		enumvalue_index = 0
		for enumvalue_desc in msg_enum_desc.value:
			enumvalue = EnumValue(enumvalue_desc)
			enumvalue.fullname = enum.fullname + '.' + enumvalue.name
			for p in enum.path:
				enumvalue.path.append(p);
			enumvalue.path.append(2);
			enumvalue.path.append(enumvalue_index);
			enumvalue.desc = get_path_comments(pfile, enumvalue.path)
			enum.valuelist.append(enumvalue.__dict__)
			enumvalue_index += 1

		msg.enumlist.append(enum.__dict__)
		enum_index += 1;

from adapter_descriptor import AdapterPbDescriptor
class Context:
	pass

def main():
	fp = open("test.txt", 'rb')
	plugin_require_bin = fp.read()
	fp.close()

	code_gen_req = plugin_pb2.CodeGeneratorRequest()
	code_gen_req.ParseFromString(plugin_require_bin)

	context = Context()
	context.code_gen_req = code_gen_req
	adapter = AdapterPbDescriptor(context)
	adapter.translate()
	return

	proj = Project();

	start_msg_CPU = time.clock()
	content = '';	
	for proto_file in code_gen_req.proto_file:
		pfile = File()
		module = proj.getModule(proto_file.package);
		if module == None:
			newmodule = Module()
			newmodule.package = proto_file.package
			module = newmodule.__dict__
			proj.modulelist.append(module)

		all_comments = {}
		for location in proto_file.source_code_info.location:
			locationPathStr = str(location.path);
			comments = location.leading_comments+' '+location.trailing_comments
			comments = comments.strip().replace("\n", "")
			all_comments[locationPathStr] = comments
		pfile.all_comments = all_comments

		path = [2]
		module['path'] = path
		module['desc'] = get_path_comments(pfile, path)

		enum_index = 0
		for enum_desc in proto_file.enum_type:
			enum = Enum()
			enum.name = enum_desc.name
			enum.fullname = module['package'] + '.' + enum_desc.name
			enum.path = [5, enum_index]
			enum.desc = get_path_comments(pfile, enum.path)
			enumvalue_index = 0
			for enumvalue_desc in enum_desc.value:
				enumvalue = EnumValue(enumvalue_desc)
				enumvalue.fullname = enum.fullname + '.' + enumvalue.name
				for p in enum.path:
					enumvalue.path.append(p);
				enumvalue.path.append(2);
				enumvalue.path.append(enumvalue_index);
				enumvalue.desc = get_path_comments(pfile, enumvalue.path)
				enum.valuelist.append(enumvalue.__dict__)
				enumvalue_index += 1
			module['enumlist'].append(enum.__dict__)
			enum_index += 1;

		msg_index = 0
		for msg_desc in proto_file.message_type:
			msg = Message()	
			msg.name = msg_desc.name
			msg.fullname = module['package'] + '.' + msg_desc.name
			msg.path = [4, msg_index]
			msg.desc = get_path_comments(pfile, msg.path)
			export_message(pfile, msg, msg_desc)
			_id = msg.searchId(proto_file, module);
			if not _id == None:
				msg.id = _id
			module['messagelist'].append(msg.__dict__)
			msg_index += 1;


	content += '\n\n\n\n\n' 

	code_generated = plugin_pb2.CodeGeneratorResponse()

	file_desc = code_generated.file.add()
	file_desc.name = 'parse.json'
	file_desc.content = json.dumps(proj.__dict__, ensure_ascii = False, sort_keys=True, indent=4)

	file_desc = code_generated.file.add()
	file_desc.name = 'log1.txt'
	file_desc.content = content + str(code_gen_req)

	print(time.clock() - start_msg_CPU)

	# sys.stdout.write(code_generated.SerializeToString())			

import profile  
if __name__ == "__main__":
	# profile.run("main()")
	main()

