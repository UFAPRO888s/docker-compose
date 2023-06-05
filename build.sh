#!/usr/bin/env bash
docker build -t clerous . 
# sudo docker save clerous -o clerous.tar
# docker save clerous | tqdm --bytes --total $(docker image inspect clerous --format='{{.Size}}') > clerous.tar
docker save clerous | (pv -p --timer --rate --bytes > clerous.tar)
now=$(date +"%T")
echo "$now : build done!!"