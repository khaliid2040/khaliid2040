#!/bin/bash
counter=10
echo "enter number: $1"
while [ $counter -ge $1 ]; do
echo $counter
((counter -= 1))
done