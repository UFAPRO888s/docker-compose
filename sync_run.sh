#!/usr/bin/env bash
sshpass -p "1234" rsync -r -v -P -t -h --delete --progress -e "ssh -p 22" ./*.sh  root@clerous.local:/large_tmp
sshpass -p "1234" rsync -r -v -P -t -h --delete --progress -e "ssh -p 22" ./app  root@clerous.local:/opt
sshpass -p "1234" ssh root@clerous.local "docker restart clerous"