#!/bin/sh
# Experiment 1: compare host vs. a process in fresh pid/mnt/uts/net/ipc namespaces
echo "HOST"; echo "pid=$$ host=$(hostname)"; ls -l /proc/self/ns | awk 'NR>1{print $9,$11}'
echo "CONTAINER"
unshare --pid --fork --mount-proc --uts --net --ipc --mount sh -c \
 'hostname lab-container; echo "pid=$$ host=$(hostname)"; ls -l /proc/self/ns | awk "NR>1{print \$9,\$11}"; ps -e -o pid,ppid,comm; cut -d: -f1 /proc/net/dev | tail -n +3'
