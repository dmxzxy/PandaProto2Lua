# PandaProto2Lua
因为协议编辑器在进入这个项目之时没有和服务器有过沟通，进入项目时也不是立项期，所以想要把整套协议编辑器的方案投入使用，是非常困难的。

建立这套规范的时候服务器已经手写了一套proto并且不想使用这个协议编辑器（因为vim编辑proto的速度是比编辑器要快一些）。

好在服务器端有一套自己的规范来编写proto文件，故我开始思考通过服务器写好的proto文件来同步到协议编辑器里面，并有了这个工程！！

由于当时写的匆忙，解析成我们自己数据结构的同时就写入数据库了，导致这部分代码和协议编辑器绑定的非常紧密，在后来做jenkins打包的时候就发现，如果想单独从proto文件直接导出成lua文件是个比较艰辛的过程，需要抽离很多东西，而且不能跨平台使用（目前只有windows支持）。那么现在我要开一个项目离开协议编辑器，专门处理这个问题（因为协议编辑器本身是跨平台的，但由于这部分的影响让协议编辑器失去了这个特性）。

用python2.7来做为开发基础
