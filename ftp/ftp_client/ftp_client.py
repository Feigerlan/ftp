import optparse
import json
import os,sys
from socket import *
#定义一个客户端类
class ClientHandler():
    def __init__(self):
        # 参数识别，生成字典对象
        self.op = optparse.OptionParser()
        self.op.add_option("-s","--server",dest="server")
        self.op.add_option("-P","--port",dest="port")
        self.op.add_option("-u","--username",dest="username")
        self.op.add_option("-p","--password",dest="password")

        self.options,self.args = self.op.parse_args()  # option为 字典对象,args为不参数形成的列表
        print(self.options)
        self.verify_args(self.options, self.args)

        self.make_connection()
        #dirname取文件所在目录，abspath为文件绝对路径
        self.mainPath = os.path.dirname(os.path.abspath(__file__))

    #serverip和port的参数验证方法
    def verify_args(self,options,args):
        server = options.server
        port = options.port
        # username = options.username
        # password = options.password

        if int(port)>0 and int(port)<65535:
            return True

        else:
            exit("The port is in 0~65535")
    #连接到服务器，连接方法
    def make_connection(self):
        self.sock = socket()
        self.sock.connect((self.options.server,int(self.options.port)))
    #用户名密码检测
    def authenticate(self):
        #如果用户名，密码为空，则提示输入用户名和密码，并把接收到的用户名密码返回给验证方法
        if self.options.username is None or self.options.password is None:
            username = input("username:")
            password = input("password:")
            return self.get_auth_result(username,password)
        return self.get_auth_result(self.options.username,self.options.password)

    #用户名密码验证
    def get_auth_result(self,username,password):
        #将用户名密码封装成字典
        data = {
            "action" : "auth",
            "username" : username,
            "password" : password
        }
        #将字典转换为json格式并编码为utf8发送出去
        self.sock.send(json.dumps(data).encode("utf8"))
        print(json.dumps(data).encode("utf8"))
        print("已发送")
        #接收服务端消息
        response = self.response()
        #打印出接收到的服务端消息
        print("response:",response["status_msg"])
        #如果服务端响应的消息代码是254，则返回真
        if response["status_code"]==254:
            self.username = username
            return True

    #接收服务端的响应
    def response(self):
        #从缓冲区接收1024字节并utf8解码，赋值给data
        data = self.sock.recv(1024).decode("utf8")
        #把接收到的数据json解为字典结构
        data = json.loads(data)
        #返回字典
        return data

    #验证通过后操作
    def interactive(self):
        #如果用户名密码验证结果为真
        if self.authenticate():
            print("开始使用ftp...")
            #接收命令信息
            while 1:
                cmd_info = input("[%s]"%self.username).strip()
                #把接收到的命令做分割为一个命令元组，默认以空格为分隔符
                cmd_list = cmd_info.split()
                #反射检测客户端类中是否有命令所对应的方法，如果有，则调用
                if hasattr(self,cmd_list[0]):
                    func=getattr(self,cmd_list[0])
                    func(*cmd_list)
                else:
                    print("无效命令")

    #put命令对应的方法
    def put(self,*cmd_list):
        #假设 put 12.png images
        #获取命令元组中的，命令、本地文件名、目标目录名，并赋值给相应变量
        action,local_path,target_path = cmd_list
        #将本地文件名和目录做拼接形成，绝对路径名
        local_path = os.path.join(self.mainPath,local_path)
        #os.path.basename(path) 返回path最后的文件名。如何path以／或\结尾，那么就会返回空值。即os.path.split(path)的第二个元素。
        file_name = os.path.basename(local_path)
        #获取文件大小
        file_size = os.stat(local_path).st_size
        #封装字典
        data={
            "action":"put",
            "file_name":file_name,
            "file_size":file_size,
            "target_path":target_path

        }
        #将字典转换为json格式并编码为utf8发送出去
        self.sock.send(json.dumps(data).encode("utf8"))

        has_sent = 0
        #接收服务端文件状态码
        file_status = self.sock.recv(1024).decode("utf8")

        #判断服务端文件存在状态码
        if file_status == "800":
            #文件不完整，是否续伟
            choice = input("文件已经存在，是否续传(Y/N)：").strip()
            #续传
            if choice.upper()=="Y":

                self.sock.sendall("Y".encode("utf8"))
                #获取服务端传过来的，文件续传的位置
                continue_position = self.sock.recv(1024).decode("utf8")
                #已发送 = 已发送 + 续传位置
                has_sent+=int(continue_position)
            #不续传
            else:
                self.sock.sendall("N".encode("utf8"))
        elif file_status == "801":
            #文件完全存在直接返回
            print("文件已存在")
            return
        #打开一个文件句柄
        f = open(local_path,"rb")
        #查找到已发送的位置
        f.seek(has_sent)
        #如果已发送的文件大小小于文件大小，循环发送
        while has_sent < file_size:
            #以1024为单位读取文件并赋值给data变量
            data = f.read(1024)
            #把读取的数据发送给服务端
            self.sock.sendall(data)
            #已发送的大小 = 已发送大小 + 本次发送大小
            has_sent+=len(data)
            #进度条
            self.show_progress(has_sent,file_size)

        #关闭文件句柄
        f.close()
        print("发送完成")

    #进度条方法
    def show_progress(self,has,total):
        #传输百分比
        rate = float(has)/float(total)
        #转化为整数
        rate_number = int(rate*100)

        # if self.last != rate_number:
        sys.stdout.write("%s%% %s\r"%(rate_number,"#"*rate_number))
        #
        # self.last = rate_number

    def ls(self,*cmd_list):
        data = {
            "action" : "ls",
        }
        self.sock.sendall(json.dumps(data).encode("utf8"))

        data = self.sock.recv(1024).decode("utf8")

        print(data)

    def cd(self,*cmd_list):
        data = {
             "action" : "cd",
             "dirname" : cmd_list[1]
         }

        self.sock.sendall(json.dumps(data).encode("utf8"))

        data = self.sock.recv(1024).decode("utf8")
        print(os.path.basename(data))


#实例化一个客户端连接
ch = ClientHandler()

#执行实例中的激活操作
ch.interactive()