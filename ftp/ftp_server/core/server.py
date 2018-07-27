import socketserver
import json
import configparser
import os
from conf import settings

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

class ServerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print("ftpserver is ok")
        while True:
            data = self.request.recv(1024).strip()
            data = json.loads(data.decode("utf8"))
            """
            data = {
            "action":"auth",
            "username": username,
            "password": password
                }
            """
            if data.get("action"):
                if hasattr(self,data.get("action")):
                    func=getattr(self,data.get("action"))
                    func(**data)
            else:
                print(data)
    def auth(self,**data):
        username = data["username"]
        password = data["password"]

        user = self.authenticate(username,password)

        if user:
            self.send_reponse(254)
        else:
            self.send_reponse(253)

    def authenticate(self,username,password):
        cfg = configparser.ConfigParser()
        cfg.read(settings.ACCOUNT_PATH)

        if username in cfg.sections():
            if cfg[username]["password"] == password:
                print('登录成功')
                self.username = username
                return username

    def send_reponse(self,status_code):
        response={"status_code":status_code,
                  "status_msg":STATUS_CODE[status_code]}
        self.request.sendall(json.dumps(response).encode("utf8"))

    def put(self,**data):
        print("data",data)
        file_name = data.get("file_name")
        file_size = data.get("file_size")
        target_path = data.get("target_path")

        abs_path = os.path.join(self.mainPath,target_path,file_name)

        has_received = 0
        #判断文件名是否存在
        if os.path.exists(abs_path):
            file_has_size = os.stat(abs_path).st_size
            if file_has_size < file_size:
                #断点续传
                self.request.sendall("800".encode("utf8"))
            else:
                #文件已完全存在
                self.request.sendall("801".encode("utf8"))
                return
        else:
            self.request.sendall("802".encode("utf8"))
            f = open(abs_path,"wb")

        while has_received<file_size:
            data = self.request.recv(1024)
            f.write(data)
            has_received+=len(data)
        f.close()

    def get(self,**data):
        pass