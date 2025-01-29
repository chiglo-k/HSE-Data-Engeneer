#! /bin/bash

# This script will be creating archive for distinct path


echo "Write way to the directory" 

read path

filename = "archive"

if [ -d "$path" ]; then
	zip  -r "$filename" "$path"
else
	echo "You gave not correct way to the directory"
fi 
