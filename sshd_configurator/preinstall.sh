#!/bin/bash

set -e

NEED_INSTALL="openssh-server python3 python3-tk"

if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo or as root" >&2
    exit 1
fi


apt update -qq
apt install -y ${NEED_INSTALL}

echo "Successfully installed: $NEED_INSTALL"