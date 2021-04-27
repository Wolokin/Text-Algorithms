#!/bin/bash

base64 /dev/urandom | head -c "$1"000 > uniform$1kB.txt
