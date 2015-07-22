#!/bin/sh
while read -r line || [[ -n $line ]]; do
	if [[ $line == *"$SKYPE_USERNAME"* ]]	
	then
# user is a mod, go ahead and unban
    while read -r inline || [[ -n $inline ]]; do
	    if [[ $inline == *"$*"* ]]	
	    then
          file="./duarte-quotes/blacklist"
          grep -v "$inline" $file > temp && mv temp $file
# admit you missed the user
  		  echo "sdds"
  		  exit 1;
	    fi
    done < ./duarte-quotes/blacklist
    echo "nss"
  	exit 1;
	fi
done < ./duarte-quotes/modlist
echo "caladinho cabrão!"
