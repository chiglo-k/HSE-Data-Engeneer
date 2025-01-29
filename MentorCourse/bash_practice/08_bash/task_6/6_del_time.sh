#! /bin/bash

cur_date=$(date +%s)

for file in *; do
	if [ -f "$file" ]; then
		date_file=$(stat -c %Y "$file")
		if (( cur_date - date_file > 604800 )); then
			rm -r "$file"
		else
			echo "$file  less than 7 days"
		fi
	else
		echo "$file doesnt exist"
	fi
done

