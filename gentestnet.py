import sys
import json
import os
import subprocess

def print_output(result):  
  if result!=b'':
    print(result)

hostfile = sys.argv[1]
testcfg = sys.argv[2]
servicecfg = sys.argv[3]
destpath = sys.argv[4]

svcItems = {}
svcApps = {}
cfgs = {}

with open(servicecfg, 'r') as f:
    data = f.read()
    cfgs = json.loads(data)
    
    services = cfgs["services"]

    for svcitem in services:
        svcItems[svcitem['tag']]=svcitem['svcs']
        svcApps[svcitem['tag']]=svcitem['apps']


with open(hostfile, 'r') as f:
    data = f.read()
    dict = json.loads(data)

    nodes = []
    idx_host = 1
    curHome = os.environ['HOME']

    for tag, ips in dict.items():
        if tag.startswith('tag_Name_'):
            sub_tag = tag[len('tag_Name_'):].lower()
            node_idx = sub_tag[:sub_tag.find('_')]
            sub_tag = sub_tag[sub_tag.find('_') + 1:]
          
            for ip in ips:
                node = {}

                node['name'] = 's'+ str(idx_host)
                idx_host = idx_host + 1
                node["ip"]=ip
                node['localip']=dict['_meta']['hostvars'][ip]['ec2_private_ip_address']
                node['port'] = cfgs["ssh_port"] 
                node['username'] = cfgs["user"]
                node['password'] = curHome + '/.ssh/' + dict['_meta']['hostvars'][ip]['ec2_region'] + '-private.pem'
                node['nidx'] = node_idx
                node['workspace'] = cfgs["mount_point"]  + '/'
                node['svcs'] = svcItems[sub_tag]
                node['apps'] = svcApps[sub_tag]

                nodes.append(node)

                if "frontend-svc" in node['svcs']:
                    print("node"+node_idx+' frontUrl: http://'+node['localip']+':8080') 

    g_data = {}
    g_data['name'] = cfgs["name"]
    g_data['chainid'] = cfgs["chainid"]
    g_data['concurrency'] = cfgs["concurrency"]
    g_data['eus'] = cfgs["eus"]
    g_data['exclude'] = []  
    g_data['hosts'] = nodes
    with open(testcfg, 'w') as out_file:
        json.dump(g_data, out_file, indent=4)
    
    print('Testnet configuration file generated')          


result =subprocess.check_output(["mkdir -p "+destpath],shell=True, stderr=subprocess.STDOUT)
print_output(result)

result =subprocess.check_output(["cp "+servicecfg+" "+destpath+"/service.json"],shell=True, stderr=subprocess.STDOUT)
print_output(result)