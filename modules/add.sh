#!/bin/sh
# Block noob joao
username="j.goncalinho"
usernameE="pedroestrela22"
if [ "$SKYPE_USERNAME" = "$username" ]
then
	echo "eu quero e que tu te fodas joao tiago"
	exit 1;
fi
if [ "$SKYPE_USERNAME" = "usernameE" ]
then
	echo "caladinho estrela"
	exit 1;
fi

# All good, duarte approves
echo "$*" >> ./duarte-quotes/quotes

# commit to git
git add ./duarte-quotes/quotes &>/dev/null
git commit -m "New quote by $SKYPE_USERNAME ($SKYPE_FULLNAME)" &>/dev/null
git push &>/dev/null

# let us know
echo "estou mesmo desertinho para dizer a nova quote"
