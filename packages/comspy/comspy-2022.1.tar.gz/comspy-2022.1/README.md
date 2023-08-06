### ComsPy

#### A package that uses Python to make communication easier

#### Latest release:2022.1

##### How to use

You need to create two programs to use this module, one called Server.py and the other called Client.py

Then type in Server.py:

```python
#English
import compys.Server.Server_English
compys.Server.Server_English.start()

#Chinese
import compys.Server.Server_Chinese
compys.Server.Server_Chinese.start()
```

In the Client.py input:

```python
#English
import compys.Client.Client_English
compys.Client.Client_English.start()

#Chinese
import compys.Client.Client_Chinese
compys.Client.Client_Chinese.start()
```

Run, and then enter the same communication port

input "QUIT" to exit

Note: they must be the same, otherwise normal communication will not work, unless you want to get to know an unknown stranger by chance

We will continue to update, try to make the interface in a short time, thank you for using