#!/bin/bash
#
# chkconfig: 2345 80 30
# description: Postfix is a Mail Transport Agent, which is the program \
# processname: master
# pidfile: /var/spool/postfix/pid/master.pid
# config: /etc/postfix/main.cf
# config: /etc/postfix/master.cf
 
# Source function library.
. /etc/rc.d/init.d/functions
 
# Source networking configuration.
. /etc/sysconfig/network
 
# Check that networking is up.
[ $NETWORKING = "no" ] && exit 3
 
[ -x /usr/sbin/postfix ] || exit 4
[ -d /etc/postfix ] || exit 5
[ -d /var/spool/postfix ] || exit 6
RETVAL=0
prog="postfix"
start() {
      # Start daemons.
      echo -n $"Starting postfix: "
        /usr/bin/newaliases >/dev/null 2>&1
      /usr/sbin/postfix start 2>/dev/null 1>&2 && success || failure $"$prog start"
      RETVAL=$?
      [ $RETVAL -eq 0 ] && touch /var/lock/subsys/postfix
        echo
      return $RETVAL
}
stop() {
        # Stop daemons.
      echo -n $"Shutting down postfix: "
      /usr/sbin/postfix stop 2>/dev/null 1>&2 && success || failure $"$prog stop"
      RETVAL=$?
      [ $RETVAL -eq 0 ] && rm -f /var/lock/subsys/postfix
      echo
      return $RETVAL
}
reload() {
      echo -n $"Reloading postfix: "
      /usr/sbin/postfix reload 2>/dev/null 1>&2 && success || failure $"$prog reload"
      RETVAL=$?
      echo
      return $RETVAL
}
abort() {
      /usr/sbin/postfix abort 2>/dev/null 1>&2 && success || failure $"$prog abort"
      return $?
}
flush() {
      /usr/sbin/postfix flush 2>/dev/null 1>&2 && success || failure $"$prog flush"
      return $?
}
check() {
      /usr/sbin/postfix check 2>/dev/null 1>&2 && success || failure $"$prog check"
      return $?
}
restart() {
      stop
      start
}
# See how we were called.
case "$1" in
  start)
      start
       ;;
  stop)
      stop
      ;;
  restart)
      stop
      start
      ;;
  reload)
      reload
      ;;
  abort)
      abort
      ;;
  flush)
      flush
      ;;
  check)
      check
      ;;
  status)
      status master
      ;;
  condrestart)
      [ -f /var/lock/subsys/postfix ] && restart || :
      ;;
  *)
      echo $"Usage: $0 {start|stop|restart|reload|abort|flush|check|status|condrestart}"
      exit 1
esac
exit $?
# END