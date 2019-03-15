#!/usr/bin/env python
# -*- encoding:utf8 -*-

import os
import core.writelua as writelua
import core.writeproto as writeproto
import core.readproto as readproto

class Context:
    project = None
    write_path = None

def checkdirector__(context):
    if not os.path.exists(context.write_path):
        os.mkdir(context.write_path)

def write(path, project):
    context = Context()
    context.write_path = path
    context.project = project
    
    checkdirector__(context)

    writeproto.do_export(context)
    writelua.do_export(context)

def read(path, rule):
    context = Context()
    context.write_path = path
    context.project = None
    context.adapter = None
    context.rule = rule
    readproto.do_read(context)
    return context.project