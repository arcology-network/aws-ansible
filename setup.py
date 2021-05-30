#!/usr/bin/env python3
import sys
import yaml
import subprocess
import multiprocessing
import os
from rich.progress import Progress


def start_instance_wrapper(jobs,progress,task):
    for job in jobs:
        start_instance(job['ev'], job['log_file'], job['key_file'],progress,task)

def start_instance(ev, log_file, key_file,progress,task):
    with open(log_file, 'w+') as out:
        args = ['/usr/bin/ansible-playbook', 
                '--vault-password-file', os.getcwd()+'/vault',
                '-e', 'ansible_python_interpreter=/usr/bin/python3',
                'demo_setup.yml',
                '--key-file', key_file,
                '-e', ev]
                
        rv  = subprocess.call(
                args, env={'ANSIBLE_HOST_KEY_CHECKING':'false'}, 
                stdout=out, stderr=out)
        
        
        if rv == 0:
            print('Instance created:', ev)
        else:
            print('Instance ', ev, 'FAILED, see log:', log_file)
        progress.update(task, advance=1)

with open(sys.argv[1], 'r') as stream:
    try:
        cfg = yaml.safe_load(stream)
        
        idx = 0
        
        tags = {}
        nodes = {}
        
        

        for group in cfg['node_cfg']:
            nodes[group['id']] = group

        jobs = []
        node_idx = 0 
        for region in cfg['regions']:
            for node_key in region['node_list']:
                
                for inst in nodes[node_key]['insts']:
                    ev = "region=" + region['region'] + \
                        " aws_zone=" + region['zone'] + \
                        " image=" + cfg['dmi_ids'][region['region']] + \
                        " count=" + str(inst['count']) + \
                        " instance_type=" + inst['instance_type'] + \
                        " volume_size=" + str(inst['volume_size']) + \
                        " mount_point=" + inst['mount_point'] + \
                        " tag=" + str(node_idx) + '_' +inst['tag']
                    args = {}
                    args['ev'] = ev
                    args['log_file'] = "./logs/" + region['region'] + "_"+str(idx) + ".log"
                    args['key_file'] = "~/.ssh/" + region['region'] + "-private.pem"
                    jobs.append(args)
                    idx = idx + 1
                node_idx = node_idx +1

        with Progress() as progress:
            task = progress.add_task("Creating instances ...", total=len(jobs))

            for job in jobs:
                start_instance(job['ev'], job['log_file'], job['key_file'],progress,task)
    except yaml.YAMLError as exc:
        print(exc)



