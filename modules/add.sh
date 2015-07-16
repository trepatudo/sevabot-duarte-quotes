#!/bin/sh
# Block noob joao
username="j.goncalinho"
if [ "$SKYPE_USERNAME" = "$username" ]
then
	echo "eu quero e que tu te fodas, joao"
	exit 1;
fi

# All good, duarte approves
echo "$*" >> ./duarte-quotes/quotes

# commit to git
git commit -m "New quote by $SKYPE_USERNAME ($SKYPE_FULLNAME)" &>/dev/null
git push >> /dev/null  &>/dev/null

# let us know
echo "estou mesmo desertinho para dizer a nova quote"
