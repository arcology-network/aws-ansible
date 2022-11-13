# aws-ansible

The tools and libraries to set up hosting instances on aws cloud.

## 1. Preparation

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

### 1.3. Installation Workflow

![alt text](img/aws.png)

## 2. Create EC2 Instances

>Currently AWS imposes a limit on maximum number of vCPU for On-Demand instances, so you may need to request limit increase.  

### 2.1. Edit instances.yml

The instances.yml contains region and type information regrading hosting instances on AWS.

If EC2 Instances have created by spot,we could skip this step. 

### 2.2.Edit services.json 

The services.json contains services and logic module information per host.

### 2.3. Create EC2 Instances and testnet  Configuration

Create EC2 instances according to the configuration info in instances.yml,or use spot instances by manually created to create testnet.json according to the configuration info in service.json.

```shell
$ ./setup-aws.sh -i instances-1.7.yml -t ../cluster/testnet.json  -s service.json -b ../bak -q true
```

| Field              | Description           |
| ------------------ | --------------------- |
| i      | instances configure file       |
| t             | testnet configuration file |
| s | service configuration file |
| b | tmp path  for bak |
| q | spot mode |

