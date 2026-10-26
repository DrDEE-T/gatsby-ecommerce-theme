set -eo pipefail
cd "$(dirname "$0")"
names=(x "Prickles-Sticky-Spikes" "Bath-Time-Song" "Hedgehogs-Sleep-in-the-Day")
for n in 1 2 3; do
  SHORT=$n python3 rshorts.py full "$PWD/Short-$n-${names[$n]}.mp4" > render_short$n.log 2>&1
  echo "short $n done"
done
