#!/bin/sh
# Block noob joao
username="j.goncalinho"
if [ "$SKYPE_USERNAME" = "$username" ]
then
	echo "eu quero e que tu te fodas joao tiago"
	exit 1;
fi
# check blacklist
while read -r line || [[ -n $line ]]; do
	if [[ $line == *"$SKYPE_USERNAME"* ]]	
	then
# not allowed, tell user to fuck off
  		echo "eu quero e que tu te fodas $SKYPE_FULLNAME"
  		exit 1;
	fi
done < ./duarte-quotes/blacklist

# All good, duarte approves
echo "$*" >> ./duarte-quotes/quotes

# commit to git
git add ./duarte-quotes/quotes &>/dev/null
git commit -m "New quote by $SKYPE_USERNAME ($SKYPE_FULLNAME)" &>/dev/null
git push &>/dev/null

# let us know
echo "havia de aplicar"
