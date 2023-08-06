import os
import sys
import requests
import time
import logging

logging.basicConfig(level=logging.DEBUG)

s = requests.Session()

pid = os.fork()
if pid == 0:
    time.sleep(1)
    print("Parent process")
else:
    print("Sub process")


s.get('http://www.baidu.com')
s.get('http://www.baidu.com')

