#!/bin/bash
#
# chkconfig: 35 75 25
# description: Apache is a World Wide Web server.  It is used to serve \
# -----------------------------------------------------------------------
# Auth:
# Email:
# Version:
# Create date:
#------------------------------------------------------------------------
if [ -f /etc/sysconfig/httpd ]; then
  . /etc/sysconfig/httpd
fi
#-------------------------The color display------------------------#
COLUMENS=80
SPACE_COL=$[ $COLUMENS-21 ]
 
RED='\033[1;5;31m'
GREEN='\033[1;32m'
YELLOW='\033[33m'
NORMAL='\033[0m'
 
success() {
   REAL_SPACE=$[ $SPACE_COL - ${#1} ]
   echo -n  "$1"
   for i in `seq 1 $REAL_SPACE`; do
       echo -n " "
   done
   echo -e "[  ${GREEN}0k${NORMAL}  ]"
}
failure() {
   REAL_SPACE=$[ $SPACE_COL - ${#1} ]
   echo -n "$1"
   for i in `seq 1 $REAL_SPACE`; do
       echo -n " "
   done
   echo -e "[ ${RED}FAIL${NORMAL} ]"
}
 
#---------------------------Functions--------------------------------#
LOCKFILE="/var/lock/subsys/httpd"
PID=`ps aux | grep httpd | grep -v grep | grep root | grep /usr/local/httpd/bin/httpd$ | awk '{print $2}'`
HTTPD="httpd"
start() {
    /usr/local/httpd/bin/httpd
    [ $? -eq 0 ] && touch $LOCKFILE
    sleep 1
    success "$HTTPD is starting.."
}
stop() {
    rm -fr $LOCKFILE
    kill $PID
    if [  ! $? -eq 0 ]; then
        failure "$HTTPD is stop"
        exit 1
    fi
    sleep 1
    success "$HTTPD is stopping.."   
}
status() {
    if [ -e $LOCKFILE ]; then
       echo "$HTTPD is running [PID: $PID].."
    else
       echo "$HTTPD is stop"
   fi
}
#------------------------------Call----------------------------------#
case $1 in
start)
    if [ -e $LOCKFILE ]; then
        failure "$HTTPD already star"
    else
        sleep 1
        start
    fi
   ;;
stop)
    if [ ! -e $LOCKFILE ]; then
        failure "$HTTPD already stop"
    else
        sleep 1
        stop
    fi
   ;;
status)
    if [ -e $LOCKFILE ]; then
        echo -e "${GREEN}$HTTPD is running..PID:$PID${NORMAL}"
    else
        echo -e "\033[1;31m$HTTPD already stop${NORMAL}"
    fi
    ;;
restart)
    if [ -e $LOCKFILE ]; then
         stop
         sleep 1
         start
    else
         sleep 1
         start
    fi
    ;;
*)
    echo -e "\033[31;1mUsage:/etc/rc.d/init.d/$HTTPD {start|stop|restart|}\033[0m"
esac