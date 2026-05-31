@echo off
git init
git add .
git commit -m "初始化教辅资料站"
git branch -M main
git remote add origin https://github.com/tobeno1no1/edu-resources-site.git
git push -u origin main
pause