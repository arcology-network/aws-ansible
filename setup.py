#!/usr/bin/env python3
import sys
import yaml
import subprocess
import json
import os
from rich.progress import Progress
from subprocess import Popen, PIPE
sys.path.append("../cluster")
import installsvclib


def create_instance(op,ev,logfile, key_file):
    cmds='ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook --vault-password-file '+ os.getcwd()+'/vault -e ansible_python_interpreter=/usr/bin/python3 '+op+' --key-file '+ key_file +' -e "'+ev+'" >'+ logfile +' 2>&1'
    return cmds

def createShell(shfile,commands,jobs):
    with open(shfile, 'w') as f:
        f.write('#!/bin/sh\n')
        # f.write('date\n')
        idx=0
        for cmd in commands:
            if len(commands)>1:
                f.write('{\n')
            f.write('  '+cmd+'\n')
            f.write('  if [ $? -eq 0 ]; then\n')
            f.write('    echo "Instance created:['+jobs[idx]['ev'] +']"\n')
            f.write('  else\n')
            f.write('    echo "Instance ['+jobs[idx]['ev'] +'] FAILED, see log:'+jobs[idx]['log_file'] +'"\n')
            f.write('  fi\n')
            if len(commands)>1:
                f.write('} &\n')
            idx=idx+1
        if len(commands)>1:
            f.write('wait\n') 
        # f.write('date\n')  


def loadnetconf(netconfig):
    groups = {}
    nets = {}

    with open(netconfig, 'r') as f:
        for line in f:
            line = line.rstrip('\n')
            
            segments = line[2:].split(',')
            if line.startswith('g:'): 
                groups[segments[0]]=segments[1]
            elif line.startswith('n:'):
                nets[segments[0]+'-'+segments[1]]=segments[2]
            
    return groups,nets


installsvclib._init()
logger = installsvclib.initLog('monaco','cluster.log')

regions = {}

with open(sys.argv[4], 'r') as f:
    data = f.read()
    regions = json.loads(data)

with open(sys.argv[1], 'r') as stream:
    try:
        cfg = yaml.safe_load(stream)
        
        conf = os.getcwd()+"/conf" 
        result = subprocess.check_output("rm -Rf "+conf+" ; touch "+conf, stderr=subprocess.STDOUT,shell=True)
        installsvclib.print_output(result)

        
        installsvclib.printSection('Creating subnet and security group')
        for region in cfg['regions']:
            node_idx = region['node_idx_start']
            ev = "region=" + region['region'] + \
                 " aws_zone=" + region['zone']+ \
                 " conf=" + conf 

            log_file = "./logs/" + region['region'] + "_config.log"
            key_file = "~/.ssh/" + region['region'] + "-private.pem"

            cmd = create_instance('setupnet.yml',ev,log_file,key_file)
            installsvclib.printLog("On "+ region['zone'] +" ... ",False)
            result = installsvclib.executeCmd(cmd)
            if result>0:
                installsvclib.printLog(" Failed.please readme "+log_file)
            else:
                installsvclib.printLog(' OK')
        

        groups,nets = loadnetconf(conf) 
        
        
        idx = 0
        nodes = {}       

        for group in cfg['node_cfg']:
            nodes[group['id']] = group

        jobs = []
        node_idx = 0 
        details = {}
        for region in cfg['regions']:
            node_idx = region['node_idx_start']
            for node_key in region['node_cluser_list']:
                for inst in nodes[node_key]['instances']:
                    tag = str(node_idx)
                    ev = "region=" + region['region'] + \
                        " aws_zone=" + region['zone'] + \
                        " image=" + cfg['dmi_ids'][region['region']] + \
                        " count=" + str(inst['count']) + \
                        " instance_type=" + inst['instance_type'] + \
                        " volume_size=" + str(inst['volume_size']) + \
                        " mount_point=" + inst['mount_point'] + \
                        " tag=" + tag +"_"+ inst['tag']+ \
                        " group_id=" + groups[region['region']] + \
                        " subnet_id=" + nets[region['region']+'-'+region['zone']]
                    
                    nums = 0
                    if region['region'] in details:
                        nums=details[region['region']]
                    nums = nums + inst['count']
                    details[region['region']]=nums

                    args = {}
                    args['ev'] = ev
                    args['log_file'] = "./logs/" + region['region'] + "_"+str(idx) + ".log"
                    args['key_file'] = "~/.ssh/" + region['region'] + "-private.pem"
                    jobs.append(args)
                    idx = idx + 1
                node_idx = node_idx +1

        commands=[]
        for job in jobs:
            commands.append(create_instance('setuphost.yml',job['ev'], job['log_file'], job['key_file']))
        
        
        installsvclib.printSection('Plan to create hosts on aws')
        for region,num in details.items():
            installsvclib.printLog("Hosts: {} \t\tRegion: {}".format(num,regions[region]))
           
        shname=sys.argv[3]
        createShell(shname,commands,jobs)

    except yaml.YAMLError as exc:
        print(exc)

destpath=sys.argv[2]
result =subprocess.check_output(["mkdir -p "+destpath],shell=True, stderr=subprocess.STDOUT)
installsvclib.print_output(result)


allfilename=sys.argv[1]
result =subprocess.check_output(["cp "+allfilename+" "+destpath+"/instances.yml"],shell=True, stderr=subprocess.STDOUT)
installsvclib.print_output(result)

installsvclib.printSection('Start Create Hosts')