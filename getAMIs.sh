#!/bin/bash
# This script takes a a parameter which needs to be a name of an AWS AMI
# The string will have to identify the AMI uniquely in all regions.
# The script will then identify the AMI identifier in all common regions (but China)
# The script will generate an output which can be copied into json files of AWS CloudFormation
#
# The script has been tested on Mac OS only
# The script uses the AWS command line tools.
# The AWS command line tools have to have a default profile with the permission to
# describe a region and to describe an image
# The script can be run with normal OS user privileges.
# The script is not supposed to modify anything.
# There is no warranty. Please check the script upfront. You will use it on your own risk
# String to be used when no AMI is available in region
NOAMI="NOT_SUPPORTED"
# Check whether AWS CLI is installed and in search path
if ! aws_loc="$(type -p "aws")" || [ -z "$aws_loc" ]; then
        echo "Error: Script requeres AWS CLI . Install it and retry"
        exit 1
fi
# Check whether parameter has been provided
if [ -z "$1" ]
then
      NAME=ubuntu/images/hvm-ssd/ubuntu-bionic-18.04-amd64-server-20191002
      echo "No parameter provided."
else
     NAME=$1
fi
echo "Will search for AMIs with name: ${NAME}"
echo "---------------------------------------"
##NAME=suse-sles-12-sp3-byos-v20180104-hvm-ssd-x86_64
R=$(aws ec2 describe-regions --query "Regions[].{Name:RegionName}" --output text)
for i in $R; do
  AMI=`aws ec2 describe-images --output text --region $i --filters  "Name=name,Values=${NAME}" | awk -F"\t" '{ print $7;}'i`
  if [ -z "$AMI" ]
  then
    AMI=$NOAMI
  fi
  echo "\"${i}\"        : {\"HVM64\": \"${AMI}\" },"
done
