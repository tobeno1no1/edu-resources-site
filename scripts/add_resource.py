#!/usr/bin/env python3
"""
教辅资料站 - WorkBuddy 内容更新脚本
用法：
  python add_resource.py \
    --title "人教版三年级数学 第一单元练习卷" \
    --grade 3 \
    --subject 数学 \
    --brand 人教版 \
    --type 练习卷 \
    --link "https://pan.quark.cn/s/xxxxxx" \
    --tags "第一单元,加法" \
    --desc "第一单元加减法综合练习"

也可以直接运行进入交互模式：
  python add_resource.py
"""

import os
import sys
import argparse
import re
from datetime import datetime, timezone, timedelta

# 内容目录路径（相对于此脚本）
CONTENT_DIR = os.path.join(os.path.dirname(__file__), '..', 'src', 'content', 'resources')

GRADE_LABELS = {
    '1': '小学一年级', '2': '小学二年级', '3': '小学三年级',
    '4': '小学四年级', '5': '小学五年级', '6': '小学六年级',
    '7': '初一', '8': '初二', '9': '初三',
}

SUBJECT_ABBR = {
    '数学': 'math', '语文': 'chinese', '英语': 'english',
    '物理': 'physics', '化学': 'chemistry', '生物': 'biology',
    '历史': 'history', '地理': 'geography', '政治': 'politics',
}

TYPE_ABBR = {
    '练习卷': 'exercise', '测试卷': 'test', '知识点': 'knowledge',
    '真题': 'exam', '答案': 'answer', '专项练习': 'special',
    '复习卷': 'review', '专题卷': 'topic',
}


def slugify(text: str) -> str:
    """简单将中文标题转为英文filename（使用abbr）"""
    return re.sub(r'[^\w\-]', '', text.replace(' ', '-'))[:30]


def get_today() -> str:
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime('%Y-%m-%d')


def generate_filename(date: str, subject: str, grade: str, title: str) -> str:
    subj = SUBJECT_ABBR.get(subject, slugify(subject))
    safe_title = slugify(title) or 'resource'
    return f"{date}-{subj}-g{grade}-{safe_title}.md"


def generate_md(title: str, date: str, grade: str, subject: str,
                brand: str, rtype: str, link: str,
                tags: list[str], description: str) -> str:
    tags_yaml = ', '.join(f'"{t.strip()}"' for t in tags if t.strip())
    desc = description.replace('"', '\\"')
    return f"""---
title: "{title}"
date: "{date}"
grade: "{grade}"
subject: "{subject}"
brand: "{brand}"
type: "{rtype}"
link: "{link}"
tags: [{tags_yaml}]
description: "{desc}"
---
"""


def add_resource(title, grade, subject, brand, rtype, link, tags_str, description):
    date = get_today()
    tags = [t.strip() for t in tags_str.split(',') if t.strip()] if tags_str else []
    filename = generate_filename(date, subject, grade, title)
    filepath = os.path.join(CONTENT_DIR, filename)

    if os.path.exists(filepath):
        print(f"⚠️  文件已存在：{filename}")
        overwrite = input("是否覆盖？(y/N) ").strip().lower()
        if overwrite != 'y':
            print("已取消。")
            return None

    content = generate_md(title, date, grade, subject, brand, rtype, link, tags, description)

    os.makedirs(CONTENT_DIR, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✅ 已生成文件：src/content/resources/{filename}")
    print(f"   标题：{title}")
    print(f"   年级：{GRADE_LABELS.get(grade, grade)}")
    print(f"   科目：{subject} | 品牌：{brand} | 类型：{rtype}")
    print(f"   日期：{date}")
    print()
    print("📌 下一步：在项目根目录执行以下命令推送到 GitHub：")
    print(f"   git add src/content/resources/{filename}")
    print(f'   git commit -m "新增资料：{title}"')
    print("   git push origin main")
    print()
    print("🚀 推送后约 2~3 分钟网站自动更新！")
    return filepath


def interactive_mode():
    print("=" * 50)
    print("  📚 教辅资料站 - 添加新资料")
    print("=" * 50)
    title = input("资料标题：").strip()
    if not title:
        print("标题不能为空")
        sys.exit(1)

    print("年级（1-9，其中7=初一，8=初二，9=初三）：", end='')
    grade = input().strip()
    if grade not in GRADE_LABELS:
        print(f"年级无效，请输入 1-9")
        sys.exit(1)

    subject = input("科目（数学/语文/英语/物理/化学/生物等）：").strip()
    brand = input("教材品牌（人教版/部编版/苏教版等）：").strip()
    rtype = input("资料类型（练习卷/测试卷/知识点/真题/答案/专题卷等）：").strip()
    link = input("夸克网盘链接：").strip()
    tags_str = input("标签（逗号分隔，可留空）：").strip()
    description = input("简短描述（可留空）：").strip()

    add_resource(title, grade, subject, brand, rtype, link, tags_str, description)


def main():
    parser = argparse.ArgumentParser(description='添加教辅资料到网站')
    parser.add_argument('--title', type=str, help='资料标题')
    parser.add_argument('--grade', type=str, help='年级 (1-9)')
    parser.add_argument('--subject', type=str, help='科目')
    parser.add_argument('--brand', type=str, help='教材品牌')
    parser.add_argument('--type', dest='rtype', type=str, help='资料类型')
    parser.add_argument('--link', type=str, help='夸克网盘链接')
    parser.add_argument('--tags', type=str, default='', help='标签（逗号分隔）')
    parser.add_argument('--desc', type=str, default='', help='简短描述')

    args = parser.parse_args()

    if all([args.title, args.grade, args.subject, args.brand, args.rtype, args.link]):
        add_resource(
            args.title, args.grade, args.subject, args.brand,
            args.rtype, args.link, args.tags, args.desc
        )
    else:
        interactive_mode()


if __name__ == '__main__':
    main()
