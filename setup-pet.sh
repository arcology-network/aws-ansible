#!/bin/bash
while getopts i:h:b:q: OPT; do
 case ${OPT} in
  i) instancecfg=${OPTARG}
    ;;
  h) hostcfg=${OPTARG}
    ;;
  b) backpath=${OPTARG}
    ;;
  q) spot=${OPTARG}
    ;;
  \?)
    printf "[Usage] `date '+%F %T'` -i <instancecfg> -h <hostcfg> -b <backpath> -q <spot>\n" >&2
    exit 1
 esac
done


if [[ ${spot} == 'true' ]]
then
    echo '1.Create EC2 Instances Skip'
else
    echo '1.Create EC2 Instances'
    python setup.py ${instancecfg} ${backpath} she
    chmod 755 she
    ./she
fi

echo '2.Get EC2 Instances'
python ec2.py > host.json

if [[ ${spot} == 'true' ]]
then
    echo '2.1.Add Tag'
    python add-tag-pet.py host.json
fi

echo '3.Get host Configuration'
python3 genhosts.py host.json ubuntu ${hostcfg}
