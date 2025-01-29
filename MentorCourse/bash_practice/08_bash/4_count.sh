#! /bin/bash

# Count words


echo "Write you word: "

read word

if [ -n "$word" ]; then
	wc -m <<<  "$word"
else
	echo "  $word contains 0 words"

fi
 
