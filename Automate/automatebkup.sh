#!/bin/bash

CONFIG_FILE=automatebi.properties


if [[ -f $CONFIG_FILE ]]; then
        . $CONFIG_FILE
else
  echo 'Autoconfig.properties does not exists'
  exit
fi


s3cmd cp --recursive --exclude=PreviousData* s3://$BUCKET/$REGION/ s3://$BUCKET/$REGION/PreviousData/$TODT/RawData


echo 'Done'
