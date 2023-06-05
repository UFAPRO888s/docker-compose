#!/usr/bin/env bash
./build.sh
# rsync -r -t -p -o -g -v --progress --delete -c -l -H -s /media/khing/Data/workspace/clerous-app /mnt/k_nas/workspace
# ssh root@clerous.local "cd /mnt/workspace/clerous-app && ./deploy.sh"
# scp clerous.tar root@clerous.local:/tmp
sshpass -p "1234" ssh root@clerous.local "mkdir -p /large_tmp"
# sshpass -p "1234" scp -v ./{deploy.sh,clerous.tar} root@clerous.local:/large_tmp
sshpass -p "1234" rsync -r -v -P -t -h --progress --delete -e "ssh -p 22" ./*.tar  root@clerous.local:/large_tmp
sshpass -p "1234" rsync -r -v -P -t -h --progress --delete -e "ssh -p 22" ./*.sh  root@clerous.local:/large_tmp
sshpass -p "1234" rsync -r -v -P -t -h --progress --delete -e "ssh -p 22" ./app  root@clerous.local:/opt

sshpass -p "1234" ssh root@clerous.local "cd /large_tmp && ./deploy.sh"
echo "deployed the app"
