#!/bin/bash
# $1: 741, 721

echo "Download Avalon Miner$1 firmware"

cd /home/factory/Avalon-extras/scripts/factory

if [ "$1" == "721" ]; then
    wget -c https://canaan.io/downloads/software/avalon7/mm/latest/MM721.mcs -O MM721.mcs.orig && mv MM721.mcs.orig MM721.mcs
    wget -c https://canaan.io/downloads/software/avalon7/pmu/latest/pmu.axf -O pmu721.axf.orig && mv pmu721.axf.orig pmu721.axf
fi

if [ "$1" == "741" ]; then
    wget -c https://canaan.io/downloads/software/avalon741/mm/latest/MM741.mcs -O MM741.mcs.orig && mv MM741.mcs.orig MM741.mcs
    wget -c https://canaan.io/downloads/software/avalon741/pmu/latest/pmu741.axf -O pmu741.axf.orig  && mv pmu741.axf.orig pmu741.axf
fi
