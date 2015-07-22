#!/bin/sh
while read -r line || [[ -n $line ]]; do
	if [[ $line == *"$SKYPE_USERNAME"* ]]	
	then
# user is a mod, go ahead and ban
		while read -r line || [[ -n $inline ]]; do
			if [[ $inline == *"$*"* ]]	
			then
				echo "calminha $SKYPE_FULLNAME" | awk '{print tolower($0)}'
  				exit 1;	
			fi
		done < ./duarte-quotes/modlist
# target is not a mod, bye bye
		echo "$*" >> ./duarte-quotes/blacklist
# rub it in
  		echo "tens que ficar interdito $*"
  		exit 1;
	fi
done < ./duarte-quotes/modlist
echo "caladinho cabrão!"
