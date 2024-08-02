#!/bin/bash

DIR="$1"

if [ -d "$DIR" ]; then
  echo "Directory $DIR already exists."
else
  mkdir -p "$DIR"
  echo "Directory $DIR created."
fi
