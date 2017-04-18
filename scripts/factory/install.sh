#!/bin/bash
cd ~
git clone https://github.com/Canaan-Creative/Avalon-extras.git && \
    cd Avalon-extras && \
    mkdir -p /home/factory/Desktop && \
    cp ./scripts/factory/desktop/* /home/factory/Desktop/
echo "Install finish"
