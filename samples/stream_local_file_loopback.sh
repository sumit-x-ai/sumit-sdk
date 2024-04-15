#sudo modprobe snd-aloop
fn=$1
date "+%s"
ffmpeg -re -i $1 -f alsa -ac 1 -ar 16000 -acodec pcm_s16le hw:Loopback
# ffmpeg -re -i $1 -f alsa -ac 2 -ar 44100 -b:a 128k -bufsize 128k -acodec pcm_s16le hw:Loopback,1,0
