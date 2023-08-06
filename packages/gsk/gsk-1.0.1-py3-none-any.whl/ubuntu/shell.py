import subprocess
import os
# from ipython import get_ipython
class Shell:
    def __init__(self):
        pass

    @staticmethod
    def run(cmd):
        if type(cmd)==str:
            cm = cmd.split(" ")
        else:
            cm = cmd
        test = subprocess.Popen(cm, stdout=subprocess.PIPE)
        output = test.communicate()[0]
        return output

    @staticmethod
    def runSystem(cmd):
        # out = os.popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = os.popen(cmd)
        print(cmd)
        return out.read()