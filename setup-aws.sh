#!/bin/bash
while getopts i:t:s:b:p:q: OPT; do
 case ${OPT} in
  i) instancecfg=${OPTARG}
    ;;
  t) testnetcfg=${OPTARG}
    ;;
  s) servicescfg=${OPTARG}
    ;;
  b) backpath=${OPTARG}
    ;;
  p) plugs=${OPTARG}
    ;;
  q) spot=${OPTARG}
    ;;
  \?)
    printf "[Usage] `date '+%F %T'` -i <instancecfg> -t <testnetcfg> -s <servicescfg> -b <backpath> -p <plugs> -q <spot>\n" >&2
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
    python add-tag.py host.json
fi

echo '3.Get Testnet Configuration'
python3 gentestnet.py host.json ${testnetcfg}  ${servicescfg} ${backpath}
