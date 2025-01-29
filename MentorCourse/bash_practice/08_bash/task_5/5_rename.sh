#! /bin/bash

# Rename prefix in files to  backup_

touch file{1..5}.txt

files=(file{1..5}.txt)

for file in "${files[@]}"; do
	mv "$file" "backup_$file"
done 
