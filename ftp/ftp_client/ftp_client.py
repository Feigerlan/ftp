import optparse
import json
import os
from socket import *


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
        self.mainPath = os.path.dirname(os.path.abspath(__file__))

    def verify_args(self,options,args):
        server = options.server
        port = options.port
        # username = options.username
        # password = options.password

        if int(port)>0 and int(port)<65535:
            return True

        else:
            exit("The port is in 0~65535")

    def make_connection(self):
        self.sock = socket()
        self.sock.connect((self.options.server,int(self.options.port)))

    def authenticate(self):
        if self.options.username is None or self.options.password is None:
            username = input("username:")
            password = input("password:")
            return self.get_auth_result(username,password)
        return self.get_auth_result(self.options.username,self.options.password)

    def get_auth_result(self,username,password):
        data = {
            "action" : "auth",
            "username" : username,
            "password" : password
        }

        self.sock.send(json.dumps(data).encode("utf8"))
        print(json.dumps(data).encode("utf8"))
        print("已发送")
        response = self.response()
        print("response:",response["status_msg"])

        if response["status_code"]==254:
            self.username = username
            return True


    def response(self):
        data = self.sock.recv(1024).decode("utf8")
        data = json.loads(data)
        return data

    def interactive(self):
        if self.authenticate():
            print("开始使用ftp...")
            cmd_info = input("[%s]"%self.username).strip() #输入目录
            cmd_list = cmd_info.split()

            if hasattr(self,cmd_list[0]):
                func=getattr(self,cmd_list[0])
                func(*cmd_list)

    def put(self,*cmd_list):
        #put 12.png images
        action,local_path,target_path = cmd_list
        local_path = os.path.join(self.mainPath,loca_path)
        file_name = os.path.basename(loca_path)
        file_size = os.stat(loca_path).st_size

        data={
            "action":"put",
            "file_name":file_name,
            "file_size":file_size,
            "target_path":target_path

        }

        self.sock.send(json.dumps(data).encode("utf8"))
        has_send = 0
        is_exist = self.sock.recv(1024).decode("utf8")
        if is_exist == "800":
            #文件不完整
            pass
        elif is_exist == "801":
            #文件完全存在
            return

        f = open(loca_path,"rb")
        while has_send < file_size:
            data = f.read(1024)
            self.sock.sendall(data)
            has_send+=len(data)

ch = ClientHandler()

ch.interactive()