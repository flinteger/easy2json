#!/bin/sh

cd out

for f in *json;
do
  count=$(echo $(grep action $f | wc -l))
  printf "%-22s: %s\n" $f $count
done

echo ""
total=$(echo $(cat *.json | grep action | wc -l))
printf "%-22s: %s\n" "Total rules" $total
echo ""
