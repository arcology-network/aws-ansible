import sys
import json

ip2region = {}
tag2ips = {}

with open(sys.argv[1], 'r') as f:
    data = f.read()
    dict = json.loads(data)
    for tag, ips in dict.items():
        if tag.startswith('tag_Name_'):
            tag2ips[tag[len('tag_Name_'):].lower()] = ips
            for ip in ips:
                ip2region[ip] = dict['_meta']['hostvars'][ip]['ec2_region']

print(tag2ips)
print(ip2region)

all = []

user = sys.argv[2]
hostfile = sys.argv[3]


with open(hostfile, 'w') as f:
    for tag, ips in tag2ips.items():
        #f.write('['+tag+']\n')
        for ip in ips:
            #line = ip+' ansible_ssh_private_key_file=~/.ssh/'+ip2region[ip]+'-private.pem ansible_python_interpreter=/usr/bin/python3\n'
            line = ip+' ansible_ssh_user='+ user +' ansible_ssh_private_key_file=~/.ssh/'+ip2region[ip]+'-private.pem ansible_python_interpreter=/usr/bin/python3\n'
            #f.write(line)
            all.append(line)
    f.write('[envs]\n')
    for line in all:
        f.write(line)
    
    f.write('[all:vars]\n')
    f.write('host_key_checking = False\n')
    f.write('ansible_port=22\n')
    f.write('ansible_ssh_port=22\n')
    f.write('forks=5\n')


for tag, ips in tag2ips.items():
    print(tag)
    for ip in ips:
        print('ssh -i ~/.ssh/%s-private.pem ubuntu@%s' % (ip2region[ip], ip))
