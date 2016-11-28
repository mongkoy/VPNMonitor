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
import getpass
import pdb

application=sys.argv[1]
__procopenvpn=0
__procapp=0
password = ""
app=""
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
    cmd = ['sudo','-S','/usr/sbin/openvpn',"--daemon", "--config",optarg,"--log","/var/log/openvpn.log"]

    #cmd = 'sudo -S /usr/sbin/openvpn --config ' + optarg + '--daemon --log /var/log/openvpn.log'
    global __procopenvpn
    print cmd
    global password
    password = getpass.getpass("enter sudo password:")
    __procopenvpn = Popen(cmd, stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    output,err = __procopenvpn.communicate(password+'\n')
    #pdb.set_trace()

def mainloop(app):
    while(True):
        cmd = ["ifconfig","tun0"]
        proc = Popen(cmd, stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        out, err = proc.communicate()
        time.sleep(10)
        if("UP POINTOPOINT" in out):
            break
    print app
    if app:
        cmd = ["nohup",app,"&"]
        global __procapp
        __procapp = Popen(cmd, close_fds=True,preexec_fn=os.setsid)

    time.sleep(2)
    while(True):
        cmd = ["ifconfig","tun0"]
        proc = Popen(cmd, stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        out, err = proc.communicate()
        if("UP POINTOPOINT" in out):
            time.sleep(2)
            continue
        else:
            cmd = 'ps aux |grep -v grep | grep "Tribler.Main"' 
            proc = Popen(cmd, stdin=subprocess.PIPE,stdout=subprocess.PIPE,shell=True)
            out,err = proc.communicate()
            procId= out.split()[1]
            print 'killing procId: ' + procId
            if procId:
               proc = Popen("kill -9 " + procId, stdin=subprocess.PIPE,shell=True)
            time.sleep(2)
            print "killing openvpn"
            cmd = ["sudo","killall",'-9',"openvpn"]
            prockill = Popen(cmd, stdin=subprocess.PIPE,stdout=subprocess.PIPE)
            out,err=prockill.communicate(password+'\n')
            print out
            break

if __name__ == "__main__":    
    #application to start or kill when vpn is on or off 
    opts, args = getopt.getopt(sys.argv[1:], "oa:n:h", ["openvpn=","application=","networkManager="])
    #pdb.set_trace()

    for opt, arg in opts:
        if opt in ("-o", "--openvpn"): 
        #start openvpn via commandline
            startcmd = True
            optarg = arg
        elif opt in ("-a","--application"):
            app = arg
            print app
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
        mainloop(app)

