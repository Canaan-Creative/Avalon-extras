#!/bin/bash

# Automated Continuous Integration script
#   Check revisions from feeds.conf and feeds-extra.conf, build if changed

set -e

BASEDIR=$(readlink -e $(dirname $0))
. $BASEDIR/aci.conf

REPO=$WORKDIR/repo
REVISION_LOG=$WORKDIR/revision.log
REVISION_NEW=$REVISION_LOG.new
REVISION_TMP=$REVISION_LOG.tmp
BUILD_DIR=`date +%Y%m%d_%H%M`

[ ! -d $REPO ] && mkdir $REPO
echo -ne > $REVISION_NEW

cd $WORKDIR
wget -nv https://raw.github.com/BitSyncom/cgminer-openwrt-packages/master/cgminer/data/feeds.conf -O $WORKDIR/feeds.conf

# Check all repos
cat $WORKDIR/feeds.conf $BASEDIR/feeds-extra.conf | sed "s/^ *//;s/ *$//;s/ \{1,\}/ /g;/^$/d;/^#.*$/d" | sort | uniq | grep -E '^src-' | while read line; do
        cd $REPO
        PROTOCOL="`echo $line | awk '{print $1}' | cut -b5-`"
        DIRECTORY="`echo $line | awk '{print $2}'`"
        URL="`echo $line | awk '{print $3}'`"
        BRANCH=""
        [ "$PROTOCOL" == "git-b" ] && BRANCH="`echo $line | awk '{print $4}'`"
        [ -z "$PROTOCOL" -o -z "$DIRECTORY" -o -z "$URL" ] && { echo "File format failed"; exit 1; }
        [ "$PROTOCOL" == "git-b" -a -z "$BRANCH" ] && { echo "File format failed"; exit 1; }

        # Checkout repo and get infomation if possible
        case "$PROTOCOL" in
        svn)
                #svn co $URL ./$DIRECTORY || { echo "Checkout svn failed: $URL"; exit 1; }
                #cd ./$DIRECTORY
                REVISION=`svn info "$URL" | grep -E "^Revision" | cut -d " " -f2`
                [ -z "$REVISION" ] && { echo "Get svn revision failed: $URL"; exit 1; }
                ;;
        git)
                if [ -d $REPO/$DIRECTORY ]; then
                        cd $REPO/$DIRECTORY
                        git pull || { cd $REPO; rm -rf $REPO/$DIRECTORY; }
                fi
                if [ ! -d $REPO/$DIRECTORY ]; then
                        cd $REPO
                        git clone $URL ./$DIRECTORY || { echo "Clone git failed: $URL"; exit 1; }
                fi
                cd $REPO/$DIRECTORY
                REVISION=`git log | head -n 1 | cut -d " " -f2`
                [ -z "$REVISION" ] && { echo "Get git revision failed: $URL"; exit 1; }
                ;;
        git-b)
                if [ -d $REPO/$DIRECTORY ]; then
                        cd $REPO/$DIRECTORY
                        git pull || { cd $REPO; rm -rf $REPO/$DIRECTORY; }
                fi
                if [ ! -d $REPO/$DIRECTORY ]; then
                        cd $REPO
                        git clone $URL ./$DIRECTORY || { echo "Clone git failed: $URL"; exit 1; }
                        cd $REPO/$DIRECTORY
                        git checkout -b "`basename $BRANCH`" $BRANCH
                fi
                REVISION=`git log | head -n 1 | cut -d " " -f2`
                [ -z "$REVISION" ] && { echo "Get git branch revision failed: $URL"; exit 1; }
                ;;
        *)
                echo "Protocol not supported"; exit 1;
                ;;
        esac
        echo -e "$PROTOCOL\t$URL\t$BRANCH\t$REVISION" >> $REVISION_NEW
done

sort $REVISION_NEW > $REVISION_TMP
mv $REVISION_TMP $REVISION_NEW

# Revision compare
[ ! -d $WORKDIR/$BUILD_DIR ] && mkdir -p $WORKDIR/$BUILD_DIR && chmod 0700 $WORKDIR/$BUILD_DIR
BUILD_LOG=$WORKDIR/$BUILD_DIR/$BUILD_DIR.log

cd $WORKDIR
if ! diff $REVISION_NEW $REVISION_LOG > $BUILD_LOG 2>&1; then
        my_mail "Avalon Build Start: $BUILD_DIR" "`echo --DIFF-- && echo && diff $REVISION_NEW $REVISION_LOG && echo` `echo --NEW-- && cat $REVISION_NEW` `echo --OLD-- && cat $REVISION_LOG`"

        echo "---------------- OLD REVISION ----------------"   >> $BUILD_LOG
        [ -r $REVISION_LOG ] && cat $REVISION_LOG               >> $BUILD_LOG
        echo                                                    >> $BUILD_LOG
        echo "---------------- NEW REVISION ----------------"   >> $BUILD_LOG
        cat $REVISION_NEW                                       >> $BUILD_LOG
        echo                                                    >> $BUILD_LOG

        cd $WORKDIR/$BUILD_DIR
        wget https://github.com/BitSyncom/avalon-extras/raw/master/scripts/build-avalon-image.sh -O build-avalon-image.sh
        chmod 0755 build-avalon-image.sh
        mkdir -p avalon/bin
        [ ! -d $WORKDIR/dl ] && mkdir -p $WORKDIR/dl
        ln -s $WORKDIR/dl avalon/dl

        TIME_BEGIN=`date +"%Y%m%d %H:%M:%S"`
        BUILD_BEGIN=`date +%s`
        AVA_TARGET_BOARD=tl-wr1043nd-v2 ./build-avalon-image.sh --build >> $BUILD_LOG 2>&1      && \
                AVA_TARGET_BOARD=tl-wr1043nd-v2 ./build-avalon-image.sh >> $BUILD_LOG 2>&1              && \
                AVA_TARGET_BOARD=tl-wr1043nd-v2 ./build-avalon-image.sh --cgminer >> $BUILD_LOG 2>&1    && \
                echo "===========================================================" >> $BUILD_LOG 2>&1   && \
                echo "=================== tl-wr1043nd-v2 DONE ===================" >> $BUILD_LOG 2>&1   && \
                echo "===========================================================" >> $BUILD_LOG 2>&1   && \
                AVA_TARGET_BOARD=tl-wr703n-v1 ./build-avalon-image.sh --build >> $BUILD_LOG 2>&1        && \
                AVA_TARGET_BOARD=tl-wr703n-v1 ./build-avalon-image.sh >> $BUILD_LOG 2>&1                && \
                AVA_TARGET_BOARD=tl-wr703n-v1 ./build-avalon-image.sh --cgminer >> $BUILD_LOG 2>&1      && \
                echo "===========================================================" >> $BUILD_LOG 2>&1   && \
                echo "==================== tl-wr703n-v1 DONE ====================" >> $BUILD_LOG 2>&1   && \
                echo "===========================================================" >> $BUILD_LOG 2>&1   && \
                AVA_TARGET_BOARD=pi-modelb-v2 ./build-avalon-image.sh --build >> $BUILD_LOG 2>&1        && \
                AVA_TARGET_BOARD=pi-modelb-v2 ./build-avalon-image.sh >> $BUILD_LOG 2>&1                && \
                AVA_TARGET_BOARD=pi-modelb-v2 ./build-avalon-image.sh --cgminer >> $BUILD_LOG 2>&1      && \
                echo "===========================================================" >> $BUILD_LOG 2>&1   && \
                echo "==================== pi-modelb-v2 DONE ====================" >> $BUILD_LOG 2>&1   && \
                echo "===========================================================" >> $BUILD_LOG 2>&1
        RET="$?"
        TIME_END=`date +"%Y%m%d %H:%M:%S"`
        BUILD_END=`date +%s`
        BUILD_COST=0
        BUILD_H=0
        BUILD_M=0
        BUILD_S=0
        [ "${BUILD_END}" -gt "${BUILD_BEGIN}" ] && BUILD_COST=`expr ${BUILD_END} - ${BUILD_BEGIN}`
        expr ${BUILD_COST} / 3600 > /dev/null 2>&1 && BUILD_H=`expr ${BUILD_COST} / 3600`
        expr ${BUILD_COST} / 60 % 60 > /dev/null 2>&1 && BUILD_M=`expr ${BUILD_COST} / 60 % 60`
        expr ${BUILD_COST} % 60 > /dev/null 2>&1 && BUILD_S=`expr ${BUILD_COST} % 60`

        echo                                                                    >> $BUILD_LOG
        echo "############################################################"     >> $BUILD_LOG
        echo " FROM  ${TIME_BEGIN}  TO  ${TIME_END}"                            >> $BUILD_LOG
        echo " BUILD RETURN : ${RET}"                                           >> $BUILD_LOG
        echo " TIME COST ${BUILD_H}:${BUILD_M}:${BUILD_S}"                      >> $BUILD_LOG
        echo "############################################################"     >> $BUILD_LOG
        echo                                                                    >> $BUILD_LOG

        cd $WORKDIR
        chmod 0755 $WORKDIR/$BUILD_DIR
        my_mail "Avalon Build End ${BUILD_DIR}$([ $RET != 0 ] && echo -FAILED-${RET})" \
                "`echo ============================================================ && echo` \
                 `echo  FROM  ${TIME_BEGIN}  TO  ${TIME_END} && echo` \
                 `echo  BUILD RETURN : ${RET} && echo` \
                 `echo  TIME COST ${BUILD_H}:${BUILD_M}:${BUILD_S} && echo` \
                 `echo ============================================================ && echo` \
                 `echo && echo && echo --DIFF-- && diff $REVISION_NEW $REVISION_LOG` \
                 `echo && echo && echo --NEW-- && cat $REVISION_NEW && echo && echo --OLD-- && cat $REVISION_LOG` \
                 `echo && echo && echo --ls-- && ls -lR $WORKDIR/$BUILD_DIR/avalon/bin/`"
        rm -rf $WORKDIR/$BUILD_DIR/avalon/[cdlo]* $WORKDIR/$BUILD_DIR/build-avalon-image.sh
        [ "$RET" != "0" ] && mv $WORKDIR/$BUILD_DIR $WORKDIR/$BUILD_DIR_failed
        mv $REVISION_NEW $REVISION_LOG
        exit 0
else
        cd $WORKDIR
        rm $REVISION_NEW
        rm -rf $WORKDIR/$BUILD_DIR
        echo "Revision has not been changed"
        exit 0
fi

