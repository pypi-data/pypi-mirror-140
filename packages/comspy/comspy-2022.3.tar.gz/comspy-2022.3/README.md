### ComsPy

#### A package that uses Python to make communication easier

#### Latest release:2022.3

##### 0. A declaration for users using version 2022.1

If you're still using version 2022.1, please note:

1. README.md:The sample code is wrong, please change all compys to comspy
2. demos1.py and demos2.py:Please change all compys to comspy

##### 1. How to use

###### (1) User

You need to create two programs to use this module, one called Server.py and the other called Client.py

Then type in Server.py:

```python
#English
import comspy.user.Server_English
comspy.user.Server_English.start()

#Chinese
import comspy.user.Server_Chinese
comspy.user.Server_Chinese.start()
```

In the Client.py input:

```python
#English
import compy.user.Client_English
comspy.user.Client_English.start()

#Chinese
import compy.user.Client_Chinese
comspy.user.Client_Chinese.start()
```

Run, and then enter the same communication port

input "QUIT" to exit

Note: they must be the same, otherwise normal communication will not work, unless you want to get to know an unknown stranger by chance

We will continue to update, try to make the interface in a short time, thank you for using

###### (2)Developer

Example:

```python
#Server.py
from comspy.developer import * #import all functions

server_socket_init() #init the server socket
server_socket_bind(int(input("Enter a port:")))#set the connection
server_setlisten(3)#set the maximum of listening
server_buildconnect()#build th connection
while True:
	msg = input("Enter a msg:")
	server_sendmsg(msg)#send message
	if msg =="QUIT":
		exit()#stop
```

```python
#Client.py
from comspy.developer import * #import all functions

client_socket_init()#init the client socket
client_connect(int(input("Enter a port:")))#set and build the connection
while True:
	msg = client_receivemsg(2048)#receive message
	if msg =="QUIT":
		exit()#stop
	else:
		print(msg)
```

##### 2. What's new

There are now two modes: developer and user

You can use developer mode to create your own communication software

You can also use user mode to communicate