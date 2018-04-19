
# coding: utf-8

# In[2]:


import socket
import os
import sys
import thread
import time
import json

IP = "127.0.0.1"
Port = 9999
username = raw_input("Enter your username: ")


# In[3]:


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# In[5]:


def get_messages():
    global sock, username
    while True:
        data = None
        try:
            data, addr = sock.recvfrom(1024)
        except socket.error:
            time.sleep(0.01)
        if data:
            try:
                message = json.loads(data)
                if(message['username'] != username):
                    msg_str = message['message']
                    if(message['username']):
                        msg_str = message['username'] + ": " + msg_str
                    if len(message['message']) > 0:
                        print msg_str
            except ValueError:
                print "error: tried to decode something invald"


# In[6]:


def get_input():
    global sock, username
    try:
        while True:
            message = {"username":username, "message":raw_input().strip()}
            sock.sendto(json.dumps(message), (IP, Port))
    except KeyboardInterrupt:
        print "Disconnected"


# In[ ]:


thread.start_new_thread(get_input, ())
thread.start_new_thread(get_messages, ())

message = {"username":username, "message":"/hello"}
sock.sendto(json.dumps(message), (IP, Port))
message = {"username":username, "message":"/who"}
sock.sendto(json.dumps(message), (IP, Port))
try: 
    while 1:
        time.sleep(0.01)
except KeyboardInterrupt:
    print "bye"
    message = {"username":username, "message":"/goodbye"}
    sock.sendto(json.dumps(message), (IP, Port))
    sys.exit(0)

