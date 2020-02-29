#!/usr/bin/expect

set host [lindex $argv 0]
set user [lindex $argv 1]
set passwd [lindex $argv 2]

spawn autossh  $user@$host
expect {
    "(yes/no)?" {
        send "yes\n"
        expect "password:"
        send "$passwd\n"
    }
    "password:" {
        send "$passwd\n"
    }
}

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

#!/usr/bin/expect
set HOST [lindex $argv 0]
set USER [lindex $argv 1]
set PASS [lindex $argv 2]
set LISTING_PORT [lindex $argv 3]
set SERVICE_PORT [lindex $argv 4]
set PROXY_PORT [lindex $argv 5]
spawn /usr/bin/autossh -M $LISTING_PORT -NR $PROXY_PORT:127.0.0.1:$SERVICE_PORT $USER@$HOST 
expect {
    "(yes/no)?" {
        send "yes\n"
        expect "*?assword:"
        send "$PASS\n"
    }
    "*?assword:" {
        send "$PASS\n"
    }
}