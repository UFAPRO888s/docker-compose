#!/bin/sh
cp -f nginx/* /etc/nginx/
echo "starting server"
nginx -g 'daemon off;' &
mkdir -p /var/run/sshd
echo 'root:1234' | chpasswd
sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
service ssh restart
echo "starting stream"
# mount -t tmpfs -o size=128m tmpfs /streaming
cd /streaming
mkdir -p tmp
# ffmpeg -ar 8000 -f alsa -i hw:0 -acodec aac -b:a 96k -strict -2 -ac 2 -ab 32k -ar 44100 -f mpegts udp://127.0.0.1:1235?pkt_size=1316 2> sound_rtp.log &
# ffmpeg -i udp://@:1235 -acodec copy output.m4a


ffmpeg \
    -nostdin \
    -f video4linux2 \
    -i /dev/video1 \
    -preset ultrafast \
    -s 1280x720 \
    -r 10 \
    -vcodec libx264 \
    -preset ultrafast \
    -tune zerolatency \
    -x264-params keyint=5:min-keyint=5 \
    -b:v 512k \
    -f mpegts udp://127.0.0.1:1234 2> vid_udp.log &
ffmpeg \
    -nostdin\
    -i udp://@:1234?fifo_size=5000000 \
    -c:v libx264 \
    -b:v 1024k \
    -preset ultrafast \
    -tune zerolatency \
    -x264-params keyint=5:min-keyint=5 \
    -f dash \
    -ldash 1 \
    -seg_duration 1 \
    -frag_duration 1 \
    -streaming 1 \
    -window_size 3 \
    -remove_at_exit 1 \
    -hls_playlist 1 \
    live.mpd 2> vid_dash.log &
echo "starting app server"

cd /app
ls -al
# python3 main.py
python3 spinner.py "./app_code"
# uvicorn main:app --host 0.0.0.0 --port 80
now=$(date +"%T")
echo "$now : quit streaming"
read -p "Press [Enter] key to exit..."
echo "$now : done!"