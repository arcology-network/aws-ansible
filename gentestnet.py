import sys
import json
import os




user = sys.argv[2]
confile = sys.argv[3]
rpm = sys.argv[4]
netname = sys.argv[5]
concurrency = sys.argv[6]
mount_point = sys.argv[7]



idx_host = 1
with open(sys.argv[1], 'r') as f:
    data = f.read()
    dict = json.loads(data)

    #nodes = {
    #           tags:[{idx:0,tag:x,ips:x}]
    #           ka:x,
    #           ka2:x,
    #           zk:x
    # }
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
                #print(node_tag)
                if node_tag.startswith('kafka0'):
                    node['ka'] = localip + ":9092"
                    node['ka2'] = localip + ":9092"
                    node['zk'] = localip + ":2181"
                elif node_tag.startswith('kafka1'):
                    node['ka'] = localip + ":9092"
                elif node_tag.startswith('kafka2'):
                    node['ka2'] = localip + ":9092"
                    node['zk'] = localip + ":2181"
            nodes[node_idx] = node
            
    hosts = []
    insids = {}
    idx_host = 1

    #print(nodes)

    for node_id,node in nodes.items():
        for tag in node['tags']:
            for ip in tag['ips']:
                ci = {}
                ci['ip'] = ip
                ci['region'] = dict['_meta']['hostvars'][ip]['ec2_region']
                ci['localip'] = dict['_meta']['hostvars'][ip]['ec2_private_ip_address']
                host_tag =  dict['_meta']['hostvars'][ip]['ec2_tag_Name']
                host_tag = host_tag[host_tag.find('_') + 1:]
                ci['tag'] = host_tag
                if ci['tag'].startswith('kafka'):
                    ci['kafka']="true"
                    ci['tag']=ci['tag'][len('kafka0_'):]
                else:
                    ci['kafka']="false"

                ci['name'] = 's'+ str(idx_host)
                idx_host = idx_host + 1
                ci['nidx'] = tag['idx']
                ci['nname'] = 'node'+ tag['idx']
               
                ci['mqaddr'] = node['ka']
                ci['mqaddr2'] = node['ka2']
                ci['zkUrl'] = node['zk']
          
                if ci['tag'].find('exec-svc')>=0:
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
    curHome = os.environ['HOME']

    for h in hosts: 
        host = {}
        host['name'] = h['name']
        host['ip'] = h['ip']
        host['localip'] = h['localip']
        host['username'] = user
        host['password'] = curHome + '/.ssh/' + h['region'] + '-private.pem'
            
        host['mqaddr'] = h['mqaddr']

        host['mqaddr2'] = h['mqaddr2']
        host['zkUrl'] = h['zkUrl']

        host['nidx'] = h['nidx']
        host['nname'] = h['nname']
        host['nthread'] = concurrency
        host['insid'] = str(h['insid'])
        host['remotepath'] = mount_point + '/'
        host['kafka'] = h['kafka']
        host['svcs'] = h['tag'].split('_')
        g_data['hosts'].append(host)
    
    
with open(confile, 'w') as out_file:
    json.dump(g_data, out_file, indent=4)

print('Testnet configuration file generated') 


