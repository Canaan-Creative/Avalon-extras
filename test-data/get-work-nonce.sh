#!/bin/bash

L1='a'
L2='a'

exec 6<./$1

while true;
do
  read L1 <&6
  read L2 <&6
  if [ "$L1" == "" ] || [ "$L2" == "" ];  then
    break
  fi
  echo "$L2" | grep -q " no nonce = "
  if [ "$?" != "0" ]; then
    echo "$L1" | cut -d":" -f4 | sed 's/ //'
    echo "$L2" | cut -d"=" -f2 | sed 's/ //'
  fi
done

exec 6<&-
