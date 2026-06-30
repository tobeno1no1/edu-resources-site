// 构建时生成 search-index.json
// 用法：node scripts/generate_search_index.mjs
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_DIR = path.resolve(__dirname, '..');
const RESOURCES_DIR = path.join(PROJECT_DIR, 'src', 'content', 'resources');
const OUTPUT = path.join(PROJECT_DIR, 'public', 'search-index.json');

function parseFrontmatter(content) {
  // 提取 --- 之间的内容
  const m = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!m) return null;
  const block = m[1];
  const obj = {};

  // 用一个简单的状态机解析
  // 规则：
  //   key: "value"  → string
  //   key: [a, "b", c]  → array
  //   key: value  → raw (number 等)
  const lines = block.split(/\r?\n/);
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    i++;
    if (!line.trim() || line.trim().startsWith('#')) continue;

    const colonIdx = line.indexOf(':');
    if (colonIdx < 0) continue;
    const key = line.slice(0, colonIdx).trim();
    let rest = line.slice(colonIdx + 1).trim();

    // 多行数组
    if (rest.startsWith('[') && !rest.includes(']')) {
      const arrLines = [rest];
      while (i < lines.length && !arrLines.join('\n').includes(']')) {
        arrLines.push(lines[i]);
        i++;
      }
      rest = arrLines.join(' ').trim();
    }

    // 字符串
    if (rest.startsWith('"') && rest.endsWith('"') && rest.length >= 2) {
      obj[key] = rest.slice(1, -1).replace(/\\"/g, '"');
      continue;
    }
    // 空字符串
    if (rest === '""') {
      obj[key] = '';
      continue;
    }
    // 数组
    if (rest.startsWith('[') && rest.endsWith(']')) {
      const inner = rest.slice(1, -1).trim();
      if (!inner) {
        obj[key] = [];
      } else {
        obj[key] = inner.split(',').map(s => s.trim()).map(s => {
          if (s.startsWith('"') && s.endsWith('"')) return s.slice(1, -1);
          return s;
        }).filter(Boolean);
      }
      continue;
    }
    // 数字
    if (/^-?\d+(\.\d+)?$/.test(rest)) {
      obj[key] = Number(rest);
      continue;
    }
    // 其它原始值
    obj[key] = rest;
  }
  return obj;
}

async function main() {
  const files = fs.readdirSync(RESOURCES_DIR).filter(f => f.endsWith('.md'));
  const items = [];
  for (const fname of files) {
    const fpath = path.join(RESOURCES_DIR, fname);
    const content = fs.readFileSync(fpath, 'utf-8');
    const fm = parseFrontmatter(content);
    if (!fm || !fm.title || !fm.link) {
      console.warn(`跳过: ${fname}`);
      continue;
    }
    const gradeNum = parseInt(fm.grade, 10);
    const gradeLabel = gradeNum <= 6 ? `小学${gradeNum}年级` : `初${gradeNum - 6}`;
    items.push({
      title: fm.title,
      subject: fm.subject || '',
      brand: fm.brand || '',
      type: fm.type || '',
      grade: String(fm.grade),
      gradeLabel,
      date: fm.date || '',
      link: fm.link,
      tags: fm.tags || [],
    });
  }

  fs.writeFileSync(OUTPUT, JSON.stringify(items), 'utf-8');
  console.log(`✓ 已生成 search-index.json: ${items.length} 条资料`);
  console.log(`  路径: ${OUTPUT}`);
}

main().catch(e => { console.error(e); process.exit(1); });
