import socket
from os import stat
import re
import threading

TCP_IP = '127.0.0.1'
TCP_PORT = 9999
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

def html_response(conn):
    html = "HTTP/1.1 200 OK\r\nContent-Length: {0}\r\nContent-Type: text/html\r\n\n{1}"
    while 1:
        data = conn.recv(BUFFER_SIZE)
        if len(re.findall(r'GET /index.html', data)):
            f = open('index.html').read()
            conn.send(html.format(len(f), f))

def jpg_response(conn):
    jpg = "HTTP/1.1 200 OK\r\nContent-Length: {0}\r\nContent-Type: image/jpg\r\n\n{1}"
    while 1:
        data = conn.recv(BUFFER_SIZE)
        if len(re.findall(r'GET /image.jpg', data)):
            f = open('image.jpg', 'rb').read()
            conn.send(jpg.format(stat('image.jpg').st_size, f))

conn, addr = s.accept()
t1 = threading.Thread(target=html_response, args=(conn,))
t2 = threading.Thread(target=jpg_response, args=(conn,))
t1.start()
t2.start()

