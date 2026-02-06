# 构建部署相关问题

## .bashrc 非交互 shell 读不到环境变量 - 2026-02-05

**问题：** SSH 非交互执行或 cron 运行时，`.bashrc` 中的 `export` 不生效
**上下文：** 部署 dollar volume 采集到云端，wrapper 脚本 `source ~/.bashrc` 后 API key 仍为空
**原因：** `.bashrc` 开头有 `[ -z "$PS1" ] && return`，非交互 shell 直接退出
**解决方案：** 创建独立 `.env` 文件（`/root/workspace/Valuation/.env`），wrapper 脚本改为 `source .env`
**教训：** 环境变量不要依赖 `.bashrc`，用独立 `.env` 文件管理，所有 wrapper 都 source 它

## .gitignore data/ 匹配 src/data/ - 2026-02-05

**问题：** `git add src/data/*.py` 报 ignored，无法 track
**上下文：** `.gitignore` 中写了 `data/`，同时匹配了根目录 `data/` 和 `src/data/`
**解决方案：** 改为 `/data/`（加前缀 `/` 只匹配根目录）
**教训：** gitignore 规则不带 `/` 前缀时会匹配任意层级的同名目录
