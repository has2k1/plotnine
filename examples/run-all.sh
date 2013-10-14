#/bin/bash

for f in $(find . | grep .py)
do
    echo "python ${f}"
    python "${f}"
done


