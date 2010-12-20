#!/bin/sh

### BEGIN INIT INFO
# Provides: redflash
# Required-Start: $local_fs $syslog
# Required-Stop: $local_fs $syslog
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: Gunicorn processes for redflash
### END INIT INFO

USER=www-data
NAME=redflash
PID="/tmp/"$NAME".pid"
LOGFILE=/var/log/redflash.log
REDFLASH_ROOT="/srv/redflash"
GUNICORN_RUN="$REDFLASH_ROOT/bin/gunicorn --log-file=$LOGFILE -D -p $PID -w 4 redflash_wsgi:application"
# Confdir: the Django project inside the virtualenv
CONFDIR="$REDFLASH_ROOT/redflash/config"
VENV_ACTIVATION=". ../../bin/activate"
RETVAL=0

# source function library
. /lib/lsb/init-functions

start()
{
echo "Starting $NAME."
touch $LOGFILE
chown $USER $LOGFILE
su -c "cd $CONFDIR; $VENV_ACTIVATION; $GUNICORN_RUN &" $USER && echo "OK" || echo "failed";
}

stop()
{
echo "Stopping $NAME"
kill -QUIT `cat $PID` && echo "OK" || echo "failed";
}

reload()
{
echo "Reloading $NAME:"
if [ -f $PID ]
then kill -HUP `cat $PID` && echo "OK" || echo "failed";
fi
}

case "$1" in
start)
start
;;
stop)
stop
;;
restart)
reload
;;
reload)
reload
;;
force-reload)
stop && start
;;
*)
echo $"Usage: $0 {start|stop|restart}"
RETVAL=1
esac
exit $RETVAL

