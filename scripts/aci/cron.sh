#!/bin/bash

# crontab -l
#
## m h  dom mon dow   command
#00 * * * * ~/aci/cron.sh
#30 * * * * ~/aci/cron.sh

umask 0022
export LC_ALL=en_US.UTF-8

export PATH=~/bin:$PATH
BASEDIR=$(readlink -e $(dirname $0))

. $BASEDIR/aci.conf
FLAG_CHECK=$WORKDIR/.check
FLAG_FAIL=$WORKDIR/.fail

cd $WORKDIR
i=0

[ -e $FLAG_FAIL ] && echo "Last build failed, please clean $WORKDIR/.fail manually" && exit
while [ -e $FLAG_CHECK ]; do
        [ "$i" == "0" ] && echo "Wait for other checking process ..."
        sleep 10
        i=`expr $i + 1`
        # 25min
        [ "$i" -ge "`expr $TIMEOUT \* 6`" ] && echo "[ERROR]: Timed out" && my_mail "Avalon Check Timed Out" "`date`" && exit
done
touch $FLAG_CHECK

[ ! -d $WORKDIR/log ] && mkdir -p $WORKDIR/log
LOG=$WORKDIR/log/`date +%Y%m%d_%H%M`.log

# Automated Continuous Integration
$BASEDIR/aci.sh > $LOG 2>&1
RET="$?"
[ "$RET" != "0" ] && my_mail "Build Error $RET" "`[ -e $LOG ] && tail -256 $LOG`"
[ "$RET" == "0" ] && grep "Revision has not been changed" $LOG > /dev/null 2>&1 && rm $LOG

rm -f $FLAG_CHECK
