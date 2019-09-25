#!/bin/bash
while IFS= read -r line; do
    ./parse_ea_task.py "$line"
done < "$1"

