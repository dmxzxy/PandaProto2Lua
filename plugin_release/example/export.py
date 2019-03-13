
import os

import sys
sys.path.append('../')

from panpbtool import panpbtool
from data_adapter import ProtoFileInputAdapter

class Context():
    pass

def main():
    context = Context()
    print(context)
    adapter = ProtoFileInputAdapter(context)
    project = adapter.translate()
    panpbtool.write(os.path.dirname(os.path.realpath(__file__)) + "/export", project)

if __name__ == "__main__":
	main()