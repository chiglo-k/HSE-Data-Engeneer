#!/bin/bash

#1 Вывод текущего пути, добавление нового

PATH=$(pwd)

echo "PATH: $PATH"

NEW_DIR="$Desktop/new_destination"

export PATH=$PATH:$NEW_DIR

echo "New Dir $PATH"

#2
# Изменения временные, из-за того что они инициализируются в "текущей" сессии оболочки.
# Для постоянных изменений следует произвести переконфигурацию .bashrc
