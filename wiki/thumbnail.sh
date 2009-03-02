#!/bin/sh

for i in "$@"; do
    echo "Thumbnailing $i"
    convert -scale 200x200 -quality 85% "$i" "thumbnails/$(basename "$i")"
done

# EOF #
