set -eo pipefail
cd "$(dirname "$0")"
names=(x "Theme-Song-Story" "Bath-Time-Song" "Hedgehogs-Sleep-in-the-Day")
for n in 1 2 3; do
  SHORT=$n python3 rshorts2.py full "$PWD/Short-v2-$n-${names[$n]}.mp4" > render_short$n.log 2>&1
  echo "short $n done"
done
