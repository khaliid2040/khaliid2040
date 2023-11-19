#!/bin/bash
#creating files
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'
YELLOW='\033[0;33m'
check_arg() {
    if [ $# -ne 2 ]
    then
        echo -e "${RED}[-]${NC} missing required positional argements. $#"
        exit 2
    else
        echo "test..."
    fi
}
create_file() {
    if ! find -name "file*" -type f | grep -q .
    then
        echo -e "${GREEN}[+]${NC}creating files..."
        sleep 1
        touch file{1..10}
        #archiving files
        echo -e "${GREEN}[+]${NC}archiving files..."
        files=$(ls file*)
        for file in $files; do
        sleep 1
        tar -cf $file.tar $file && rm $file
        done
    else
        echo -e "${RED}[-]${NC}files already exist"
    fi
}
create_file
echo -e "${GREEN}[+]${NC}archive successuful"
#backing up
source_dir=$1
dest_dir=$2
echo -e "${GREEN}[+]${NC} backing up from $source_dir to $dest_dir"
if [ -f $source_dir ] && [ -d $dest_dir ] #|| [ -d $source_dir ] && [ -f $dest_dir ]
then
    echo -e "${GREEN}[+]${NC}backuping up"
    sleep 1
    mv $source_dir $dest_dir 2>/dev/null
else
    echo -e "${RED}[-]${NC}something gone wrong..."
    check_arg
fi