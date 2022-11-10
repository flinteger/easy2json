#!/bin/sh

cd out

total=0
for f in *json;
do
  # count=$(echo $(grep action $f | wc -l))
  count=$(jq '. | length' $f)
  total=$(expr $total + $count)
  printf "%-22s: %s\n" $f $count
done

echo ""
printf "%-22s: %s\n" "Total rules" $total
echo ""
