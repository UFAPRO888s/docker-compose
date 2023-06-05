#!/usr/bin/env bash
docker stop clerous
docker rm clerous
docker rmi clerous
docker load -i clerous.tar
docker run -d \
    --name=clerous \
    --device=/dev/video1 \
    --device /dev/snd \
    --device /dev/i2c-0 \
    --device /dev/gpiomem \
    --mount type=bind,source=/opt/app,target=/app \
    --mount type=tmpfs,destination=/streaming \
    --restart=always \
    -p 8080:8080 -p 80:80 -p 2222:22 -p 4000:4000 \
    --privileged \
    clerous
