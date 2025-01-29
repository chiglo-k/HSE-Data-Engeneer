# /bin/bash

echo "Write 1st num: "

read num1

echo "Write 2nd num: "

read num2

if [ "$num1" -gt "$num2" ]; then
	echo "$num1 gt than $num2"
elif [ "$num1" -eq "$num2" ]; then
	echo "$num1 is eq $num2"
else
	echo "$num1 less than $num2"
fi
