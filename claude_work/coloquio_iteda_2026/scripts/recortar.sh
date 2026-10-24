#!/usr/bin/env bash
# Center-crops an image to a given aspect ratio (width/height), so photos can be
# placed with both width and height fixed without distortion.
# Usage: scripts/recortar.sh input output ratio
set -euo pipefail
in=$1; out=$2; r=$3
w=$(identify -format %w "$in"); h=$(identify -format %h "$in")
geom=$(python3 -c "
w,h,r=$w,$h,$r
if w/h>r:
    nw=int(h*r); print(f'{nw}x{h}+{(w-nw)//2}+0')
else:
    nh=int(w/r); print(f'{w}x{nh}+0+{(h-nh)//2}')")
convert "$in" -crop "$geom" +repage "$out"
