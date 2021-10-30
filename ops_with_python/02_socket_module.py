#!/bin/env python
#-*- coding: utf-8 -*-

import socket
host= socket.gethostbyname_ex("www.google.com")

print("\n---------Host Info.---------")
print(host)

print("\n---------Host line by line---------")
for i in host :
    print(i)

(hostname, aliaslist, ipaddrlist) = host
print("\n---------IP Addr.---------")
print("ip :", ipaddrlist[0])