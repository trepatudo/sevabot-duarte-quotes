#!/usr/bin/python
import random
import sys
# TODO n ler um uma etc
file = './duarte-quotes/quotes'
lines = [line.strip() for line in open(file)]
message = 'jss'
ans = list()
if len(sys.argv) == 2:
	message = sys.argv[1]
for line in lines:
	msgwords=message.split()
	for word in msgwords:
		if word in line:
			ans.append(line)
print(random.choice(ans))
