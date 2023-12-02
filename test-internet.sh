#!/bin/bash
RED='\033[0;31m'
NC='\033[0m'
YELLOW='\033[0;33m'
time=$(date)
echo -e "${YELLOW}report for $time.${NC}" &>> /home/khaalid/Documents/report.txt 
/usr/bin/speedtest-cli &>> /home/khaalid/Documents/report.txt
if [ $? -ne 0 ]
then
	echo -e "${RED}there was an error."
fi
