import socket

from bsocket import connect

#
# Connect to server and run debug shell
#
def run_shell(conf):
    s = connect.connect(conf.serveraddr, conf.serverport, "debug-shell", "CONTROLLER")

    while True:
        print("[branch] ~> ", end = '')
        line = input()
        
        if(line == ""):
            continue

        data = connect.send_msg(s, line)
        print("Response: {}".format(data))


