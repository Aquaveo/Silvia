#!/bin/bash

#Source: HIDROLOGIA/Monitoreo_Hidrologico/SILVIA/SILVIA_v1
#File:SILVIA_Op.csv 
HOST="xxxxxxx"
USER="xxxxxxx"
PASSWORD="xxxxxxxx"

SOURCE=$1
ALL_FILES="${@:2}"

ftp -p -inv $HOST <<EOF
user $USER $PASSWORD
cd $SOURCE
mget $ALL_FILES
bye
EOF