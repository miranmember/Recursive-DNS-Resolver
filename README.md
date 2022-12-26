# Recursive-DNS-Resolver
Created the functionality of a recursive DNS resolver. 
This project is a recursive resolver built using the dnspython library. It allows you to lookup various DNS records (e.g., A, AAAA, MX, CNAME) for a given domain name.
The program performs all recursion by itself.
## Requirements
To use this project, you will need to have the following libraries installed:
+ dnspython
To install it run any of the following:
```
pip3 install dnspython
```
```
pip install dnspython
```
```
python -m pip install dnspython
```

## Running
To run the DNS on a website:
```
python resolve.py yahoo.com
```
To run DNS on multiple websites:
```
resolve.py first.com second.edu third.org
```
