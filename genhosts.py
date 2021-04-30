import sys
import json

ip2region = {}
tag2ips = {}

with open(sys.argv[1], 'r') as f:
    data = f.read()
    dict = json.loads(data)
    for tag, ips in dict.items():
        if tag.startswith('tag_Name_'):
            sub_tag = tag[len('tag_Name_'):].lower()
            sub_tag = sub_tag[sub_tag.find('_') + 1:]
            for ip in ips:
                if sub_tag in tag2ips:
                    tag2ips[sub_tag].append(ip)
                else:
                    ipps = []
                    ipps.append(ip)
                    tag2ips[sub_tag] = ipps
                ip2region[ip] = dict['_meta']['hostvars'][ip]['ec2_region']

print(tag2ips)
print(ip2region)

all = []
ammolite = []
kafka = []

user = sys.argv[2]
hostfile = sys.argv[3]
ammolite_tag = ""

with open(hostfile, 'w') as f:
    for tag, ips in tag2ips.items():
        for ip in ips:
            line = ip+' ansible_ssh_user='+ user +' ansible_ssh_private_key_file=~/.ssh/'+ip2region[ip]+'-private.pem ansible_python_interpreter=/usr/bin/python3\n'
            all.append(line)
            if tag.startswith('ammolite'):
                ammolite.append(line)
                ammolite_tag = tag
            if tag.startswith('kafka'):
                kafka.append(line)

    f.write('[envs]\n')
    for line in all:
        f.write(line)
    
    ammolite_tag = ammolite_tag.replace('_','-')
    if len(ammolite_tag)>0:
        f.write('['+ ammolite_tag +']\n')
    for line in ammolite:
        f.write(line)
    
    f.write('[kafka]\n')
    for line in kafka:
        f.write(line)
    
    f.write('[all:vars]\n')
    f.write('host_key_checking = False\n')
    f.write('ansible_port=22\n')
    f.write('ansible_ssh_port=22\n')
    f.write('forks=15\n')

ammolite_ips = {}

for tag, ips in tag2ips.items():
    print(tag)
    if tag.startswith('ammolite'):
        ammolite_ips = ips
    for ip in ips:
        print('ssh -i ~/.ssh/%s-private.pem ubuntu@%s' % (ip2region[ip], ip))

for ip in ammolite_ips:
    print('scp -i ~/.ssh/%s-private.pem -r ../txs %s@%s:/data' % (ip2region[ip], user,ip))

      