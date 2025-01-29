#! /bin/bash

# User write his name and age, the output shows text greetings

echo "Please enter your name and age: "

read name age

echo "Hello, $name! After one year you will be $(($age + 1))  age old"
