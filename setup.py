#!/usr/bin/env python3
import sys
import yaml
import subprocess
import multiprocessing
import os
from rich.progress import Progress

def print_output(result):  
  if result!=b'':
    print(result)


def create_instance(ev,logfile, key_file):
    cmds='ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook --vault-password-file '+ os.getcwd()+'/vault -e ansible_python_interpreter=/usr/bin/python3 demo_setup.yml --key-file '+ key_file +' -e "'+ev+'" >'+ logfile +' 2>&1'
    return cmds

def createShell(shfile,commands,jobs):
    with open(shfile, 'w') as f:
        f.write('#!/bin/sh\n')
        f.write('date\n')
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
        f.write('date\n')    

with open(sys.argv[1], 'r') as stream:
    try:
        cfg = yaml.safe_load(stream)
        
        idx = 0
        
        nodes = {}
        
        

        for group in cfg['node_cfg']:
            nodes[group['id']] = group

        jobs = []
        node_idx = 0 

        #if len(sys.argv)==4:
        #    node_idx=int(sys.argv[3])
        
        
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
                        " tag=" + tag +"_"+ inst['tag']
                    
                    args = {}
                    args['ev'] = ev
                    args['log_file'] = "./logs/" + region['region'] + "_"+str(idx) + ".log"
                    args['key_file'] = "~/.ssh/" + region['region'] + "-private.pem"
                    jobs.append(args)
                    idx = idx + 1
                node_idx = node_idx +1

        commands=[]
        for job in jobs:
            commands.append(create_instance(job['ev'], job['log_file'], job['key_file']))
        #print(commands)

        shname=sys.argv[3]
        createShell(shname,commands,jobs)

    except yaml.YAMLError as exc:
        print(exc)

destpath=sys.argv[2]
result =subprocess.check_output(["mkdir -p "+destpath],shell=True, stderr=subprocess.STDOUT)
print_output(result)


allfilename=sys.argv[1]
result =subprocess.check_output(["cp "+allfilename+" "+destpath+"/instances.yml"],shell=True, stderr=subprocess.STDOUT)
print_output(result)