#!/bin/bash
# Те же параметры, что использовались при кодировании
BLOCK_SIZE=16
FRAME_WIDTH_MP4=2000
FRAME_HEIGHT_MP4=2000
FRAME_WIDTH=$(echo "${FRAME_WIDTH}/${BLOCK_SIZE}" | bc)
FRAME_HEIGHT=$(echo "${FRAME_HEIGHT}/${BLOCK_SIZE}" | bc)
MP4_HZ=60
MP4_FPS=60

ffmpeg -y -i "./tech_demo.mp4" -r ${MP4_FPS} -f rawvideo -pix_fmt monob -vf "scale=iw/${BLOCK_SIZE}:ih/${BLOCK_SIZE}" -video_size ${FRAME_WIDTH}x${FRAME_HEIGHT} -sws_flags neighbor -r ${MP4_HZ} pipe:1 | xz -d --stdout > outputfile
