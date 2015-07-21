#!/bin/sh
while read -r line || [[ -n $line ]]; do
	if [[ $line == *"$SKYPE_USERNAME"* ]]	
	then
# user is a mod, go ahead and ban
	    echo "$*" >> ./duarte-quotes/blacklist
# rub it in
  		echo "tens que ficar interdito $*"
  		exit 1;
	fi
done < ./duarte-quotes/modlist
echo "caladinho cabrão!"
