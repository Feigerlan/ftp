import socketserver
from conf import settings
import optparse #参数拼接
from core import server

#定义一个接收参数类
class ArgvHandler():
    print('调用成功')
    def __init__(self):
        #参数识别，生成字典对象
        self.op = optparse.OptionParser()
        # self.op.add_option("-s","--server",dest='server')
        # self.op.add_option("-P","--port",dest="port")
        options,args=self.op.parse_args() #option为字典对象,args为非常规参数形成的列表
        self.verify_args(options,args)

    #验证参数方法
    def verify_args(self,options,args):

        cmd = args[0]
        #反射判断是否有参数中对应 的方法 ，有则调用 执行
        if hasattr(self,cmd):
            func = getattr(self,cmd)
            func()
    #定义方法
    def start(self):
        print("服务启动中..")
        #从设置中读取ip，port，并实例化一个tcp服务线程
        s = socketserver.ThreadingTCPServer((settings.IP,settings.PORT),server.ServerHandler)
        print("正在监听IP端口：%s:%d" %(settings.IP,settings.PORT))
        s.serve_forever()
    def help(self):
        pass

    def status(self):
        pass