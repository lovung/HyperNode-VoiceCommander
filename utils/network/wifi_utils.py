#!/usr/bin/python
import uuid

def getMACString():
	mac = uuid.getnode()
	return hex(mac)[2:]
