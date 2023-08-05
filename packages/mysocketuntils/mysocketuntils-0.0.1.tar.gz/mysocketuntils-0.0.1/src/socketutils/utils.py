#!/home/ai-046/anaconda3/bin/python3
# -*- coding: utf-8 -*- #
# ------------------------------------------------------------------
# @File Name:        utils.py
# @Author:           wen
# @Version:          ver0_1
# @Created:          2022/2/10 上午10:56
# @Description:      Main Function:    xxx
# @Note:             xxx
# Function List:     hello() -- print helloworld
# History:
#       <author>    <version>   <time>      <desc>
#       wen         ver0_1      2020/12/15  xxx
# ------------------------------------------------------------------
import os
import sys
from tqdm import tqdm
import struct

class SocketUtils:
    def __init__(self):
        self.bufsize = 65536

    def Recv(self, conn, fmt, bufsize=None):
        msg = self.recv(conn, fmt, bufsize=bufsize)
        if msg is None:
            self.send(conn, "=I", 0)
        else:
            self.send(conn, "=I", len(msg))
        return msg

    def Send(self, conn, fmt, *args, bufsize=None):
        self.send(conn, fmt, *args, bufsize=bufsize)
        msg2 = self.recv(conn, "=I")
        return msg2

    def recv(self, conn, fmt, bufsize=None):
        msgsize = struct.calcsize(fmt)
        if bufsize is None: bufsize = self.bufsize
        if msgsize > bufsize:
            recv_size = 0
            msg = b''
            while recv_size < msgsize:
                recvsize = min(bufsize, msgsize - recv_size)
                recvmsg = conn.recv(recvsize)
                if len(recvmsg) == 0:
                    break
                msg += recvmsg
                recv_size = len(msg)
        else:
            msg = conn.recv(msgsize)
        if len(msg) == 0:
            return []
        return struct.unpack(fmt, msg)

    def send(self, conn, fmt, *args, bufsize=None):
        if bufsize is None: bufsize = self.bufsize
        msgsize = struct.calcsize(fmt)
        msg = struct.pack(fmt, *args)
        if msgsize > bufsize:
            send_index = 0
            while send_index < msgsize:
                send_size = min(bufsize, msgsize - send_index)
                conn.sendall(msg[send_index:send_index + send_size])
                send_index += send_size
        else:
            conn.sendall(struct.pack(fmt, *args))

    def readfile(self, filepath, bufsize=65536):
        filesize = os.path.getsize(filepath)
        bufsize = min(filesize, bufsize)
        contents = b''
        with open(str(filepath), 'rb') as f:
            while (bufsize <= filesize and bufsize > 0):
                contents += f.read(bufsize)
                filesize -= bufsize
                bufsize = min(filesize, bufsize)
        return contents

    def writefile(self, contents, savepath, bufsize=65536):
        bufsize = min(len(contents), bufsize)
        with open(str(savepath), 'wb') as f:
            while (bufsize <= len(contents) and bufsize > 0):
                f.write(contents[:bufsize])
                contents = contents[bufsize:]
                bufsize = min(len(contents), bufsize)
