#!/usr/bin/env python3
"""
批量导入脚本 - 从 CSV 或 JSON 文件批量添加资料
CSV 格式（第一行为表头）：
  title,grade,subject,brand,type,link,tags,description

用法：
  python batch_import.py resources.csv
  python batch_import.py resources.json
"""

import os
import sys
import csv
import json
from add_resource import add_resource, get_today

CONTENT_DIR = os.path.join(os.path.dirname(__file__), '..', 'src', 'content', 'resources')


def import_csv(filepath: str):
    with open(filepath, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print(f"📂 读取到 {len(rows)} 条记录")
    added = []
    for row in rows:
        result = add_resource(
            title=row.get('title', '').strip(),
            grade=row.get('grade', '').strip(),
            subject=row.get('subject', '').strip(),
            brand=row.get('brand', '').strip(),
            rtype=row.get('type', '').strip(),
            link=row.get('link', '').strip(),
            tags_str=row.get('tags', '').strip(),
            description=row.get('description', '').strip(),
        )
        if result:
            added.append(result)
    print(f"\n✅ 成功添加 {len(added)} 份资料")
    print_git_hint(len(added))


def import_json(filepath: str):
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f)
    items = data if isinstance(data, list) else data.get('resources', [])
    print(f"📂 读取到 {len(items)} 条记录")
    added = []
    for item in items:
        result = add_resource(
            title=item.get('title', '').strip(),
            grade=str(item.get('grade', '')).strip(),
            subject=item.get('subject', '').strip(),
            brand=item.get('brand', '').strip(),
            rtype=item.get('type', '').strip(),
            link=item.get('link', '').strip(),
            tags_str=','.join(item.get('tags', [])),
            description=item.get('description', '').strip(),
        )
        if result:
            added.append(result)
    print(f"\n✅ 成功添加 {len(added)} 份资料")
    print_git_hint(len(added))


def print_git_hint(count: int):
    if count > 0:
        print("\n📌 推送到 GitHub 更新网站：")
        print("   git add src/content/resources/")
        print(f'   git commit -m "批量新增 {count} 份资料 ({get_today()})"')
        print("   git push origin main")


def main():
    if len(sys.argv) < 2:
        print("用法: python batch_import.py <file.csv 或 file.json>")
        sys.exit(1)
    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"文件不存在: {filepath}")
        sys.exit(1)
    if filepath.endswith('.csv'):
        import_csv(filepath)
    elif filepath.endswith('.json'):
        import_json(filepath)
    else:
        print("仅支持 .csv 或 .json 文件")
        sys.exit(1)


if __name__ == '__main__':
    main()
