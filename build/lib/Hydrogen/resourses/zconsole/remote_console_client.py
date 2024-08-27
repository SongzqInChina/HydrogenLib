# only output window
from ... import znetwork
from ...znetwork import NetPackage, Request, Error, Answer, Info
from argparse import ArgumentParser


def main():
    server = znetwork.Server()

    argparser = ArgumentParser()
    argparser.add_argument("-p", "--port", help="port", type=int, default=8080)

    args = argparser.parse_args()

    server.bindport(args.port)
    server.start_server()

    while True:
        request: NetPackage | None = server.get_request()
        if request is not None:
            if Request.is_package(request): # 如果是一个请求
                header, data = request.get()



