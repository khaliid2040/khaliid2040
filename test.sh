#!/bin/bash
# Creating backup script
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

create_file() {
    if ! find -name "file*" -type f | grep -q .; then
        echo "Files don't exist, creating files..."
        sleep 2
        touch file{1..10}
    else
        echo -e "${RED}Files already exist.${NC}"
    fi
}

create_file

if find -name "file*" -type f | grep -q .; then
    echo "Creating archives..."
    for file in file*; do
        tar -cf "$file.tar" "$file" &>/dev/null
    done
    echo -e "${GREEN}Archives created successfully.${NC}"
else
    echo -e "${RED}Failed: Files don't exist.${NC}"
fi