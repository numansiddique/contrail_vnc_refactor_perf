import argparse
import os
import socket
import subprocess
import sys
import time

SERVER_PORT = '10001'


class VncPerfCmdReceiver():
    def __init__(self, v2_config_file, v3_config_file, is_devstack):
        self.v2_config_file = v2_config_file
        self.v3_config_file = v3_config_file
        self.is_devstack = is_devstack
        self.port = None
        if is_devstack:
            self.start_neutron_cmd = "sudo start neutron-server"
            self.stop_neutron_cmd = "sudo stop neutron-server"
        else:
            self.start_neutron_cmd = "sudo service neutron-server start"
            self.stop_neutron_cmd = "sudo service neutron-server stop"
        self.neutron_config_file = "/etc/neutron/neutron.conf"

    def _start_neutron_server(self, command):
        print '_start_neutron_server entered : command  = ', command

        # stop the neutron server
        try:
            subprocess.check_call(self.stop_neutron_cmd.split(" "))
        except Exception as e:
            print 'Exception while stopping the neutron : ', e
            return 'KO 1'

        print 'Stopped Neutron server'
        time.sleep(2)
        if command == "v2":
            copy_config_file_cmd = "sudo cp %s %s" % (self.v2_config_file,
                                                      self.neutron_config_file)
        else:
            copy_config_file_cmd = "sudo cp %s %s" % (self.v3_config_file,
                                                      self.neutron_config_file)
        try:
            print 'Copying the file : ', copy_config_file_cmd
            subprocess.check_call(copy_config_file_cmd.split(" "))
            print 'Copied the neutron config file'
        except Exception as e:
            print 'Exception while copying the file : ', copy_config_file_cmd
            print 'Exception : ', e
            return 'KO 2'

        time.sleep(2)
        print 'Starting the neutron server'
        # start the neutron server
        try:
            subprocess.check_call(self.start_neutron_cmd.split(" "))
        except:
            print 'Exception while starting the neutron server : ', e
            return 'KO 3'

        print 'Started the Neutron server'
        time.sleep(5)
        print 'Returning OK'
        return 'OK 4'

    def start(self, host, port):
        self.host = host
        self.port = port
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.bind((host, int(port)))
        self.serversocket.listen(5)

        while True:
            print 'Waiting for clients to connect '
            (clientsocket, address) = self.serversocket.accept()
            print 'client socket connected : ', address
            while True:
                try:
                    msg = clientsocket.recv(2)
                    if not msg:
                        print 'recieved returned None'
                        break
                    print 'Received command ', msg
                    if msg in ['v2', 'v3']:
                        status_msg = self._start_neutron_server(msg)
                        clientsocket.send(status_msg)
                    else:
                        print 'Invalid message. Ignoring it : ', msg
                except socket.error as e:
                    print 'Socket Error occured : disconnecting client', e
                    break
            try:
                clientsocket.shutdown(socket.SHUT_RD)
                clientsocket.close()
            except:
                pass
            break
        try:
            self.serversocket.shutdown(socket.SHUT_RD)
        except:
            pass
        self.serversocket.close()


parser = argparse.ArgumentParser(description='Start neutron service')

parser.add_argument('--v2-config-file', metavar='v2_config_file', type=str,
                    required=True,
                    help='Neutron config file path with contrail v2 plugin')

parser.add_argument('--v3-config-file', metavar='v3_config_file', type=str,
                    required=True,
                    help='Neutron config file path with contrail v3 plugin')

parser.add_argument('--is_devstack', metavar='is_devstack', type=bool,
                    default=True,
                    help='is it a devstack setup ')

parser.add_argument('--host', metavar='host', type=str,
                    required=True,
                    help='Server host ip to bind on')

parser.add_argument('--port', metavar='port', type=str,
                    default=SERVER_PORT,
                    help='Server port to listen on for commands')

args = parser.parse_args()

vnc_cmd_receiver = VncPerfCmdReceiver(args.v2_config_file, args.v3_config_file,
                                      args.is_devstack)

print 'Starting the Server to receive commands'
vnc_cmd_receiver.start(args.host, args.port)
print 'Done with it. Exiting'
