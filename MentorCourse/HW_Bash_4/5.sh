#!/bin/bash

#5  Три команды sleep --> jobs, fg, bg
set -m
counter=3
while [ $counter -gt 0 ]; do
	sleep $((counter * 2)) &
	counter=$((counter -1))
done

echo "Jobs"
jobs 

echo "fg"
fg 

echo "bg"
bg 
