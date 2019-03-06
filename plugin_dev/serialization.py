#!/usr/bin/env python
# -*- encoding:utf8 -*-

import json
import collections
import middata

class JsonClassSerializable(json.JSONEncoder):

    REGISTERED_CLASS = {}

    def register(ctype):
        JsonClassSerializable.REGISTERED_CLASS[ctype.__name__] = ctype

    def default(self, obj):
        if isinstance(obj, collections.Set):
            return dict(_set_object=list(obj))
        if isinstance(obj, JsonClassSerializable):
            jclass = {}
            jclass["name"] = type(obj).__name__
            jclass["dict"] = obj.__dict__
            return dict(_class_object=jclass)
        else:
            return json.JSONEncoder.default(self, obj)

    def json_to_class(self, dct):
        if '_set_object' in dct:
            return set(dct['_set_object'])
        elif '_class_object' in dct:
            cclass = dct['_class_object']
            cclass_name = cclass["name"]
            if cclass_name not in self.REGISTERED_CLASS:
                raise RuntimeError(
                    "Class {} not registered in JSON Parser"
                    .format(cclass["name"])
                )
            instance = self.REGISTERED_CLASS[cclass_name]()
            instance.__dict__ = cclass["dict"]
            return instance
        return dct

    def encode_(self, file):
        with open(file, 'w') as outfile:
            json.dump(
                self.__dict__, outfile,
                cls=JsonClassSerializable,
                indent=4,
                sort_keys=True
            )

    def decode_(self, file):
        try:
            with open(file, 'r') as infile:
                self.__dict__ = json.load(
                    infile,
                    object_hook=self.json_to_class
                )
        except FileNotFoundError:
            print("Persistence load failed "
                  "'{}' do not exists".format(file)
                  )


JsonClassSerializable.register(middata.Project)

def __serialize(obj):
    return obj.__dict__

# return an json string
def DoSerializing(project):
    # content = json.dumps(project, ensure_ascii=False, default=__serialize)
    
    # file_content = open("serializing",'w')
    # file_content.write(content.encode("utf8"))
    project.encode_("serializing")
    # return content


def DoDeserializing():
    # file_content = open("serializing", "r")

    # data = json.load(file_content)
    
    # instance = object.__new__(middata.Project)

    # for key, value in data.items():
    #     setattr(instance, key, value)
    
    # return instance
    project = middata.Project()
    project.decode_("serializing")
    return project

