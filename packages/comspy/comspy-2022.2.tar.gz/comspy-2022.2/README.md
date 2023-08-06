### ComsPy

#### A package that uses Python to make communication easier

#### Latest release:2022.2

##### 0. A declaration for users using version 2022.1

If you're still using version 2022.1, please note:

1. README.md:The sample code is wrong, please change all compys to comspy
2. demos1.py and demos2.py:Please change all compys to comspy

##### 1. How to use

You need to create two programs to use this module, one called Server.py and the other called Client.py

Then type in Server.py:

```python
#English
import comspy.Server.Server_English
comspy.Server.Server_English.start()

#Chinese
import comspy.Server.Server_Chinese
comspy.Server.Server_Chinese.start()
```

In the Client.py input:

```python
#English
import compy.Client.Client_English
comspy.Client.Client_English.start()

#Chinese
import compy.Client.Client_Chinese
comspy.Client.Client_Chinese.start()
```

Run, and then enter the same communication port

input "QUIT" to exit

Note: they must be the same, otherwise normal communication will not work, unless you want to get to know an unknown stranger by chance

We will continue to update, try to make the interface in a short time, thank you for using

##### 2. What's new

In the Server.py function, the parameter Maximum_Number_Connections is set to set the maximum number of connections

In the Client.py function, we have added the Message_Reception_Size function, which sets the maximum file size. 2048 is recommended now.