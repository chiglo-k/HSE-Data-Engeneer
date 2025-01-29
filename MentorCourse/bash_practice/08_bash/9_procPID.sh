#! /bin/bash


echo  "Write command, which you want to start: "

read comm

echo "$(pgrep -f "$comm")"
