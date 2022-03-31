import multiprocessing
import re
import socket
import sys


class WSGIServer(object):
    def __init__(self, port: int, app, static_path):
        # 1.创建监听套接字
        self.file_name = None
        self.header = None
        self.status = None
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 2.为了服务端先断开时，客户端马上能链接
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 3.绑定本地端口
        self.server_socket.bind(("", port))
        # 4.监听
        self.server_socket.listen(128)

        self.port = port
        self.application = app
        self.static_path = static_path

    def deal_with_static(self, new_socket):
        # 如果不是以.py结尾的文件，当成静态页面处理
        try:
            f = open("static" + self.file_name, "rb")
        except OSError:
            header = "HTTP/1.1 404 NOT FOUND FILE\r\n"
            header += "\r\n"
            body = r"<h1>not found file <\h1>"
            response = header + body
            new_socket.send(response.encode("utf-8"))
        else:
            header = "HTTP/1.1 200 OK\r\n"
            header += "\r\n"
            body = f.read()
            response = header.encode("utf-8") + body
            new_socket.send(response)

    def deal_with_dynamic(self, new_socket):
        """处理动态页面"""

        env = dict()
        env["PATH_INFO"] = self.file_name

        # web框架的接口函数
        body = self.application(env, self.set_response_header)

        # header部分的拼接成指定格式
        header = "HTTP/1.1 %s" % self.status

        for temp in self.header:
            header += "%s:%s\r\n" % (temp[0], temp[1])
        header += "\r\n"
        print(header)

        new_socket.send(header.encode("utf-8"))
        new_socket.send(body.encode("utf-8"))

    def set_response_header(self, status, header):
        """作为接口函数的参数，相当于容器接收web框架返回的头部信息"""

        self.status = status
        self.header = header

    def serve_client(self, new_socket):
        """接收请求消息和发送相应消息"""
        # 1.接受请求消息 GET / HTTP/1.1
        request = new_socket.recv(1024).decode("utf-8")

        # 2.解析请求消息
        request_lines = request.splitlines()
        ret = re.match(r"[^/]+(/[^ ]*)", request_lines[0])
        if ret:
            self.file_name = ret.group(1)
            if self.file_name == "/":
                self.file_name = "/index.html"
        # print(file_name)

        # 3.尝试打开文件，若文件存在则能打开，否则发送404
        if not self.file_name.endswith(".py"):
            # 处理静态网页
            self.deal_with_static(new_socket)

            # new_socket.close()
        else:
            # 处理动态网页
            self.deal_with_dynamic(new_socket)

        new_socket.close()

    def run_forever(self):
        """当成主函数"""
        while True:
            new_socket, client_address = self.server_socket.accept()
            p = multiprocessing.Process(target=self.serve_client, args=(new_socket,))
            p.start()
            p.join()

            new_socket.close()
        self.server_socket.close()


def main():
    # 运行服务器时，给出指定的 端口和运行的框架
    if len(sys.argv) < 3:
        print("请输入端口和框架")
        return
    try:
        port = int(sys.argv[1])  # 6968
        frame_app_name = sys.argv[2]  # mini_frame:application
    except ValueError:
        print("输入方式有误，请按照以下方式运行：")
        print("python3 web_server.py 6968 mini_frame:application")
        return
    ret = re.match(r"([^:]+):(.*)", frame_app_name)

    # 获取框架文件名
    if ret:
        frame_name = ret.group(1)
        app_name = ret.group(2)
    else:
        print("您的输入方式有误，请按照上述方式运行")
        return

    with open("./web_server.conf", "r") as f:
        conf_info = eval(f.read())  # 将字符串转为字典类型

    # 将导入动态数据的模块添加到python解释器的环境变量中
    sys.path.append(conf_info["dynamic_path"])
    print(sys.path)

    frame = __import__(frame_name)  # 导入指定的模块
    app = getattr(frame, app_name)  # 反射出该模块下的指定的函数app_name

    wsgi_server = WSGIServer(port, app, conf_info["static_path"])
    wsgi_server.run_forever()


if __name__ == '__main__':
    main()
