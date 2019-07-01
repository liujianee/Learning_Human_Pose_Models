#!/usr/bin/env sh
# 
# 

echo "Creating images..."

a=1
for i in $(seq 1 3)
do
    start=`expr $a \* $i`
    end=`expr $a \* $i + $a`
    echo "=====pose starting from: $start"
    echo "=====pose ending to: $end"
    blender --background --python ./lighting_render.py -- $start $end
    sleep 10
done

echo "Done Done Done."
