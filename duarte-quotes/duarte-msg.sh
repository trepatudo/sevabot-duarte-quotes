#!/bin/sh
# Load config
source config.sh
# EO config

    msg="$1"

    md5=`echo -n "$chat$msg$secret" | md5 -r`

    #md5sum prints a '-' to the end. Let's get rid of that.
    for m in $md5; do
        break
    done

    curl $msgaddress --data-urlencode chat="$chat" --data-urlencode msg="$msg" --data-urlencode md5="$m"
    echo -e "Sent: $msg"
