import socket

x = input ("\nPlease enter a domain name that you wish to translate: ")  

data = socket.gethostbyname_ex(x)
print ("\n\nThe IP Address of the Domain Name is: "+repr(data))  