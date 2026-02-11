# 001: sync_to_cloud 丢失脚本执行权限

**日期**: 2026-02-11
**严重性**: P0 — cron 完全不触发
**影响**: Finance 每日价格更新 + 扫描全部静默失败

## 现象

云端 cron 日志末尾出现：
```
/bin/sh: 1: /root/workspace/Finance/scripts/run_update_data.sh: Permission denied
/bin/sh: 1: /root/workspace/Finance/scripts/run_daily_scan.sh: Permission denied
```

Telegram 无通知，无报错邮件，完全静默失败。

## 根因

本地 `.sh` 文件权限为 `644`（无执行位），`sync_to_cloud.sh` 用 rsync/scp 同步后云端也变成 `644`，cron 直接执行 `.sh` 时 Permission denied。

## 修复

```bash
# 本地 + 云端都加执行权限
chmod +x scripts/run_update_data.sh scripts/run_daily_scan.sh
```

## 防范

- **新建 `.sh` 文件后必须 `chmod +x`**
- sync 脚本可考虑加 `--chmod=+x` 或 post-sync hook 自动修复权限
- cron 可改用 `bash /path/to/script.sh` 代替直接执行，不依赖执行位
