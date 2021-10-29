#!/bin/bash
sudo docker start worker-container
sudo docker exec worker-container /bin/sh -c "rm -rf /input"
sudo docker exec worker-container /bin/sh -c "rm -rf /output"
sudo docker cp /input/. worker-container:/input
sudo docker exec worker-container /bin/sh -c "mkdir /output"
sudo rm -rf /output
sudo mkdir /output
sudo chmod -R 777 /output
echo $(date -u) >>/output/start.log
sudo docker exec worker-container /bin/sh -c "/run.sh"
echo $(date -u) >>/output/end.log
sudo docker cp worker-container:/output/. /output/
