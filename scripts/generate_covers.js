// 调用 Python 脚本生成封面图
// 用法：node scripts/generate_covers.js
import { spawnSync } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SCRIPT = path.join(__dirname, 'generate_covers.py');

// 尝试不同的 Python 命令
const candidates = process.platform === 'win32'
  ? ['python', 'python3', 'py']
  : ['python3', 'python'];

let py = null;
for (const c of candidates) {
  const r = spawnSync(c, ['--version'], { stdio: 'ignore' });
  if (r.status === 0) { py = c; break; }
}

if (!py) {
  console.error('未找到 Python，请先安装 Python 3.8+');
  process.exit(1);
}

console.log(`使用 Python: ${py}`);
const result = spawnSync(py, [SCRIPT], { stdio: 'inherit' });
process.exit(result.status || 0);
