#!/bin/sh
perl -e 'srand; rand($.) < 1 && ($line = $_) while <>; print $line;' ./duarte-quotes/quotes`
