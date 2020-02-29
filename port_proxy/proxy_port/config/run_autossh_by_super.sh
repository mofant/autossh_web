#!/bin/bash
HOST=$1
USER=$2
PASS=$3
LISTING_PORT=$4
SERVICE_PORT=$5
PROXY_PORT=$6

VAR=$(expect -c "
spawn /usr/bin/autossh -M $LISTING_PORT -NR $PROXY_PORT:127.0.0.1:$SERVICE_PORT $USER@$HOST 
expect {
    \"(yes/no)?\" {
        send \"yes\n\"
        expect \"*?assword:\"
        send \"$PASS\n\"
    }
    \"*?assword:\" {
        send \"$PASS\n\"
    }
}
expect eof
")
echo "$VAR"