import sys
import json
import os
import shutil
import subprocess

def print_output(result):  
  if result!=b'':
    print(result)

def findPlugs(plugs,svc):
  for plug in plugs:
    if svc.startswith('plug-'+plug+'-'):
      return True
  return False

user = sys.argv[2]
confile = sys.argv[3]
rpm = sys.argv[4]
netname = sys.argv[5]
concurrency = sys.argv[6]
mount_point = sys.argv[7]
ssh_port = sys.argv[8]


plugs=[]
if len(sys.argv)>=12:
    plugstring = sys.argv[11]
    plugs = plugstring.split(",")

svcItems = {}

with open(sys.argv[9], 'r') as f:
    data = f.read()
    services = json.loads(data)

    for svcitem in services:
        svcItems[svcitem['tag']]=svcitem['svcs']


with open(sys.argv[1], 'r') as f:
    data = f.read()
    dict = json.loads(data)

    nodes = {}
    for tag, ips in dict.items():
        if tag.startswith('tag_Name_'):
            sub_tag = tag[len('tag_Name_'):].lower()
            node_idx = sub_tag[:sub_tag.find('_')]
            sub_tag = sub_tag[sub_tag.find('_') + 1:]
            tag_item = {}
            tag_item['idx'] = node_idx
            tag_item['tag'] = sub_tag
            tag_item['ips'] = ips

            node = {}
            if node_idx in nodes:
                node = nodes[node_idx]
            else:
                node['tags']=[]
            node['tags'].append(tag_item)
            
            
            for ip in ips:
                localip = dict['_meta']['hostvars'][ip]['ec2_private_ip_address']
                node_tag = dict['_meta']['hostvars'][ip]['ec2_tag_Name'] 
                node_tag = node_tag[node_tag.find('_') + 1:]
                svcs=svcItems[node_tag]
                if 'kafka0' in svcs:
                    node['ka1'] = localip + ":9092"
                    node['ka2'] = localip + ":9092"
                    node['ka3'] = localip + ":9092"
                    node['zk'] = localip + ":2181"
                elif 'kafka1' in svcs:
                    node['ka1'] = localip + ":9092"
                    node['zk'] = localip + ":2181"
                elif 'kafka2' in svcs:
                    node['ka2'] = localip + ":9092"
                elif 'kafka3' in svcs:
                    node['ka3'] = localip + ":9092"
                
                for plug in plugs:
                    plug_str=""
                    if plug in node.keys():
                        plug_str=node[plug]
                    for svc in svcs:
                        if svc.startswith('plug-'+plug+'-'):
                            plug_str = plug_str + ','+ ip +':' +svc[len('plug-'+plug+'-'):]
                    node[plug]=plug_str

            nodes[node_idx] = node
            
    hosts = []
    insids = {}
    idx_host = 1

    #nidxes = {}
    nodeids = []
    #print(nodes)

    for node_id,node in nodes.items():
        #print(node_id)
        nodeids.append(node_id)
        for tag in node['tags']:
            for ip in tag['ips']:
                ci = {}
                ci['ip'] = ip
                ci['region'] = dict['_meta']['hostvars'][ip]['ec2_region']
                ci['localip'] = dict['_meta']['hostvars'][ip]['ec2_private_ip_address']
                host_tag =  dict['_meta']['hostvars'][ip]['ec2_tag_Name']
                host_tag = host_tag[host_tag.find('_') + 1:]
                svcs=svcItems[host_tag]
                ci['kafka']="false"
                for svc in svcs:
                    if svc.startswith('kafka'):
                        ci['kafka']="true"
                
                ci['svcs'] = svcs
                ci['name'] = 's'+ str(idx_host)
                idx_host = idx_host + 1
                ci['nidx'] = tag['idx']
                ci['nname'] = 'node'+ tag['idx']
               
                ci['mqaddr'] = node['ka1']
                ci['mqaddr2'] = node['ka2']
                ci['mqaddr3'] = node['ka3']
                ci['zkUrl'] = node['zk']

                for plug in plugs:
                    plug_str=node[plug]
                    if plug_str.startswith(','):
                        plug_str=plug_str[1:]
                    ci[plug] = plug_str
          
                if 'exec-svc' in svcs:
                    if tag['idx'] in insids:
                        insids[tag['idx']] = insids[tag['idx']] + 1
                        ci['insid'] = insids[tag['idx']]
                    else:
                        ci['insid'] = 1
                        insids[tag['idx']] = 1
                else:
                    ci['insid'] = 0
                hosts.append(ci)

    g_data = {}
    g_data['name'] = netname
    g_data['rpm'] = rpm
    g_data['hosts'] = []
    g_data['exclude'] = []
    curHome = os.environ['HOME']

    for h in hosts: 
        host = {}
        host['name'] = h['name']
        host['ip'] = h['ip']
        host['port'] =ssh_port
        host['localip'] = h['localip']
        host['username'] = user
        host['password'] = curHome + '/.ssh/' + h['region'] + '-private.pem'
            
        host['mqaddr'] = h['mqaddr']

        host['mqaddr2'] = h['mqaddr2']
        host['mqaddr3'] = h['mqaddr3']
        host['zkUrl'] = h['zkUrl']

        host['nidx'] = h['nidx']
        host['nname'] = h['nname']
        host['nthread'] = concurrency
        host['insid'] = str(h['insid'])
        host['remotepath'] = mount_point + '/'
        host['kafka'] = h['kafka']
        for plug in plugs:
            host[plug] = h[plug]

        svcs=[]
        for svc in h['svcs']:
            if svc.startswith('plug-'):
                if findPlugs(plugs,svc):
                    svcs.append(svc)
            else:
                svcs.append(svc)

        host['svcs'] = svcs
        g_data['hosts'].append(host)

        if "frontend-svc" in host['svcs']:
            print(host['nname']+' frontUrl: http://'+host['localip']+':8080') 

    #with open(confile+'/testnet.json', 'w') as out_file:
    with open(confile, 'w') as out_file:
        json.dump(g_data, out_file, indent=4)
    
    print('Testnet configuration file generated') 


destpath=sys.argv[10]
result =subprocess.check_output(["mkdir -p "+destpath],shell=True, stderr=subprocess.STDOUT)
print_output(result)


allfilename=sys.argv[9]
result =subprocess.check_output(["cp "+allfilename+" "+destpath+"/service.json"],shell=True, stderr=subprocess.STDOUT)
print_output(result)