# translate descriptor to models
# the descriptor input in many different ways 

from models import *

def getProjectModuleNotNone(pProject, namespace):
    for module in pProject.modules:
        if module.namespace == namespace:
            return module
    
    #not found, add it
    module = Module()
    module.namespace = namespace
    pProject.modules.append(module)

class AdapterPbDescriptor:
    context = None
    def __init__(self, context):
        self.context = context

    def parse_namespace(self):
        code_gen_req = self.context.code_gen_req
        project_namespace = ""
        if not hasattr(self.context, "namespace"):
            for proto_file in code_gen_req.proto_file:
                project_namespace = proto_file.package
                index = project_namespace.rfind('.')
                if index != -1:
                    project_namespace = project_namespace[0:index]
                break
        else:
            project_namespace = self.context.namespace
        return project_namespace

    
    def translate(self):
        code_gen_req = self.context.code_gen_req
        project_namespace = self.parse_namespace()

        pProject = Project()
        pProject.namespace = project_namespace

        for proto_file in code_gen_req.proto_file:
            module = getProjectModuleNotNone(pProject, proto_file.package)
            print(proto_file.package)

        return pProject
    
