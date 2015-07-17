#!/bin/sh
# Load config
source config.sh
# EO config

# Wake up Duarte
while [ 1 ]
do
    # time verification for Duarte's law:
    # Duarte never stays at work more than 1 minute, there's too much LoL to be played
    # Weekend? Duarte is smoking zlotas... no time to speak
    time=`date +"%k%M"`
    day=`date +"%u"`
    if [[ !( "$time" -gt 930 && "$time" -lt 1800) ]] || [[ "$day" -gt "5" ]]; then
        sleep 600
        continue
    fi
    

    # Duarte is in his workplace !

    # prepare a quote
    msg=`gshuf -n 1 quotes`
    
    # encrypted msg (md5, encrypted? ha ha)
    md5=`echo -n "$chat$msg$secret" | md5 -r`
    #md5sum prints a '-' to the end. Let's get rid of that.
    for m in $md5; do
        break
    done

    # send to sevabot api
    curl $msgaddress --data-urlencode chat="$chat" --data-urlencode msg="$msg" --data-urlencode md5="$m"
    echo -e "[$time] Sent: $msg"

    # 5 minutes break to handle velho
    sleep 300
done
