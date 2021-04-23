import sys
import json
import os

hosts = []
mqs = []
mqs2 = []

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

    reg2tag2ips = {}
    for tag, ips in dict.items():
        if tag.startswith('tag_Name_'):
            tags = tag[len('tag_Name_'):].lower()
            for ip in ips:
                reg = dict['_meta']['hostvars'][ip]['ec2_region']

                tag2ips = {}
                if len(reg2tag2ips)>0 and reg in reg2tag2ips:
                    tag2ips = reg2tag2ips[reg]

                if len(tag2ips)>0 and tags in tag2ips:
                    tag2ips[tags].append(ip)
                else:
                    ipp = []
                    ipp.append(ip)
                    tag2ips[tags] = ipp

                reg2tag2ips[reg] = tag2ips
    
    for reg, tag22ips in reg2tag2ips.items():
        nodenums = 1
        for tags,ips in tag22ips.items():
            if tags.find('core_svc') >= 0:
                nodenums = len(ips)
                break

        insids = []
        for idx in range(0,nodenums):
            insids.append(1)

        for tags,ips in tag22ips.items():
            ipsnum = len(ips)
            step = ipsnum / nodenums
            idx_node = 0
            idx_step = 0 

            for ip in ips:
                ci = {}
                ci['ip'] = ip
                ci['region'] = dict['_meta']['hostvars'][ip]['ec2_region']
                ci['localip'] = dict['_meta']['hostvars'][ip]['ec2_private_ip_address']
                ci['tag'] = dict['_meta']['hostvars'][ip]['ec2_tag_Name']
                
                if ci['tag'].startswith('kafka0'):
                    mqs.append(ci['localip']+":9092")
                    mq = {}
                    mq['ka']=ci['localip']+":9092"
                    mq['zk']=ci['localip']+":2181"
                    mqs2.append(mq)
                elif ci['tag'].startswith('kafka1'):
                    mqs.append(ci['localip']+":9092")
                elif ci['tag'].startswith('kafka2'):
                    mq = {}
                    mq['ka']=ci['localip']+":9092"
                    mq['zk']=ci['localip']+":2181"
                    mqs2.append(mq)
                if ci['tag'].startswith('kafka'):
                    ci['kafka']="true"
                    ci['tag']=ci['tag'][len('kafka0_'):]
                else:
                    ci['kafka']="false"

                ci['name'] = 's'+str(idx_host)
                idx_host = idx_host + 1

                ci['nidx'] = idx_node
                ci['nname'] = 'node'+str(idx_node)
                idx_step = idx_step + 1

                if idx_step == step :
                    idx_node = idx_node + 1
                    idx_step = 0
                
                if ci['tag'].find('exec-svc')>=0:
                    ci['insid'] = insids[ci['nidx']]
                    insids[ci['nidx']] = insids[ci['nidx']] + 1
                else:
                    ci['insid'] = 0
                hosts.append(ci)

    print(reg2tag2ips)
    
print(hosts)


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
    
    host['mqaddr'] = mqs[h['nidx']]

    host['mqaddr2'] = mqs2[h['nidx']]['ka']
    host['zkUrl'] = mqs2[h['nidx']]['zk']

    host['nidx'] = str(h['nidx'])
    host['nname'] = h['nname']
    host['nthread'] = concurrency
    host['insid'] = str(h['insid'])
    host['remotepath'] = mount_point + '/'
    host['kafka'] = h['kafka']
    host['svcs'] = h['tag'].split('_')
    g_data['hosts'].append(host)

with open(confile, 'w') as out_file:
    json.dump(g_data, out_file, indent=4)




