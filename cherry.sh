#!/bin/bash

set -eu

if [ $# != 2 ]; then
    echo "USAGE: $(basename $0) <file> <number>"
    exit 1
fi

args=("$@")
filename=${args[0]}
lineno=${args[1]}

git cherry-pick $(sed ${lineno}\!d $filename)
