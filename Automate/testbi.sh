#!/bin/bash

CONFIG_FILE=automatebi.properties


if [[ -f $CONFIG_FILE ]]; then
        . $CONFIG_FILE
else
  echo 'Autoconfig.properties does not exists'
  exit
fi





echo 'Running the PROC'

echo "$CREATEPROC"| isql $DSN $USER $PASS $SERVER


echo "$CREATEOWNRPROC"| isql $DSN $USER $PASS $SERVER

echo 'Export the Owner Time Zone'

freebcp " $OWNERTMQRY " queryout $FILEPATH$OWNERTIMEFILE -c -t $DELIMIT -S $HOST:1433 -U $USER -P $PASS

echo 'Export the Vehicle Time Zone'

echo "$CREATEVHCLPROC"| isql $DSN $USER $PASS $SERVER

freebcp " $VHCLTMQRY " queryout $FILEPATH$VHCLTIMEFILE -c -t $DELIMIT -S $HOST:1433 -U $USER -P $PASS


echo 'Done'
