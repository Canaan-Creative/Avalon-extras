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
    echo "$L1$L2"
done

exec 6<&-
