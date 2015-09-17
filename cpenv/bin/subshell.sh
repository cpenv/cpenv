#!/bin/bash
tmprc=$(mktemp)

echo "source ~/.bashrc" > $tmprc
echo "PS1='$PROMPT'" >> $tmprc
echo "rm -f $tmprc" >> $tmprc

bash --rcfile $tmprc
