#!/bin/sh
awk 'BEGIN{i=1} /.*/{printf "%d: % s\n",i,$0; i++}' ./duarte-quotes/quotes | curl -s -F 'sprunge=<-' http://sprunge.us
