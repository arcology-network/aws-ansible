import json
import sys

hostfile=sys.argv[1]

with open(hostfile, 'r') as fp:
    data = json.load(fp)

ips=data['security_group_ansible_sec_group']
idx=0
for ip in ips:
    tag_name_1={}
    ipp=[]
    ipp.append(ip)
    data['tag_Name_'+str(idx)+'_s1']=ipp
    data['_meta']['hostvars'][ip]['ec2_tag_Name']=str(idx)+'_s1'
    idx=idx+1


with open(hostfile, 'w') as fp:
    json.dump(data, fp, indent=2)