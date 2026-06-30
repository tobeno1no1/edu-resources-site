#!/usr/bin/env python3
"""
教辅资料封面图自动生成器
读取 src/content/resources/*.md 的 frontmatter，为每份资料生成一张柔和背景的封面图。
输出到 public/covers/<filename>.png

用法：
  python scripts/generate_covers.py
"""

import os
import re
import sys
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ===== 路径配置 =====
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
RESOURCES_DIR = PROJECT_DIR / "src" / "content" / "resources"
OUTPUT_DIR = PROJECT_DIR / "public" / "covers"

# 图片尺寸
IMG_W, IMG_H = 600, 420

# 字体路径（按平台优先级尝试）
FONT_CANDIDATES = [
    # Windows
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/simsun.ttc",
    # Linux (Noto CJK)
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    # macOS
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/Library/Fonts/Songti.ttc",
]

# 解析 FONT_REGULAR 和 FONT_BOLD（运行时查找）
def _find_font(bold=False):
    """查找可用的字体文件"""
    suffix = "Bold" if bold else "Regular"
    for p in FONT_CANDIDATES:
        if ("Bold" in p) == bold and os.path.exists(p):
            return p
    # 退化：返回第一个存在的字体（不管 bold）
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            return p
    return None

FONT_REGULAR = _find_font(bold=False) or _find_font(bold=True)
FONT_BOLD = _find_font(bold=True) or FONT_REGULAR

# ===== 科目配色方案（柔和渐变） =====
# 每个科目对应 (顶部颜色, 底部颜色, 装饰圆颜色, 主文字颜色, 副文字颜色)
SUBJECT_THEMES = {
    "语文": {
        "grad_top": (254, 242, 232),    # 暖橙
        "grad_bottom": (253, 226, 226), # 浅粉
        "circle": (251, 191, 36, 60),   # 半透明装饰
        "title_color": (120, 53, 15),   # 深棕
        "sub_color": (180, 83, 9),      # 中棕
        "accent_bar": (251, 146, 60),   # 橙色装饰条
    },
    "数学": {
        "grad_top": (239, 246, 255),    # 浅蓝
        "grad_bottom": (219, 234, 254), # 天蓝
        "circle": (59, 130, 246, 50),
        "title_color": (30, 58, 138),   # 深蓝
        "sub_color": (37, 99, 235),     # 中蓝
        "accent_bar": (96, 165, 250),   # 蓝色装饰条
    },
    "英语": {
        "grad_top": (236, 253, 245),    # 浅绿
        "grad_bottom": (209, 250, 229), # 薄荷绿
        "circle": (16, 185, 129, 50),
        "title_color": (6, 78, 59),     # 深绿
        "sub_color": (5, 150, 105),     # 中绿
        "accent_bar": (52, 211, 153),   # 绿色装饰条
    },
    "物理": {
        "grad_top": (255, 247, 237),    # 浅橙
        "grad_bottom": (254, 226, 226), # 浅红
        "circle": (239, 68, 68, 50),
        "title_color": (127, 29, 29),   # 深红
        "sub_color": (220, 38, 38),     # 中红
        "accent_bar": (248, 113, 113),  # 红色装饰条
    },
    "化学": {
        "grad_top": (245, 243, 255),    # 浅紫
        "grad_bottom": (237, 233, 254), # 淡紫
        "circle": (139, 92, 246, 50),
        "title_color": (76, 29, 149),   # 深紫
        "sub_color": (126, 34, 206),    # 中紫
        "accent_bar": (167, 139, 250),  # 紫色装饰条
    },
    "生物": {
        "grad_top": (240, 253, 244),    # 浅青绿
        "grad_bottom": (220, 252, 231), # 淡绿
        "circle": (34, 197, 94, 50),
        "title_color": (21, 94, 50),    # 深绿
        "sub_color": (22, 101, 52),     # 中绿
        "accent_bar": (74, 222, 128),   # 绿色装饰条
    },
    "历史": {
        "grad_top": (253, 246, 236),    # 浅棕
        "grad_bottom": (251, 238, 224), # 暖棕
        "circle": (180, 83, 9, 50),
        "title_color": (67, 20, 7),     # 深棕
        "sub_color": (120, 53, 15),     # 中棕
        "accent_bar": (217, 119, 6),    # 棕色装饰条
    },
    "地理": {
        "grad_top": (240, 253, 250),    # 浅青
        "grad_bottom": (204, 251, 241), # 淡青
        "circle": (20, 184, 166, 50),
        "title_color": (19, 78, 74),    # 深青
        "sub_color": (15, 118, 110),    # 中青
        "accent_bar": (45, 212, 191),   # 青色装饰条
    },
    "政治": {
        "grad_top": (254, 242, 242),    # 浅红
        "grad_bottom": (254, 226, 226), # 淡红
        "circle": (239, 68, 68, 50),
        "title_color": (127, 29, 29),   # 深红
        "sub_color": (185, 28, 28),     # 中红
        "accent_bar": (248, 113, 113),  # 红色装饰条
    },
    "道德法治": {
        "grad_top": (254, 242, 242),
        "grad_bottom": (254, 226, 226),
        "circle": (239, 68, 68, 50),
        "title_color": (127, 29, 29),
        "sub_color": (185, 28, 28),
        "accent_bar": (248, 113, 113),
    },
    "科学": {
        "grad_top": (255, 251, 235),    # 浅黄
        "grad_bottom": (254, 243, 199), # 淡黄
        "circle": (245, 158, 11, 50),
        "title_color": (120, 53, 15),   # 深棕
        "sub_color": (146, 64, 14),     # 中棕
        "accent_bar": (251, 191, 36),   # 黄色装饰条
    },
}

# 默认配色
DEFAULT_THEME = {
    "grad_top": (248, 250, 252),
    "grad_bottom": (241, 245, 249),
    "circle": (100, 116, 139, 30),
    "title_color": (30, 41, 59),
    "sub_color": (71, 85, 105),
    "accent_bar": (148, 163, 184),
}

GRADE_LABELS = {
    "1": "一年级", "2": "二年级", "3": "三年级",
    "4": "四年级", "5": "五年级", "6": "六年级",
    "7": "初一", "8": "初二", "9": "初三",
}


def parse_frontmatter(content: str) -> dict:
    """解析 Markdown frontmatter"""
    m = re.match(r"^---\r?\n(.*?)\r?\n---", content, re.DOTALL)
    if not m:
        return {}

    block = m.group(1)
    obj = {}
    for line in block.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        colon_idx = line.find(":")
        if colon_idx < 0:
            continue
        key = line[:colon_idx].strip()
        val = line[colon_idx + 1:].strip()

        # 字符串
        if val.startswith('"') and val.endswith('"'):
            obj[key] = val[1:-1].replace('\\"', '"')
        # 空字符串
        elif val == '""':
            obj[key] = ""
        # 数组
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            if inner:
                obj[key] = [
                    s.strip().strip('"') for s in inner.split(",")
                    if s.strip()
                ]
            else:
                obj[key] = []
        else:
            obj[key] = val

    return obj


def get_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    """加载字体，失败则用默认"""
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def draw_gradient(draw: ImageDraw.Draw, w: int, h: int,
                  top_color: tuple, bottom_color: tuple):
    """绘制垂直渐变背景"""
    for y in range(h):
        ratio = y / h
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def draw_decorative_circles(img: Image.Image, w: int, h: int,
                            circle_color: tuple):
    """在图片上绘制半透明装饰圆（使用 alpha paste）"""
    # 创建装饰图层
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    layer_draw = ImageDraw.Draw(layer)

    # 解析颜色
    cr, cg, cb = circle_color[0], circle_color[1], circle_color[2]
    base_alpha = circle_color[3] if len(circle_color) > 3 else 30

    # 右上角大圆（半径渐变模拟柔和感）
    cx1, cy1 = w - 50, 50
    for i in range(160, 0, -2):
        alpha = int(base_alpha * 1.5 * (1 - i / 160))
        layer_draw.ellipse(
            [cx1 - i, cy1 - i, cx1 + i, cy1 + i],
            fill=(cr, cg, cb, alpha)
        )

    # 左下角中圆
    cx2, cy2 = -10, h + 10
    for i in range(120, 0, -2):
        alpha = int(base_alpha * 0.8 * (1 - i / 120))
        layer_draw.ellipse(
            [cx2 - i, cy2 - i, cx2 + i, cy2 + i],
            fill=(cr, cg, cb, alpha)
        )

    # 合并
    img.alpha_composite(layer)


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int,
              draw: ImageDraw.Draw) -> list:
    """中文文本自动换行，返回行列表"""
    lines = []
    current = ""
    for char in text:
        test = current + char
        bbox = draw.textbbox((0, 0), test, font=font)
        w = bbox[2] - bbox[0]
        if w > max_width and current:
            lines.append(current)
            current = char
        else:
            current = test
    if current:
        lines.append(current)
    return lines


def clean_title(title: str) -> str:
    """清理标题，去掉方括号标签前缀，保留核心内容"""
    # 去掉【xxx】前缀
    title = re.sub(r"^【.+?】\s*", "", title)
    # 去掉 pdf电子版可打印 等后缀
    title = re.sub(r"\s*(pdf|PDF)?电子版可打印\s*$", "", title)
    title = re.sub(r"\s*含答案\s*$", "", title)
    return title.strip()


def generate_cover(md_path: Path, output_path: Path):
    """为单个 md 文件生成封面图"""
    content = md_path.read_text(encoding="utf-8")
    fm = parse_frontmatter(content)

    title = fm.get("title", "")
    subject = fm.get("subject", "")
    grade = fm.get("grade", "")
    brand = fm.get("brand", "")
    res_type = fm.get("type", "")

    if not title:
        return False

    theme = SUBJECT_THEMES.get(subject, DEFAULT_THEME)

    # 创建 RGBA 图片（用于半透明装饰合成）
    img = Image.new("RGBA", (IMG_W, IMG_H),
                    (255, 255, 255, 255))

    # 1. 绘制渐变背景（先用纯色铺底）
    bg = Image.new("RGBA", (IMG_W, IMG_H),
                   theme["grad_top"] + (255,))
    bg_draw = ImageDraw.Draw(bg)
    draw_gradient(bg_draw, IMG_W, IMG_H,
                  theme["grad_top"], theme["grad_bottom"])
    img.paste(bg, (0, 0))

    # 2. 绘制半透明装饰圆
    draw_decorative_circles(img, IMG_W, IMG_H, theme["circle"])

    # 重新获取绘制对象（alpha_composite 后在 RGB 上绘制）
    draw = ImageDraw.Draw(img)

    # 3. 顶部装饰条
    bar_h = 6
    draw.rounded_rectangle(
        [60, 45, 160, 45 + bar_h],
        radius=3,
        fill=theme["accent_bar"] + (255,)
    )

    # 4. 顶部标签行：年级 · 科目 · 品牌
    grade_label = GRADE_LABELS.get(grade, grade)
    top_label = f"{grade_label}  ·  {subject}  ·  {brand}"
    font_label = get_font(FONT_REGULAR, 22)
    draw.text((60, 65), top_label, fill=theme["sub_color"] + (255,),
              font=font_label)

    # 5. 主标题（清理后，自动换行）
    clean = clean_title(title)
    font_title = get_font(FONT_BOLD, 38)
    max_text_width = IMG_W - 100  # 左右各 50px 边距
    lines = wrap_text(clean, font_title, max_text_width, draw)

    # 限制最多3行（更紧凑）
    if len(lines) > 3:
        lines = lines[:3]

    # 计算标题垂直居中位置
    line_height = 54
    total_h = len(lines) * line_height
    start_y = (IMG_H - total_h) // 2 + 20

    for i, line in enumerate(lines):
        y = start_y + i * line_height
        draw.text((50, y), line, fill=theme["title_color"] + (255,),
                  font=font_title)

    # 6. 底部信息：资料类型 + 分隔线
    draw.line(
        [(60, IMG_H - 60), (IMG_W - 60, IMG_H - 60)],
        fill=theme["accent_bar"] + (255,),
        width=1
    )

    bottom_label = res_type if res_type else "教辅资料"
    font_bottom = get_font(FONT_REGULAR, 20)
    draw.text((60, IMG_H - 45), bottom_label,
              fill=theme["sub_color"] + (255,), font=font_bottom)

    # 右下角品牌
    font_brand = get_font(FONT_REGULAR, 18)
    brand_text = "教辅资料站"
    bbox = draw.textbbox((0, 0), brand_text, font=font_brand)
    tw = bbox[2] - bbox[0]
    draw.text((IMG_W - 60 - tw, IMG_H - 43), brand_text,
              fill=theme["sub_color"] + (255,), font=font_brand)

    # 转为 RGB 保存为 PNG
    img_rgb = Image.new("RGB", (IMG_W, IMG_H), (255, 255, 255))
    img_rgb.paste(img, mask=img.split()[3])
    img_rgb.save(output_path, "PNG", optimize=True)
    return True


def main():
    if not RESOURCES_DIR.exists():
        print(f"错误: 资料目录不存在: {RESOURCES_DIR}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    md_files = sorted(RESOURCES_DIR.glob("*.md"))
    if not md_files:
        print("未找到任何 .md 文件")
        sys.exit(1)

    success = 0
    failed = 0
    for md_file in md_files:
        output_name = md_file.stem + ".png"
        output_path = OUTPUT_DIR / output_name
        try:
            if generate_cover(md_file, output_path):
                success += 1
            else:
                failed += 1
                print(f"  跳过: {md_file.name}")
        except Exception as e:
            failed += 1
            print(f"  失败: {md_file.name} - {e}")

    print(f"\n{'='*40}")
    print(f"✓ 成功生成: {success} 张封面图")
    if failed:
        print(f"✗ 失败: {failed} 张")
    print(f"  输出目录: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
