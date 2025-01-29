#!/bin/bash

for file in *; do
    if [[ -f "$file" ]]; then
        new_name=$(echo "$file" | tr '[:upper:]' '[:lower:]')
        mv "$file" "$new_name"
    fi
done
