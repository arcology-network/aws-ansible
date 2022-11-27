import sys
import json
import os
import subprocess
import yaml
sys.path.append("../cluster")
import installsvclib

hostfile = sys.argv[1]
testcfg = sys.argv[2]
servicecfg = sys.argv[3]
destpath = sys.argv[4]
regionfile = sys.argv[5]

svcItems = {}
svcApps = {}
cfgs = {}

installsvclib._init()
logger = installsvclib.initLog('monaco','cluster.log')

regions = {}
with open(regionfile, 'r') as f:
    data = f.read()
    regions = json.loads(data)

with open(servicecfg, 'r') as f:
    data = f.read()
    cfgs = json.loads(data)

    services = cfgs["services"]

    for svcitem in services:
        svcItems[svcitem['tag']]=svcitem['svcs']
        svcApps[svcitem['tag']]=svcitem['apps']

plans = {}
with open(sys.argv[6], 'r') as stream:
    try:
        cfg = yaml.safe_load(stream)
        nodes = {}       

        for group in cfg['node_cfg']:
            nodes[group['id']] = group

        for region in cfg['regions']:
            node_idx = region['node_idx_start']
            for node_key in region['node_cluser_list']:
                for inst in nodes[node_key]['instances']:
                    nums = 0
                    if regions[region['region']] in plans:
                        nums=plans[regions[region['region']]]
                    nums = nums + inst['count']
                    plans[regions[region['region']]]=nums
    
    except yaml.YAMLError as exc:
        print(exc)

with open(hostfile, 'r') as f:
    data = f.read()
    dict = json.loads(data)

    nodes = {}  #
    curHome = os.environ['HOME']

    for tag, ips in dict.items():
        if tag.startswith('tag_Name_'):
            sub_tag = tag[len('tag_Name_'):].lower()
            node_idx = sub_tag[:sub_tag.find('_')]
            sub_tag = sub_tag[sub_tag.find('_') + 1:]
            
            for ip in ips:
                node = {}

                node['name'] = 's'
                node["ip"]=ip
                node['localip']=dict['_meta']['hostvars'][ip]['ec2_private_ip_address']
                node['port'] = cfgs["ssh_port"] 
                node['username'] = cfgs["user"]
                node['password'] = curHome + '/.ssh/' + dict['_meta']['hostvars'][ip]['ec2_region'] + '-private.pem'
                node['nidx'] = node_idx
                node['workspace'] = cfgs["mount_point"]  + '/'
                node['svcs'] = svcItems[sub_tag]
                node['apps'] = svcApps[sub_tag]
                node['region'] = regions[dict['_meta']['hostvars'][ip]['ec2_region']]


                nodelist = []
                if node_idx in nodes:
                    nodelist = nodes[node_idx]
                nodelist.append(node)
                nodes[node_idx] = nodelist

                
    
    idxes =  []
    for idx,list in nodes.items():
        idxes.append(int(idx))
    idxes.sort()

    sortedNodes = []
    hidx = 0
    nidx = 0
    results = {}
    installsvclib.printSection('Created Hosts Informations')
    for idx in idxes:
        list = nodes[str(idx)]
        for n in list:
            n['name']='s'+str(hidx)
            n['nidx'] = str(nidx)
            region = n['region']
            installsvclib.printLog("Node index: {} Ip: {} in {} ".format(str(nidx),n['ip'],region))
            nums = 0
            if region in results:
                nums = results[region]
            nums = nums + 1
            results[region] = nums

            sortedNodes.append(n)
            hidx = hidx + 1
        nidx = nidx + 1
    
    installsvclib.printSection('Created Hosts Summary')
    for region,num in plans.items():
        installsvclib.printLog("Success: {} \t\tFailed: {} \t\tRegion: {}".format(results[region],num-results[region],region))
    
    g_data = {}
    g_data['name'] = cfgs["name"]
    g_data['chainid'] = cfgs["chainid"]
    g_data['concurrency'] = cfgs["concurrency"]
    g_data['eus'] = cfgs["eus"]
    g_data['exclude'] = []  
    g_data['hosts'] = sortedNodes
    with open(testcfg, 'w') as out_file:
        json.dump(g_data, out_file, indent=4)
    
    print('Testnet configuration file generated')          


result =subprocess.check_output(["mkdir -p "+destpath],shell=True, stderr=subprocess.STDOUT)
installsvclib.print_output(result)

result =subprocess.check_output(["cp "+servicecfg+" "+destpath+"/service.json"],shell=True, stderr=subprocess.STDOUT)
installsvclib.print_output(result)