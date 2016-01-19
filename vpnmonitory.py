#!/usr/bin/python

import dbus.mainloop.glib; dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
from gi.repository import GObject
import subprocess
from subprocess import Popen, PIPE
import sys
import os
import signal

application=sys.argv[1]
	
def vpn_handler(*args, **kwargs):
    print "Caught signal (in catchall handler) "
    print args
    cmd = list()
    cmd = ["pgrep",application]

    if args[0] == 7 and args[1] == 2:
        p = Popen(cmd, stdout=PIPE)
        out,err = p.communicate()
        print "killing process " + str(out)
        os.kill(int(out),signal.SIGKILL)
        return
    if args[0] == 5 and args[1] == 1:
        print 'starting tribler'
        p = Popen([application], stdout=PIPE)
        out, err = p.communicate()
        print out

if __name__ == "__main__":
    
    #application to start or kill when vpn is on or off 
        
    bus= dbus.SystemBus()
    object = bus.get_object('org.freedesktop.NetworkManager',
            '/org/freedesktop/NetworkManager/VPN')
    bus.add_signal_receiver(vpn_handler, dbus_interface = 'org.freedesktop.NetworkManager.VPN.Connection', message_keyword='VpnStateChanged')
    loop = GObject.MainLoop()
    loop.run()


