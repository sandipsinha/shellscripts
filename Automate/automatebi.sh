#!/bin/bash

CONFIG_FILE=automatebi.properties


if [[ -f $CONFIG_FILE ]]; then
        . $CONFIG_FILE
else
  echo 'Autoconfig.properties does not exists'
  exit
fi


echo 'Export the Owner Details'  $USER $PASS $HOST $DELIMIT $OWNERFILE $FILEPATH

freebcp " $OWNERQRY " queryout $FILEPATH$OWNERFILE -c -t $DELIMIT -S $HOST:1433 -U $USER -P $PASS

echo 'Export the Site Details'

freebcp " $SITEQRY " queryout $FILEPATH$SITEFILE -c -t $DELIMIT -S $HOST:1433 -U $USER -P $PASS

echo 'Export the Driver Details'

freebcp " $DRVRQRY " queryout $FILEPATH$DRVRFILE -c -t $DELIMIT -S $HOST:1433 -U $USER -P $PASS

echo 'Running the PROC'

echo "$CREATEPROC"| isql $DSN $USER $PASS $SERVER

echo 'Export the Vehicle Details'

freebcp " $VHCLQRY " queryout $FILEPATH$VHCLFILE -c -t $DELIMIT -S $HOST:1433 -U $USER -P $PASS

echo "$CREATEOWNRPROC"| isql $DSN $USER $PASS $SERVER

echo 'Export the Owner Time Zone'

freebcp " $OWNERTMQRY " queryout $FILEPATH$OWNERTIMEFILE -c -t $DELIMIT -S $HOST:1433 -U $USER -P $PASS

echo 'Export the Vehicle Time Zone'

echo "$CREATEVHCLPROC"| isql $DSN $USER $PASS $SERVER

freebcp " $VHCLTMQRY " queryout $FILEPATH$VHCLTIMEFILE -c -t $DELIMIT -S $HOST:1433 -U $USER -P $PASS

echo 'Export the User Details'

freebcp " $USERQRY " queryout $FILEPATH$USERFILE -c -t $DELIMIT -S $HOST:1433 -U $USER -P $PASS

echo 'Export the User Vehicle Details'

freebcp " $USERVHCLQRY " queryout $FILEPATH$USERVHCLFILE -c -t $DELIMIT -S $HOST:1433 -U $USER -P $PASS

echo 'Export the Tenant KPI Details'

freebcp " $TENANTKPIQRY " queryout $FILEPATH$TENANTKPIFILE -c -t $DELIMIT -S $HOST:1433 -U $USER -P $PASS

echo 'Export the User office Details'

freebcp " $USEROFFICEQRY " queryout $FILEPATH$USEROFFICEFILE -c -t $DELIMIT -S $HOST:1433 -U $USER -P $PASS

echo 'Export the Driver Target Details'

freebcp " $DRVRTGTQRY " queryout $FILEPATH$DRVRTGTFILE -c -t $DELIMIT -S $HOST:1433 -U $USER -P $PASS

echo 'Export the Vehicle Target Details'

freebcp " $VHCLTGTQRY " queryout $FILEPATH$VHCLTGTFILE -c -t $DELIMIT -S $HOST:1433 -U $USER -P $PASS

echo 'Export the Activity Log Details ' $ACTIVITYQRY 

freebcp " $ACTIVITYQRY " queryout $FILEPATH$ACTIVITYFILE -c -t $DELIMIT -S $HOST:1433 -U $USER -P $PASS

echo 'Done - Data Extract'

echo "$TRUNCSQL"| isql $DSN $USER $PASS $SERVER 

echo 'Inserting data for Owner Dim Fact'

echo "$OWNERSQL" | isql $DSN $USER $PASS $SERVER 


cp windowstimezone.csv /home/dataextract/



echo 'Done'
