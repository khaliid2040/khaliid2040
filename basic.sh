#!/bin/bash
#creating backup script

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'
YELLOW='\033[0;33m'
echo "${YELLOW}file automatic remover"
create_file() {
    if ! find -name "file*" -type f | grep -q .;
    then
        echo "files don't exist, creating files..."
        sleep 2
        touch file{1..10}

    else 
        echo -e "${RED}files already exist${NC}."
    fi
}
create_file
if find -name "file*" -type f | grep -q .;
then
    #$files=$(ls file*)
    echo "creating archives...."
    for file in file* 
    do
        tar -cf $file.tar $file &>/dev/null && rm file*
    done
    echo -e "${GREEN}created successful"
else
    echo -e "${RED}failed files doesn't exist${NC}."
fi