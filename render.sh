#!/usr/bin/env bash
# 渲染信息几何讲解视频并拼接成完整成片。
# 用法: ./render.sh [质量参数，默认 -qm]
#   -ql 480p15（快速预览） | -qm 720p30 | -qh 1080p60
set -euo pipefail

QUALITY="${1:--qm}"
case "$QUALITY" in
  -ql) DIR="480p15" ;;
  -qm) DIR="720p30" ;;
  -qh) DIR="1080p60" ;;
  *) echo "未知质量参数: $QUALITY"; exit 1 ;;
esac

SCENES=(TitleScene ManifoldScene EuclideanFailsScene
        FisherMetricScene GeodesicScene SummaryScene)

manim "$QUALITY" --disable_caching information_geometry.py "${SCENES[@]}"

OUT_DIR="media/videos/information_geometry/$DIR"
LIST="$OUT_DIR/concat.txt"
: > "$LIST"
for s in "${SCENES[@]}"; do
  echo "file '$s.mp4'" >> "$LIST"
done

ffmpeg -y -f concat -safe 0 -i "$LIST" -c copy information_geometry_full.mp4
echo "完整视频: information_geometry_full.mp4"
