import argparse
import os
import socket
import sys
import time

from neutronclient.v2_0.client import Client as NeutronClient


class VncPerfClient(object):
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((server_ip, int(server_port)))

    def _send_msg(self, msg, length=None):
        if not length:
            length = len(msg)

        totalsent = 0
        while totalsent < length:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def _recv_msg(self, length):
        chunks = []
        bytes_recd = 0
        while bytes_recd < length:
            chunk = self.sock.recv(min(length - bytes_recd, 2048))
            if chunk == '':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return ''.join(chunks)

    def _send_and_recv_msg(self, msg):
        print 'Sending msg : ', msg
        self._send_msg(msg)
        msg = self._recv_msg(4)
        print 'Received the msg ', msg

    def start_neutron_with_contrail_v2(self):
        self._send_and_recv_msg("v2")

    def start_neutron_with_contrail_v3(self):
        self._send_and_recv_msg("v3")

    def disconnect(self):
        try:
            self.sock.shutdown(socket.SHUT_RD)
        except:
            pass

        self.sock.close()


class VncPerfCheck(object):

    def __init__(self, server_ip, server_port, output_file_name):
        kwargs = {}
        kwargs['username'] = os.environ.get('OS_USERNAME')
        kwargs['tenant_name'] = os.environ.get('OS_TENANT_NAME')
        kwargs['auth_url'] = os.environ.get('OS_AUTH_URL')
        # kwargs['endpoint_url'] = os.environ.get('OS_AUTH_URL')
        kwargs['auth_strategy'] = 'keystone'
        kwargs['password'] = os.environ.get('OS_PASSWORD')
        self.client = NeutronClient(**kwargs)

        try:
            self.vnc_per_client = VncPerfClient(server_ip, server_port)
        except:
            print 'Connecting to the server failed . check if the server is up'
            sys.exit(0)

        self.output_file_name = output_file_name
        self.perf_data = {}
        self.no_of_runs = 3

    def start(self):
        print 'Starting the performance measure '
        print 'Sending the command to start contrail plugin v2'
        self.vnc_per_client.start_neutron_with_contrail_v2()
        time.sleep(10)
        print 'Starting the resource list tests for contrail plugin v2'
        self.perf_data['contrail_plugin_v2'] = self._run_performance_tests()

        print 'Sending the command to start contrail plugin v3'
        self.vnc_per_client.start_neutron_with_contrail_v3()
        time.sleep(10)
        print 'Starting the resource list tests for contrail plugin v3'
        self.perf_data['contrail_plugin_v3'] = self._run_performance_tests()
        print 'Done for now'

    def stop(self):
        print 'Stopping the client : reverting back to v2'
        self.vnc_per_client.start_neutron_with_contrail_v2()
        time.sleep(10)
        print 'Disconnecting now'
        self.vnc_per_client.disconnect()

    def save_data(self):
        print 'Saving the data'
        print self.perf_data

    def _run_resource_list(self, resource):
        result = {}
        for i in range(self.no_of_runs):
            run = 'run_%s' % str(i)
            print 'Starting : ', run
            start_time = time.time()
            res_func = getattr(self.client, 'list_' + resource)
            net_list = res_func()[resource]
            end_time = time.time()
            print 'Completed : ', run
            result[run] = {'time_taken': str(end_time - start_time),
                           resource: len(net_list)}
            time.sleep(5)

        return result

    def _run_performance_tests(self):
        perf_result = {}
        # run net-list first
        for resource in ['networks', 'ports', 'subnets']:
            print 'Running the resource list for : ', resource
            perf_result[resource] = self._run_resource_list(resource)

        return perf_result

parser = argparse.ArgumentParser(description='Start neutron service')

parser.add_argument('--server_ip', metavar='server_ip', type=str,
                    required=True,
                    help='Server host ip to connect to')

parser.add_argument('--port', metavar='port', type=str,
                    default='10002',
                    help='Server port to connect to')

parser.add_argument('--output_file', metavar='output_file', type=str,
                    required=True,
                    help='Result output file name')

args = parser.parse_args()

vnc_perf_check = VncPerfCheck(args.server_ip, args.port, args.output_file)

print 'Starting the performance checking'
vnc_perf_check.start()
vnc_perf_check.stop()
vnc_perf_check.save_data()

print 'Exiting..'
