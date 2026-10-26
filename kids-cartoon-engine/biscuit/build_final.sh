set -eo pipefail
cd "$(dirname "$0")"
names=(x "Theme-Song-Story" "Bath-Time-Song" "Hedgehogs-Sleep-in-the-Day")
for n in 1 2 3; do
  SHORT=$n python3 rshorts2.py full "$PWD/Short-v2-$n-${names[$n]}.mp4" > rs$n.log 2>&1; echo "short $n done"
done
for E in 1 2 3; do
  M=show; [ $E -gt 1 ] && M=show$E
  SHOW=$M python3 render.py full $PWD/Biscuit-and-Friends-Ep$E-final.mp4 > render_ep$E.log 2>&1; echo "ep$E done"
done
printf "file '%s'\n" $PWD/Biscuit-and-Friends-Ep1-final.mp4 $PWD/Biscuit-and-Friends-Ep2-final.mp4 $PWD/Biscuit-and-Friends-Ep3-final.mp4 > comp.txt
ffmpeg -v error -y -f concat -safe 0 -i comp.txt -c:v copy -c:a aac -b:a 192k -movflags +faststart $PWD/Biscuit-and-Friends-Compilation-1-final.mp4
echo "compilation done"
