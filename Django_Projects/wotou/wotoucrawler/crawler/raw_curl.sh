#!/bin/sh

base='http://db.yaozh.com/zhuce?p='

i=0
while [[ $i -le 100 ]]; do
    url=$base$i
    echo $url
    curl $url
    let "i+=1"
done
