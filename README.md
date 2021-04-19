# aws-ansible

The tools and libraries to start hosting machines on aws cloud.

## 1. **Preparation**

### 1.1. AWS Preperation

* Create an AWS account;
* Create new user with permission policy **AmazonEC2FullAccess**；
* Create access key；
* Save access key in secret.yml in the same directory as the other scripts like this：

```yaml
ec2_access_key: THISISYOURACCESSKEY
ec2_secret_key: ThisIsYourSecretKey
```

### 1.2. Setup Client Environment

* Install python3 and pip;
* Install ansible;
* Use pip to install ansible, boto and boto3 python libraries;
* Install awscli and login with your AWS account;
* Use ansible-vault to encrypt your secret.yml, save your vault's password in a file named **vault** in the same directory as the other scripts.

### 1.3. Installation Process

![alt text](img/installation-process.svg)

## 2. **Create EC2 Instances**

Currently AWS imposes a limit on number of vCPU for On-Demand instances, so you may need to request limit increase.  

### 2.1. Edit instances.yml

```yaml
---
# The AWS OS images lookup table. In different regions, the same OS images use different DMI IDs. The current OS version we used is Ubuntu 20.04.
dmi_ids:
    eu-north-1: ami-04ec5f55f21fa091e 
    ap-south-1: ami-02240fe5e8581a077
    eu-west-3: ami-0f8e5edde3a79f541
    eu-west-2: ami-0a5c9ebccc5a914b4
    eu-west-1: ami-068064aad57b179f3
    ap-northeast-2: ami-048d434559cc26206
    ap-northeast-1: ami-04297bd23c488ac2d
    sa-east-1: ami-0af5bbfe9a9157cfb
    ca-central-1: ami-0a21034f235f66ffd
    ap-southeast-1: ami-0e0436d1fd18d1122
    ap-southeast-2: ami-0ea7af759a98f50c1
    eu-central-1: ami-0a09486b18ca1a617
    us-east-1: ami-0745d55d209ff6afd
    us-east-2: ami-08541d54d54812a51
    us-west-1: ami-0713bfb5ea0df48be
    us-west-2: ami-01f398167e3bba7a0
# The regions section is used to configure the Monaco node list. The following configuration means create a single node Monaco network which is located in region ap-northeast-1, zone ap-northeast-1a. The available regions and zones can be found on AWS website. If more than one node was needed, add more items under the regions section will do.
# IMPORTANT NOTICE: before setup the EC2 instances, make sure the private key of certain region had been generated on AWS and stored under the ~/.ssh/ directory. The private key should be named as <region>-private.pem. Eg. The private key of region ap-northeast-1 should be saved in file ~/.ssh/ap-nrotheast-1-private.pem. The setup scripts assumes that the private key file had been placed according to this rule.
regions:
  - region: ap-northeast-1
    zone: ap-northeast-1a
    #- region: us-east-2
    #  zone: us-east-2a
    #- region: us-east-2
    #  zone: us-east-2b
    #- region: us-west-1
    #  zone: us-west-1a
# The node_cfg section is used to configure the machines within one Monaco node. 
node_cfg:
  - count: 1                 # Count of this type of machine(s).
    instance_type: r5.xlarge # Type of the EC2 instance(s).
    volume_size: 10          # Size of the data volume (in GB).
    mount_point: /data       # The mount point of the data volume.
    tag: ammolite            # The service(s) run on this type of machine(s).
  - count: 3
    instance_type: r5.xlarge
    volume_size: 20
    mount_point: /data
    tag: ppt-svc_client-svc
  - count: 1
    instance_type: r5.2xlarge
    volume_size: 20
    mount_point: /data
    tag: core-svc_eshing-svc
  - count: 4
    instance_type: r5.2xlarge
    volume_size: 20
    mount_point: /data
    tag: exec-svc
  - count: 1
    instance_type: r5.2xlarge
    volume_size: 500
    mount_point: /data
    tag: kafka2
  - count: 1
    instance_type: r5.2xlarge
    volume_size: 20
    mount_point: /data
    tag: pool-svc
  - count: 1
    instance_type: r5.2xlarge
    volume_size: 500
    mount_point: /data
    tag: kafka1
  - count: 1
    instance_type: r5.2xlarge
    volume_size: 500
    mount_point: /data
    tag: consensus-svc_exec-svc
  - count: 1
    instance_type: r5.4xlarge
    volume_size: 20
    mount_point: /data
    tag: storage-svc
  - count: 1
    instance_type: r5.2xlarge
    volume_size: 20
    mount_point: /data
    tag: arbitrator-svc_generic-hashing-svc
  - count: 1
    instance_type: r5.2xlarge
    volume_size: 20
    mount_point: /data
    tag: scheduling-svc_frontend-svcs
```

### 2.2. Create EC2 Instances with setup.py

Run setup.py to create EC2 instances according to the configuration info in instances.yml.

```shell
$ setup.py
```

### 2.3. Get List of EC2 Instance

After running setup.py successfully, use ec2.py to get the information of all the EC2 instances. Output the information to host.json, this file will be used in the following installation scripts.

```shell
$ ec2.py > host.json
```

## 3. **Setup Basic Runtime Environment**

use genhosts.py create configuration file for setup basic runtime environment.

```shell
$ python3 genhosts.py host.json ubuntu ../env/envs
```

> Extract Login info ?

- ubuntu        ---  login account name
- ../env/envs  --- configuration file
> envs => loginInfo.txt

run script to setup basic runtime environment

```shell
$ cd ../env
$ ansible-playbook -i envs install.yml
```

## 4. **Install and Start the Testnet**

use genhosts.py create configuration file for setup testnet.

```shell
$ python3 gentestnet.py host.json ubuntu ../cluster/testnet.json 50000 testnet 2 4 /data
```

- ubuntu                                ---  login account name
- ../cluster/testnet.json       --- configuration file
- 50000                                  --- max txs of per block
- 2                                           --- node nums of cluster
- 4                                           --- concurrency
- /data                                    --- remote path
> What is the remote path ?

```shell
$ cd ../cluster
$ python3 svcsInstaller.py restart testnet.json 4 5000000 -sshkey 
```

