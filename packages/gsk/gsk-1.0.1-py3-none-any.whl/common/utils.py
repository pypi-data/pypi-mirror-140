
import time
import random
def numberEncode(n,salt):
    if n == 0:
        return "0"

    # q = "0123456789-abcdefghijklmnopqrstuvwxyz_ABCDEFGHIGHIJKLMNOPQRSTUVWXYZ"
    q = salt
    s = ""
    while n > 0 :
        c = n % len(q)
        s = s+q[c]
        n = int(n / len(q))
    return s

def uniqid():
    
    l = str(time.time()).replace(".","")+str(random.randint(1,99999999))
    s = numberEncode(int(l),"0123456789-abcdefghijklmnopqrstuvwxyz_ABCDEFGHIGHIJKLMNOPQRSTUVWXYZ")
    return s

