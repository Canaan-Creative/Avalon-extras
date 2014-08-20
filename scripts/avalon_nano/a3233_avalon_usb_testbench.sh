#!/bin/bash 

DELAY=0
DEVICE=/dev/ttyACM0
RUNTIMES=100
ERRORTIMES=0
RUNCOUNTS=0

if [ "$1" == "--help" ]; then
    echo "\

Usage: $0 [--help] 

     --help             Display help message
You can choose your test device and run times through params, 
eg:$0 device[default:/dev/ttyACM0] times[default:100]
Without any parameter it will use /dev/ttyACM0 and run 100 times 

Written by: Mikeqin <Fengling.Qin@gmail.com>"
    exit 0
fi

[ -n "$1" -a -c "$1" ] && DEVICE=$1
[ ! -z "${2##*[!0-9]*}" ] && RUNTIMES=$2
echo "Choose dev:$DEVICE,Runtimes:$RUNTIMES"

for i in `seq 1 $RUNTIMES`
do
    echo "==== $i ===="
    ./a3233_avalon_usb_test.py -d d8f8ef6712146495c44192c07145fd6d974bf4bb8f41371d65c90d1e9cb18a170000000000000000000000000000000000000000087e051a885170504ac1d001 -n 010f0eb6 -s $DEVICE
    ERRORTIMES=$((ERRORTIMES+$?))
    RUNCOUNTS=$((RUNCOUNTS+1))
    sleep ${DELAY}
    # R:  010f0eb6

    ./a3233_avalon_usb_test.py -d d8f8ef6712146495c44192c07145fd6d974bf4bb8f41371d65c90d1e9cb18a170000000000000000000000000000000000000000087e051a895170504ac1d001 -n null -s $DEVICE
    # ERROR NEVER RETURN
    ERRORTIMES=$((ERRORTIMES+$?))
    RUNCOUNTS=$((RUNCOUNTS+1))
    sleep ${DELAY}

    ./a3233_avalon_usb_test.py -d d8f8ef6712146495c44192c07145fd6d974bf4bb8f41371d65c90d1e9cb18a170000000000000000000000000000000000000000087e051a895170504ac1d001 -n null -s $DEVICE
    # ERROR NEVER RETURN
    ERRORTIMES=$((ERRORTIMES+$?))
    RUNCOUNTS=$((RUNCOUNTS+1))
    sleep ${DELAY}

    ./a3233_avalon_usb_test.py -d d8f8ef6712146495c44192c07145fd6d974bf4bb8f41371d65c90d1e9cb18a170000000000000000000000000000000000000000087e051a8c5170504ac1d001 -n c95d88ca -s $DEVICE
    ERRORTIMES=$((ERRORTIMES+$?))
    RUNCOUNTS=$((RUNCOUNTS+1))
    sleep ${DELAY}
    # R:  c95d88ca

    ./a3233_avalon_usb_test.py -d d8f8ef6712146495c44192c07145fd6d974bf4bb8f41371d65c90d1e9cb18a170000000000000000000000000000000000000000087e051a895170504ac1d001 -n null -s $DEVICE
    # ERROR NEVER RETURN
    ERRORTIMES=$((ERRORTIMES+$?))
    RUNCOUNTS=$((RUNCOUNTS+1))
    sleep ${DELAY}

    ./a3233_avalon_usb_test.py -d d8f8ef6712146495c44192c07145fd6d974bf4bb8f41371d65c90d1e9cb18a170000000000000000000000000000000000000000087e051a8f5170504ac1d001 -n daa48ad5 -s $DEVICE
    ERRORTIMES=$((ERRORTIMES+$?))
    RUNCOUNTS=$((RUNCOUNTS+1))
    sleep ${DELAY}
    # R:  daa48ad5

    ./a3233_avalon_usb_test.py -d 81c9ffffdd3da630ea65fc9d857ccb588a77651867eb9370ed14a977f1d2de330000000000000000000000000000000000000000087e051a65527050c290e5a7 -n 873d6a5e -s $DEVICE
    ERRORTIMES=$((ERRORTIMES+$?))
    RUNCOUNTS=$((RUNCOUNTS+1))
    sleep ${DELAY}
    # R:  873d6a5e

    ./a3233_avalon_usb_test.py -d 4679ba4ec99876bf4bfe086082b400254df6c356451471139a3afa71e48f544a000000000000000000000000000000000000000087320b1a1426674f2fa722ce -n 000187a2 -s $DEVICE
    ERRORTIMES=$((ERRORTIMES+$?))
    RUNCOUNTS=$((RUNCOUNTS+1))
    sleep ${DELAY}
    # R:  000187a2

    echo "ErrRate: $ERRORTIMES/$RUNCOUNTS"
done
