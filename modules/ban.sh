#!/bin/sh
while read -r line || [[ -n $line ]]; do
	if [[ $line == *"$SKYPE_USERNAME"* ]]	
	then
	    echo "$*" >> ./duarte-quotes/blacklist
  		echo "tens que ficar interdito $*"
  		exit 1;
	fi
done < ./duarte-quotes/modlist
