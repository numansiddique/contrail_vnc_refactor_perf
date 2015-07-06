# contrail_vnc_refactor_perf

Measure the time time for the port-list, net-list and subnet-list and other 
list commands by the contrail neutron plugin v2 and refactored v3.

Please follow the below steps to run this small crapy program

1. Cherry pick this patch - https://review.opencontrail.org/#/c/11280/
   into the contrail-neutron-plugin repo.
   
2. Create lots of networks, ports, subnets, routers, fips, security groups/rules.

3. Make sure that neutron server can be started or stopped using the
   upstart/service command. 
   If you are running devstack, then you create an upstart configuration by
   refering to the file "neutron-server-upstart.conf".
   This program switches between the v2 plugin and v3 plugin by stopping and
   starting the neutron server.

4. This repo has two programs - vnc_perf_server.py and vnc_perf_check.py
    vnc_perf_server.py should be run in the node where neutron server is run.
   vnc_perf_check.py can be run in any node as long as the neutron server
   and keystone is reachable. vnc_perf_check uses the neutron client to send 
   the commands. So source the openstack credentials.
   
4. Run vnc_perf_server.py as shown below
    $sudo python vnc_perf_server.py --v2-config-file <V2 PLUGIN CONFIG FILE PATH>
    --v3-config-file <V2 PLUGIN CONFIG FILE PATH> --is_devstack True/False 
    --host <IP ADDR OF NEUTRON SERVER> --port <PORT NO TO LISTEN>

    Eg.
    
    $sudo python vnc_perf_server.py --v2-config-file /etc/neutron/neutron_v2.conf
    --v3-config-file /etc/neutron/neutron_v3.conf --is_devstack True 
    --host 10.43.100.3 --port 10002

    Set is_devstack to True if running in devstack environment.
    --v2-config-file --> This takes the path of the neutron.conf in which
    core_plugin is defined as
    "core_plugin=core_plugin = neutron_plugin_contrail.plugins.opencontrail.contrail_plugin.NeutronPluginContrailCoreV2"

    --v3-config-file --> This takes the path of the neutron.conf in which
    core_plugin is defined as
    "core_plugin=core_plugin = neutron_plugin_contrail.plugins.opencontrail.contrail_plugin_v3.NeutronPluginContrailCoreV3"
   
5. Run vnc_perf_check.py as 
   $python vnc_perf_client.py --server_ip <NEUTRON_SERVER_IP> --port <VNC_PERF_SERVER_PORT>
   --output_file <output file name >
   
   Eg.  python vnc_perf_client.py --server_ip 10.43.100.09 --port 10002 --output_file out_file



   