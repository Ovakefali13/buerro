from controller import ControllerFromArgs
from chatbot import Chatbot, BuerroBot
from http.server import HTTPServer

usecaseByContext = {
    #"work": SetupWork
}

if __name__ == "__main__":
    hostName = "localhost"
    serverPort = 9150
    server_url = "http://" + hostName + ":" + str(serverPort)

    chatbot = Chatbot(BuerroBot())

    Controller = ControllerFromArgs(chatbot, usecaseByContext)
    httpd = HTTPServer((hostName, serverPort),
        Controller)
    print("serving at port", serverPort)
    httpd.serve_forever()

