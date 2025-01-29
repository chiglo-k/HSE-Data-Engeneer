#! /bin/bash

echo "What password lenght do you need?: "

read num_pass

password=$(apg -a 0 -M NL -m "$num_pass" -x "$num_pass")

echo ""$password""

