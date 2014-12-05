#!/bin/bash

CONFIG_FILE=autoconfig.properties

if [[ -f $CONFIG_FILE ]]; then
        . $CONFIG_FILE
else
  echo 'Autoconfig.properties does not exists'
  exit
fi
#Copy the DSP File
echo 'Now Copying the DSP Prop file'
if [[ -f $PWD/pentahofiles/NoCodeDsp.properties ]]; then
   cp $SOURCE/NoCodeDsp.properties $PENTAHOHOME/$DSP   
else
  echo 'No Code DSP properties does not exists'
  exit
fi

#Copy the sln700 jar File
echo 'Now Copying the sln700 jar file'

if [[ -f $SOURCE/pentaho-sln7000-5.0-GA.jar ]]; then
   cp $SOURCE/pentaho-sln7000-5.0-GA.jar $PENTAHOHOME/$JAR
else
  echo 'pentaho-sln7000-5.0-GA.jar does not exists'
  exit
fi

#Copy the onfig files
echo 'Now Copying the Config files'
if [[ -f $SOURCE/applicationContext-OEM.xml ]]; then
   cp $SOURCE/applicationContext-OEM.xml $PENTAHOHOME/$CONFIG
else
  echo 'applicationContext-OEM.xml  does not exists'
  exit
fi

#Copy the onfig files
echo 'Now Copying the second Config files'
if [[ -f $SOURCE/applicationContext-spring-security.xml ]]; then
   cp $SOURCE/applicationContext-spring-security.xml $PENTAHOHOME/$CONFIG
else
  echo 'applicationContext-spring-security.xml  does not exists'
  exit
fi

#Copy the onfig files
echo 'Now Copying the third Config files'
if [[ -f $SOURCE/applicationContext-spring-security-jackrabbit.xml ]]; then
   cp $SOURCE/applicationContext-spring-security-jackrabbit.xml $PENTAHOHOME/$CONFIG
else
  echo 'applicationContext-spring-security-jackrabbit.xml  does not exists'
  exit
fi

#Copy the config files
echo 'Now Copying the fourth Config files'
if [[ -f $SOURCE/pentaho-spring-beans.xml ]]; then
   cp $SOURCE/pentaho-spring-beans.xml  $PENTAHOHOME/$CONFIG
else
  echo 'pentaho-spring-beans.xml does not exists'
  exit
fi



#Copy the commons-configuration-1.5.jar  jar File
echo 'Now Copying the commons-configuration-1.5.jar  file'

if [[ -f $SOURCE/commons-configuration-1.5.jar ]]; then
   cp $SOURCE/commons-configuration-1.5.jar  $PENTAHOHOME/$JAR
else
  echo 'commons-configuration-1.5.jar  does not exists'
  exit
fi


#Copy the mysql drivers  File
echo 'Now Copying the sqlodbc  file'

if [[ -f $SOURCE/sqljdbc4.jar ]]; then
   cp $SOURCE/sqljdbc4.jar  $PENTAHOHOME/$LIB
else
  echo 'sqljdbc4.jar  does not exists'
  exit
fi

#Copy the mysql drivers  File
echo 'Now Copying the mysql-connector-java-5.1.30-bin file'

if [[ -f $SOURCE/mysql-connector-java-5.1.30-bin.jar ]]; then
   cp $SOURCE/mysql-connector-java-5.1.30-bin.jar  $PENTAHOHOME/$LIB
else
  echo 'mysql-connector-java-5.1.30-bin.jar  does not exists'
  exit
fi

head --lines=31  $PENTAHOHOME/$CONTEXT/context.xml >  contexthead.txt 

#sed -i 's|<\/context>|'"$DSSTRING"'|g' $PENTAHOHOME/$CONTEXT/context.xml

cp  contexthead.txt  $PENTAHOHOME/$CONTEXT/context.xml

#sed '/<Valve/{N;s/.*$//;}' $PENTAHOHOME/$CONTEXT/context.xml

echo $DSSTRING >> $PENTAHOHOME/$CONTEXT/context.xml

echo 'Second sed'

sed -i 's|'"$MOND1"'|'"$MOND1A"'|g' $PENTAHOHOME/$MONDRIAN/mondrian.properties

echo 'third sed'

sed -i 's|'"$MOND2"'|'"$MOND2A"'|g' $PENTAHOHOME/$MONDRIAN/mondrian.properties

sed -i '/'"$MOND3"'/d' $PENTAHOHOME/$MONDRIAN/mondrian.properties 

echo $MOND3 >> $PENTAHOHOME/$MONDRIAN/mondrian.properties

if [[ -d $PENTAHOHOME/$MSGCLASS ]]; then
        echo "directory found"
else
        mkdir -p $PENTAHOHOME/$MSGCLASS
fi

cp $SOURCE/MondrianMessages*.prop* $PENTAHOHOME/$MSGCLASS


sed -i 's|'"$THEME1"'|'"$THEME2"'|g' $PENTAHOHOME/$THEMEDIR1/themes.xml


sed -i 's|'"$THEME3"'|'"$THEME4"'|g' $PENTAHOHOME/$CONFIG/pentaho.xml

sed -i 's|'"$SESSION1"'|'"$SESSION2"'|g' $PENTAHOHOME/$SESSION/web.xml

sed -i '/'"$HSQL1"'/,/'"$HSQL2"'/{//!d}' $PENTAHOHOME/$SESSION/web.xml
