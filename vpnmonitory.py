#!/usr/bin/python

import dbus.mainloop.glib; dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
from gi.repository import GObject
import subprocess
from subprocess import Popen, PIPE
import sys
import os
import signal
import getopt
import time
import pdb

application=sys.argv[1]
__procopenvpn=0
__procapp=0
	
def vpn_handler(*args, **kwargs):
    print "Caught signal (in catchall handler) "
    print args
    cmd = list()
    cmd = ["pgrep","-f",application]

    if args[0] == 7 and args[1] == 2:
        p = Popen(cmd, stdout=PIPE)
        out,err = p.communicate()
        print "killing process " + str(out)
        os.kill(int(out),signal.SIGKILL)
        return
    if args[0] == 5 and args[1] == 1:
        print 'starting tribler'
        p = Popen(["nohup",application,"&"])
        out, err = p.communicate()
        print out

def startOpenVpn(optarg,app):
    cmd = list()
    cmd = ["nohup","/usr/sbin/openvpn","--daemon", "--config",optarg,"--log","/var/log/openvpn.log"]
    global __procopenvpn
    print optarg
    __procopenvpn = Popen(cmd, close_fds=True,preexec_fn=os.setsid)
    time.sleep(5)
    print app
    cmd = ["nohup",app,"&"]
    global __procapp
    __procapp = Popen(cmd, close_fds=True,preexec_fn=os.setsid)
    time.sleep(2)

def mainloop():
    time.sleep(5)
    while(True):
        cmd = ["ifconfig","tun0"]
        proc = Popen(cmd, stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        out, err = proc.communicate()
        if("UP POINTOPOINT" in out):
            time.sleep(2)
            continue
        else:
            print "killing " + str(__procapp.pid)
            os.killpg(__procapp.pid, signal.SIGUSR1)
            time.sleep(2)
            print "killing " + str(__procopenvpn.pid)
            os.killpg(__procopenvpn.pid, signal.SIGUSR1)
            os.killpg(__procopenvpn.pid+1, signal.SIGUSR1)
            break




if __name__ == "__main__":
    
    #application to start or kill when vpn is on or off 
    opts, args = getopt.getopt(sys.argv[1:], "oan:h", ["openvpn=","application=","networkManager="])
    app = ""
    for opt, arg in opts:
        if opt in ("-o", "--openvpn"):             
            pdb.set_trace()

        #start openvpn via commandline
            startcmd = True
            optarg = arg
        elif opt in ("-a","--application"):
            app = arg
        elif opt in ("-n","--networkManager"):
            bus= dbus.SystemBus()
            object = bus.get_object('org.freedesktop.NetworkManager',
            '/org/freedesktop/NetworkManager/VPN')
            bus.add_signal_receiver(vpn_handler, dbus_interface = 'org.freedesktop.NetworkManager.VPN.Connection', message_keyword='VpnStateChanged')
            loop = GObject.MainLoop()
            loop.run()
            sys.exit()
        else:
            assert False, "unhandled option"
    if(startcmd):
        startOpenVpn(optarg,app)
        mainloop()

