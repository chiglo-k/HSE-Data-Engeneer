#!/bin/bash

# Мониторинг системы
OVER_MEM=80

while true; do
	MEMORY=$(free -m | awk 'NR==2{printf "%.2f", $3*100/$2}')
	DISK=$(df -h | awk '$NF=="/"{printf "%s", $5}')
	CPU=$(top -bn1 | grep load | awk '{printf "%.2f", $(NF-2)}')
	
	echo "Memory : $MEMORY%"
	echo "Disk : $DISK"
	echo "CPU: $CPU"
	

	if (( $(echo "$MEMORY > $OVER_MEM" | bc -l) ));then
		echo "Memory almost full!"
	fi

	sleep 5

done

