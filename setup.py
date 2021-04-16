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
        for region in cfg['regions']:
            jobs = []
            for inst in cfg['node_cfg']:
                ev = "region=" + region['region'] + \
                    " aws_zone=" + region['zone'] + \
                    " image=" + cfg['dmi_ids'][region['region']] + \
                    " count=" + str(inst['count']) + \
                    " instance_type=" + inst['instance_type'] + \
                    " volume_size=" + str(inst['volume_size']) + \
                    " mount_point=" + inst['mount_point'] + \
                    " tag=" + inst['tag']
                args = {}
                args['ev'] = ev
                args['log_file'] = "./logs/" + region['region'] + "_"+str(idx) + ".log"
                args['key_file'] = "~/.ssh/" + region['region'] + "-private.pem"
                jobs.append(args)
                idx = idx + 1
            jobs_list.append(jobs)
        print(jobs_list)
        pool = multiprocessing.Pool(processes=16)
        pool.map(start_instance_wrapper, jobs_list)
    except yaml.YAMLError as exc:
        print(exc)



