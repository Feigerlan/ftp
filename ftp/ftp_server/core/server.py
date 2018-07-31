import socketserver
import json
import configparser
import os
from conf import settings

#定义一系列状态码
STATUS_CODE  = {
    250 : "Invalid cmd format, e.g: {'action':'get','filename':'test.py','size':344}",
    251 : "Invalid cmd ",
    252 : "Invalid auth data",
    253 : "Wrong username or password",
    254 : "Passed authentication",
    255 : "Filename doesn't provided",
    256 : "File doesn't exist on server",
    257 : "ready to send file",
    258 : "md5 verification",

    800 : "the file exist,but not enough ,is continue? ",
    801 : "the file exist !",
    802 : " ready to receive datas",
    900 : "md5 valdate success"

}

#定义一个服务端类
class ServerHandler(socketserver.BaseRequestHandler):
    #定义handle循环接收客户端消息
    def handle(self):
        print("ftpserver is ok")
        while True:
            #接收客户端消息并json转换为字典
            data = self.request.recv(1024).strip()
            data = json.loads(data.decode("utf8"))
            """
            data = {
            "action":"auth",
            "username": username,
            "password": password
                }
            """
            #获取字典中的action字典，反射查找是否有对应功能，有则调用方法
            if data.get("action"):
                if hasattr(self,data.get("action")):
                    func=getattr(self,data.get("action"))
                    func(**data)
            else:
                print(data)
    #验证方法
    def auth(self,**data):
        username = data["username"]
        password = data["password"]
        #调用验证方法
        is_passed = self.authenticate(username,password)
        #如果验证通过，用户名有值被返回
        if is_passed:
            self.send_reponse(254)
            self.mainPath = os.path.join(settings.BASE_DIR,"home",self.username)
        #如果验证不通过
        else:
            self.send_reponse(253)

    #验证核心
    def authenticate(self,username,password):
        #实例一个configparser，配置文件模块
        cfg = configparser.ConfigParser()
        #读取配置文件
        cfg.read(settings.ACCOUNT_PATH)
        #如果用户名在配置文件中
        if username in cfg.sections():
            #如果密码匹配返回用户名
            if cfg[username]["password"] == password:
                print('登录成功')
                self.username = username
                return username
    #状态码-消息响应模块，传入状态码响应状态消息
    def send_reponse(self,status_code):
        response={"status_code":status_code,
                  "status_msg":STATUS_CODE[status_code]}
        #发送状态码及状态消息
        self.request.sendall(json.dumps(response).encode("utf8"))

    #put模块，接收客户端传来的data字典数据
    def put(self,**data):
        print("data",data)
        #获取put的文件的名字，大小，目标路径
        file_name = data.get("file_name")
        file_size = data.get("file_size")
        target_path = data.get("target_path")
        #服务端绝对路径,主路径+目标文件夹+目标文件名

        abs_path = os.path.join(self.mainPath,target_path,file_name)

        has_received = 0
        #判断文件是否存在，如果存在
        if os.path.exists(abs_path):
            #取文件大小
            file_has_size = os.stat(abs_path).st_size
            #如果文件大小小于文件实际大小
            if file_has_size < file_size:
                #断点续传，告诉客户端文件存在但是不完整
                self.request.sendall("800".encode("utf8"))
                #接收客户端的选择，Y或者N
                choice = self.request.recv(1024).decode("utf8")
                #如果选择续传
                if choice == "Y":#续传
                    #告诉客户端现有文件大小
                    self.request.sendall(str(file_has_size).encode("utf8"))
                    #已接收大小 = 已接收大小 + 现有文件大小
                    has_received+=file_has_size

                    f = open(abs_path,"ab")#追加内容
                #如果选择不续传
                else:#不续传
                    f = open(abs_path,"wb")
            else:
                #文件已完全存在
                self.request.sendall("801".encode("utf8"))
                return
        #文件不存在，直接写
        else:
            #告诉客户端，可以接收数据。
            self.request.sendall("802".encode("utf8"))
            f = open(abs_path,"wb")
        #当已接收数据小于文件大小时，文件循环写入
        while has_received<file_size:
            try:
                data = self.request.recv(1024)
            except Exception as e:
                break
            #
            f.write(data)
            has_received+=len(data)
        f.close()

    def ls(self):
        pass

    def get(self,**data):
        pass