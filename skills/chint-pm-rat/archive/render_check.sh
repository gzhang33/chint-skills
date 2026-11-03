#!/usr/bin/env bash
# chint-pm-RAT 渲染目检一条龙：soffice 探测 → PDF → 150dpi PNG → 一页纸六敏感区裁切
# 用法: render_check.sh <input.pptx> [outdir]   （outdir 默认 <pptx所在目录>/.render）
# 依赖: LibreOffice(soffice)、poppler(pdftoppm)、Pillow(PIL)；裁切坐标与
#       references/zone-spec.md 分区同步维护。
set -euo pipefail

PPTX="${1:?用法: render_check.sh <input.pptx> [outdir]}"
OUT="${2:-$(dirname "$PPTX")/.render}"

SOFFICE="$(command -v soffice || true)"
if [ -z "$SOFFICE" ] && [ -x "/Applications/LibreOffice.app/Contents/MacOS/soffice" ]; then
  SOFFICE="/Applications/LibreOffice.app/Contents/MacOS/soffice"
fi
[ -n "$SOFFICE" ] || { echo "FAIL: 未找到 soffice（PATH 与 /Applications 均无）"; exit 1; }
command -v pdftoppm >/dev/null || { echo "FAIL: 缺 pdftoppm（brew install poppler）"; exit 1; }

mkdir -p "$OUT"
echo "→ PDF 转换"
"$SOFFICE" --headless --convert-to pdf --outdir "$OUT" "$PPTX" >/dev/null
PDF="$OUT/$(basename "${PPTX%.*}").pdf"

echo "→ 150dpi 整页渲染"
pdftoppm -png -r 150 "$PDF" "$OUT/page"

echo "→ 敏感区裁切（第 1 页文本框分区）"
python3 - "$OUT" <<'PY'
import sys
from PIL import Image

out = sys.argv[1]
# (x0, y0, x1, y1) 英寸坐标，源自 references/zone-spec.md（RAT 表格模版实测几何）
ZONES = {
    "L1_需求背景":   (0.05, 1.50, 4.30, 3.30),
    "L2_场景痛点":   (0.05, 3.30, 4.30, 4.75),
    "M1_产品定义":   (4.25, 1.50, 8.35, 4.75),
    "PM_L3快览":     (0.05, 4.70, 2.20, 7.50),
    "非PM_右列":     (8.20, 1.50, 13.10, 4.75),
    "非PM_底部小表": (2.10, 4.70, 13.10, 7.50),
}
d = 150
im = Image.open(f"{out}/page-1.png")
for name, (x0, y0, x1, y1) in ZONES.items():
    im.crop((round(x0 * d), round(y0 * d), round(x1 * d), round(y1 * d))
            ).save(f"{out}/crop_{name}.png")
    print(f"   crop_{name}.png")
PY

echo "完成：整页 $OUT/page-N.png（全部页）+ $OUT/crop_*.png（第 1 页六敏感区）"
echo "目检要点：crop 图内文字不得触底/缺末字（LibreOffice 会裁掉超框文字）"
