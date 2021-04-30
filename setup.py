#!/usr/bin/env python3
import yaml
import subprocess
import multiprocessing
import os

def start_instance_wrapper(jobs):
    for job in jobs:
        start_instance(job['ev'], job['log_file'], job['key_file'])

def start_instance(ev, log_file, key_file):
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
            print('Finish job:', ev)
        else:
            print('Job', ev, 'FAILED, see log:', log_file)

with open("instances.yml", 'r') as stream:
    try:
        cfg = yaml.safe_load(stream)
        jobs_list = []
        idx = 0

        tags = {}
        nodes = {}
        for group in cfg['node_cfg']:
            nodes[group['id']] = group
            for inst in group['insts']:
                if inst['tag'] in tags:
                    tags[inst['tag']] = tags[inst['tag']] + 1
                else:
                    tags[inst['tag']] = 1
        repetition = 0
        for tag,num in tags.items():
            if num>1:
                print(' tag [' + tag + '] is reduplicative!')
                repetition = repetition + 1
        if repetition>0:
            raise Exception("found tag is reduplicative!")
        node_idx = 0 
        for region in cfg['regions']:
            for node_key in region['node_list']:
                jobs = []
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
                jobs_list.append(jobs)
                node_idx = node_idx +1

        print(jobs_list)
        pool = multiprocessing.Pool(processes=16)
        pool.map(start_instance_wrapper, jobs_list)
    except yaml.YAMLError as exc:
        print(exc)



