import socketserver
from conf import settings
import optparse #参数拼接
from core import server

class ArgvHandler():
    print('调用成功')
    def __init__(self):
        #参数识别，生成字典对象
        self.op = optparse.OptionParser()
        # self.op.add_option("-s","--server",dest='server')
        # self.op.add_option("-P","--port",dest="port")

        options,args=self.op.parse_args() #option为 字典对象,args为不参数形成的列表

        self.verify_args(options,args)

    def verify_args(self,options,args):
        cmd = args[0]

        if hasattr(self,cmd):
            func = getattr(self,cmd)
            func()

    def start(self):
        print("服务已经启动..")
        s = socketserver.ThreadingTCPServer((settings.IP,settings.PORT),server.ServerHandler)
        print("正在监听IP端口：%s:%d" %(settings.IP,settings.PORT))
        s.serve_forever()
    def help(self):
        pass

    def status(self):
        pass