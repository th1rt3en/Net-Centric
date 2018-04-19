
# coding: utf-8

# In[1]:


import socket
import time
import sys
import json

IP = "127.0.0.1"
Port = 9999


# In[2]:


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, Port))


# In[3]:


clients = []


# In[4]:


def broadcast(data):
    global clients
    for client in clients:
        sock.sendto(data, client[1])


# In[ ]:


while True:
    data = None
    message = None
    try:
        data, addr = sock.recvfrom(1024)
        message = json.loads(data)
        client = (message['username'], addr)
        if client not in clients:
            clients.append(client)
    except socket.error:
        time.sleep(0.01)
    if data:
        print data
        try: 
            if(message['message'].startswith("/hello")):
                outjson = {"username":"server", "message":message['username']+" joined the chat"} 
                broadcast(json.dumps(outjson))
            elif (message['message'].startswith("/who")):
                outjson = {"username":"server", "message":"people in room: "+', '.join([y[0] for y in clients])} 
                sock.sendto(json.dumps(outjson), client[1])
            elif (message['message'].startswith("/goodbye")):
                outjson = {"username":"server", "message":message['username']+" left the chat"} 
                clients.remove(client)
                broadcast(json.dumps(outjson))
            else:
                outjson = {"username":message['username'], "message":message['message']}
                broadcast(json.dumps(outjson))
                print clients
        except ValueError:
            print "indecipherable json"

