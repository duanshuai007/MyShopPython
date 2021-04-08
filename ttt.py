import os


r = os.popen("ls /dev/tty.* | grep usbserial").read().split('\n')
print(r)
'''
ret = r.read()
print(ret)

rr = ret.split('\n')
print(rr)
'''
