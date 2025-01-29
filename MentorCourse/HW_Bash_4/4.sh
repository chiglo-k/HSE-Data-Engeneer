#!/bin/bash

#5 Полдьзователь предлагает текст --> добавление префикса Holla, запрос 2 цифр , выводится их сумма.

echo "Escribe tu texto: "
read text

string_convert(){
	echo "Holla_$text"
}

echo "$(string_convert), amigo tu necesitas escribir dos numeros: " 

read num_1 num_2

num_positive(){
	result=$((num_1 + num_2))
	echo "$num_1 + $num_2 = $result"
}

num_positive


