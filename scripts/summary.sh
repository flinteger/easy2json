#!/bin/sh

cd out

total=0
for f in *.ndjson;
do
  # count=$(echo $(grep action $f | wc -l))
  # count=$(jq '. | length' $f)
  # total=$(expr $total + $count)
  count=$(wc -l $f | awk '{ print $1 }')
  printf "%-22s: %s\n" $f $count
done

total=$(cat *.ndjson | sort | uniq | wc -l | awk '{ print $1 }')

echo ""
printf "%-22s: %s\n" "Total rules" $total
echo ""
