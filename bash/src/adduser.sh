#!/bin/bash
#
#./SCRIPTNAME.sh -v -h --add/--del peng,dong,wen
declare -i DEBUG=0
declare -i ADD=0
declare -i DEL=0
if [ $# -lt 1 ]; then
echo "Usage:./`basename $0` --add/--del USER,USER -v|--verbose -h|--help"
exit 1
fi
for i in `seq 1 $#`; do
  case $1 in
  -v|--verbose)
     DEBUG=1
     shift 1
     ;;
  -h|--help)
    echo "Usage:./`basename $0` --add/--del USER,USER -v|--verbose -h|--help"
    exit 0
    ;;
  --add)
    ADD=1
    ADDUSER=$2
    shift 2
    ;;
  --del)
    DEL=1
    DELUSER=$2
    shift 2
    ;;
  *)
    echo "Usage:./`basename $0` --add/--del USER,USER -v|--verbose -h|--help"
    esac
done
if [ $ADD -eq 1 ]; then
  for USER in `echo $ADDUSER | sed 's@,@ @g'`; do
    if id $USER &> /dev/null; then
    [ $DEBUG -eq 1 ] && echo "user $USER exist."
    else
    useradd $USER
    echo "$USER" passwd --tdin $USER &> /dev/null
    [ $DEBUG = 1 ] && echo "user $USER add success."
    fi
  done
fi
 
if [ $DEL -eq 1 ]; then
  for USER in `echo $DELUSER | sed 's@,@ @g'`; do
    if id $USER &> /dev/null; then
    userdel -r $USER
    [ $DEBUG -eq 1 ] && echo "user $USER delete success."
  else
    [ $DEBUG = 1 ] && echo "user $SEER not exist."
  fi
  done
fi