cd E:\\workspace\\PandaProto2Lua\\plugin_dev
E:
%~dp0bin/protoc.exe -I=%~dp0/protocol --outbin_out=%~dp0/plugin_dev --plugin=protoc-gen-outbin=%~dp0/plugin/runoutbin.bat %~dp0/protocol/module_global.proto %~dp0/protocol/module1.proto %~dp0/protocol/module1_1.proto %~dp0/protocol/module2.proto

pause