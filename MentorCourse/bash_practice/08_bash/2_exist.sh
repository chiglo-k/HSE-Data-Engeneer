#! /bin/bash

# This  script is checking user's file for existing


echo  "Wright name of file which you want to check: "

read  file

if [ -e "$file" ]; then

	echo "File $file is exist"
else

	echo "File $file  is not exist"
fi
