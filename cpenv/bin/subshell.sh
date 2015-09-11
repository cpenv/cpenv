#!/bin/bash
tmprc=$(mktemp)

echo "source ~/.bashrc" > $tmprc
echo "export PS1=" >> $tmprc
echo "rm -f $tmprc" >> $tmprc

bash --rcfile $tmprc
