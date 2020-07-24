END=9
for i in $(seq 0 $END); do git push mirror-$i master; done;
for i in $(seq 0 $END); do git push mirror-$i $1; done;
