# How to Configure AWS Instances

- [How to Configure AWS Instances](#how-to-configure-aws-instances)
  - [1. Dynamic Testnet](#1-dynamic-testnet)
    - [1.1. Pros](#11-pros)
    - [1.2. Cons](#12-cons)
  - [2. testnet.json](#2-testnetjson)
    - [2.1. Example for testnet.json](#21-example-for-testnetjson)
      - [2.1.1. Regions and Zones](#211-regions-and-zones)
      - [2.1.2. node_cfg](#212-node_cfg)
      - [2.1.3. Instance Configuration](#213-instance-configuration)
    - [2.2. Anther Example](#22-anther-example)
  
Arcology is a complex system with a lot of moving parts. It has a number of services and these services have to communicate asynchronously with other internal services and external peers via network connections. Basically, an Arcology tesnet is a network of networks.

## 1. Dynamic Testnet

An Arcology testnet usually involves in multiple machines, setting them up one by one manually is impractical sometimes. Therefore, Arcology testnet installer comes with tools to start a testnet on AWS **dynamically** on-demand.

The installer scripts will take care of everything for the most part. The overall process is pretty automatic. But there are still a few configuration files user need to edit based on their own settings.

### 1.1. Pros

A dynamic testnet has a number of benefits:

- **Reduced cost:** AWS charges an hourly rate based on the number of active instance. Maintaining a on-demand only testnet will minimize the cost.

- **Flexibility:**  User can easily update the testnet verions or switch to different configurations in minutes.

### 1.2. Cons

There is a steep learning curve. Starting a dynamic testnet requires the ablities to deal with all the factors programmatically. In the process of starting a new testnet, all the instances need to be recreated, and these new instances will have new IP addresses.

Instead of hardcoding the IP addresses directly into the installation scripts, there are tools to programmatically extract the instance information from AWS and then write it into the configuration file for installer to use. That is why we wrote some scripts to help with the whole process.

## 2. testnet.json

The testnet.json is the first one we need to edit. The testnet.yml helping the installer to find out the relationship between different machines and services AWS. The testnet is started dynamically, which means everytime we start a new testnet the machines will be different, so are their IPs. Thus we cannot simply write the IP inforamtion into a configuration file, we need to get it on the fly.

What we can do is to specify the instance types and the what Arcology services need to install and then let AWS to assign the hosts. The testnet.json tells the relationship between instance types and the services.

### 2.1. Example for testnet.json

The sample configuration starts a testnet with two Arcology node clusters hosted in two AWS data center.  

```yml
dmi_ids:                                                              # AWS data centers
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
regions:                                                
  - region: us-east-2                                                  # Where the testnet will be hosted
    zone: us-east-2a                                       
    node_cluster_list: [min]                                           # node cluster type to creates    
node_cfg:                                                              # Configuration type      
  - id: min                                 
    instances: 
      - count: 1                                
        instance_type: r5.xlarge
        volume_size: 100
        mount_point: /data
        services: ammolite-docker                                            # Install the ammolite-docker on this host
      - count: 1                                                        # Create on host machine
        instance_type: r5.2xlarge                                       # Host machine type
        volume_size: 20                                                 # 20G of extra storage space
        mount_point: /data                                              # storage folder  
        services: core-svc_eshing-svc_generic-hashing-svc_ppt-svc_client-svc # Services to install
      - count: 1
        instance_type: r5.2xlarge
        volume_size: 100
        mount_point: /data
        services: exec-svc_consensus-svc_arbitrator-svc_ppt-svc_client-svc
      - count: 1
        instance_type: r5.4xlarge
        volume_size: 500
        mount_point: /data
        services: kafka0_storage-svc_pool-svc_exec-svc_scheduling-svc_frontend-svc
  - id: large
     instances: 
      - count: 1
        instance_type: r5.xlarge
        volume_size: 100
        mount_point: /data
        services: ammolite-docker
      - count: 1
        instance_type: r5.2xlarge
        volume_size: 20
        mount_point: /data
        services: eshing-svc_generic-hashing-svc_ppt-svc_client-svc
      - count: 1
        instance_type: r5.2xlarge
        volume_size: 20
        mount_point: /data
        services: core-svc_consensus-svc_pool-svc_exec-svc
      - count: 1
        instance_type: r5.2xlarge
        volume_size: 100
        mount_point: /data
        services: exec-svc_arbitrator-svc_ppt-svc_client-svc
      - count: 1
        instance_type: r5.4xlarge
        volume_size: 500
        mount_point: /data
        services: kafka0_storage-svc_scheduling-svc_frontend-svc
```

#### 2.1.1. Regions and Zones

Users needs to specify the data centers where the testnet will be hosted. There can be multiple data center involved.
Apart from the data center, users also need to indicate what the of node cluster they want in the node_cluster_list field,
which is defined in the section below. Users can deploy any number of node clusters.

```yml
  - region: us-east-2                                  
    zone: us-east-2a                                       
    node_list: [min]                                   
```

The configuraiton above bascially tells the installer to create a "min" cluster in the us-east-2 data center. The "min" is defined in the in section `id:min` below. We can add more to the node_cluster_list attribute. 

For example, we can have `node_list: [min, min, min, min]` to create 4 "min" clusters in the same data center.

#### 2.1.2. node_cfg

The node_cfg section contains the hardware configuration for each cluster type what services users want to install.

Usually there will be multiple hosts in each cluster for better performance. The section below defines a cluster type called "min", which has 4 instances and lists of services to install.

```yml
- id: min                                                                 # Cluster Type 
instances: 
      - count: 1                                
        instance_type: r5.xlarge
        volume_size: 100
        mount_point: /data
        services: [ammolite-docker]                                              # Install the ammolite-docker on this host
      - count: 1                                                          # Create on host machine
        instance_type: r5.2xlarge                                         # Host machine type
        volume_size: 20                                                   # 20G of extra storage space
        mount_point: /data                                                # storage folder  
        services: [core-svc,eshing-svc,generic-hashing-svc,ppt-svc,client-svc] # A list of services to install 
      - count: 1
        instance_type: r5.2xlarge
        volume_size: 100
        mount_point: /data
        services: [exec-svc,consensus-svc,rbitrator-svc,ppt-svc,client-svc]
      - count: 1
        instance_type: r5.4xlarge
        volume_size: 500
        mount_point: /data
        services: [kafka0,storage-svc,pool-svc,exec-svc,scheduling-svc,frontend-svc]
```

#### 2.1.3. Instance Configuration

There is not limit on the number of hosts we can have but, but we still need at least on instance for all these services.

```yml
  - count: 1                    # The Number of host
    instance_type: r5.xlarge    # Instance type
    volume_size: 100            # Extra storage space
    mount_point: /data          # Storage folder location   
    services: ammolite-docker        # Install a Ammolite docker image on the machine
 ```

Bascially, what it says is to start a [r5.xlarge](https://aws.amazon.com/ec2/instance-types/r5/) instance with 100G of extra storage space mounted under /data folder and then install the [ammolite-docker](https://github.com/arcology-network/ammolite) on it.

### 2.2. Anther Example

It is perfectly possible to run everything on a single machine. The configuration file below starts a single host cluster with all the services deployed on one machine.

```yml
dmi_ids:                                                              # AWS data centers
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
regions:                                                
  - region: us-east-2                                                  # Where the testnet will be hosted
    zone: us-east-2a                                       
    node_cluster_list: [all-in-one ]                                   # node cluster type to creates   
node_cfg:                                                              # Configuration type      
  - id: all-in-one                                 
    instances: 
      - count: 1                                
        instance_type: r5.xlarge
        volume_size: 500
        mount_point: /data
        services:  [exec-svc,consensus-svc,rbitrator-svc,ppt-svc,client-svc,kafka0,storage-svc,pool-svc,exec-svc,scheduling-svc,frontend-svc,core-svc,eshing-svc,generic-hashing-svc,ppt-svc,client-svc]   # All the services
