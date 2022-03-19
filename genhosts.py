import sys
import json
import os
import shutil

ip2region = {}
tag2ips = {}
ip2node = {}

with open(sys.argv[1], 'r') as f:
    data = f.read()
    dict = json.loads(data)
    for tag, ips in dict.items():
        if tag.startswith('tag_Name_'):
            sub_tag = tag[len('tag_Name_'):].lower()
            node_idx = sub_tag[:sub_tag.find('_')]
            sub_tag = sub_tag[sub_tag.find('_') + 1:]
            for ip in ips:
                ip2node[ip] = node_idx
                if sub_tag in tag2ips:
                    tag2ips[sub_tag].append(ip)
                else:
                    ipps = []
                    ipps.append(ip)
                    tag2ips[sub_tag] = ipps
                ip2region[ip] = dict['_meta']['hostvars'][ip]['ec2_region']

#print(tag2ips)
#print(ip2region)

all = []
ammolite = []
kafka = []

user = sys.argv[2]
hostfile = sys.argv[3]
ammolite_tag = ""

envs = {}

with open(hostfile, 'w') as f:
    for tag, ips in tag2ips.items():
        for ip in ips:
            line = ip+' ansible_ssh_user='+ user +' node_idx='+ str(ip2node[ip]) +'  ansible_ssh_private_key_file=~/.ssh/'+ip2region[ip]+'-private.pem ansible_python_interpreter=/usr/bin/python3 base_path=/data/ \n'
            nIdx=str(ip2node[ip])
            lines=[]
            if tag.startswith('pet'): 
                all.append(line)

    f.write('[docker]\n')
    for line in all:
        f.write(line)

print('host file generated')      