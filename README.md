# 📚 教辅资料站

> 小学初中教辅资料免费分享网站，每日更新，基于 Astro 构建，部署于 GitHub Pages。

## 功能特性

- 📅 每日更新展示
- 🏫 按年级（1-9年级）分类浏览
- 📚 按科目筛选（数学/语文/英语/物理等）
- 🔗 夸克网盘直链跳转
- 💨 静态网站，访问极快
- 🤖 支持 WorkBuddy 自动化更新

---

## 本地开发

```bash
# 安装依赖
npm install

# 启动开发服务器（http://localhost:4321）
npm run dev

# 构建生产版本
npm run build
```

---

## 部署到 GitHub Pages（首次配置）

### 第一步：修改 astro.config.mjs

打开 `astro.config.mjs`，将以下内容中的 `YOUR_GITHUB_USERNAME` 替换为你的 GitHub 用户名：

```js
export default defineConfig({
  site: 'https://YOUR_GITHUB_USERNAME.github.io',
  base: '/edu-resources-site',
  // ...
});
```

### 第二步：创建 GitHub 仓库

1. 登录 GitHub，新建仓库，仓库名设为 `edu-resources-site`
2. **不要**勾选初始化 README

### 第三步：推送代码

```bash
cd edu-resources-site
git init
git add .
git commit -m "初始化教辅资料站"
git branch -M main
git remote add origin https://github.com/你的用户名/edu-resources-site.git
git push -u origin main
```

### 第四步：启用 GitHub Pages

1. 进入仓库 → Settings → Pages
2. Source 选择 **GitHub Actions**
3. 保存，等待约 2-3 分钟

网站地址：`https://你的用户名.github.io/edu-resources-site`

---

## 添加新资料

### 方式一：让 WorkBuddy 帮你添加（推荐）

直接告诉 WorkBuddy：
> "新增一篇资料：人教版五年级数学第二单元练习卷，链接是 https://pan.quark.cn/s/xxx，年级5，科目数学，品牌人教版，类型练习卷"

WorkBuddy 会自动调用脚本生成文件并提示 git 操作。

### 方式二：命令行添加单条

```bash
python scripts/add_resource.py \
  --title "人教版三年级数学 第一单元练习卷" \
  --grade 3 \
  --subject 数学 \
  --brand 人教版 \
  --type 练习卷 \
  --link "https://pan.quark.cn/s/xxxxxx" \
  --tags "第一单元,加法" \
  --desc "第一单元加减法综合练习"
```

或进入交互模式：
```bash
python scripts/add_resource.py
```

### 方式三：批量导入

复制 `scripts/resources_template.csv`，填写内容后：
```bash
python scripts/batch_import.py scripts/resources_template.csv
```

### 添加后推送更新

```bash
git add src/content/resources/
git commit -m "新增资料：xxx"
git push origin main
```

推送后 GitHub Actions 自动构建，约 **2-3 分钟**网站更新。

---

## 资料文件格式

每份资料是 `src/content/resources/` 目录下的 `.md` 文件：

```markdown
---
title: "人教版三年级数学上册 第二单元练习卷"
date: "2026-05-31"          # 日期 YYYY-MM-DD
grade: "3"                   # 年级 1-9（7=初一，8=初二，9=初三）
subject: "数学"              # 科目
brand: "人教版"              # 教材品牌
type: "练习卷"               # 类型
link: "https://pan.quark.cn/s/xxxxx"  # 夸克网盘链接
tags: ["乘法", "第二单元"]   # 标签（可选）
description: "简短描述"      # 描述（可选）
---
```

---

## 目录结构

```
edu-resources-site/
├── src/
│   ├── content/
│   │   └── resources/       # ← 所有资料 .md 文件放这里
│   ├── layouts/
│   │   └── BaseLayout.astro
│   ├── components/
│   │   └── ResourceCard.astro
│   ├── pages/
│   │   ├── index.astro      # 首页
│   │   ├── daily.astro      # 每日更新
│   │   └── grade/
│   │       └── [grade].astro # 年级页
│   └── styles/
│       └── global.css
├── scripts/
│   ├── add_resource.py      # 单条添加脚本
│   ├── batch_import.py      # 批量导入脚本
│   └── resources_template.csv
├── .github/workflows/
│   └── deploy.yml           # GitHub Actions 自动部署
├── astro.config.mjs
└── package.json
```
