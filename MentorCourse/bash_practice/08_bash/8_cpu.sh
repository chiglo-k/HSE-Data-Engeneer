#! /bin/bash

# This script will be aware user about high run of disc)

if [ $(df -h | {awk  '$5 > 80') ] ; then
	echo " Warning! Disk is already full !!"
else
	echo " Memory is normal"
fi
