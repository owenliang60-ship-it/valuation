#!/bin/bash
# Finance 工作区同步到云端
# 用法: ./sync_to_cloud.sh [--code|--data|--all]
# 注意: 云端路径仍为 /root/workspace/Finance (保持 cron 兼容)

set -e

LOCAL_DIR="/Users/owen/CC workspace/Finance"
REMOTE="aliyun:/root/workspace/Finance"

sync_code() {
    echo "📦 同步代码..."
    rsync -avz --delete \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        "$LOCAL_DIR/src/" "$REMOTE/src/"
    rsync -avz --delete \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        "$LOCAL_DIR/scripts/" "$REMOTE/scripts/"
    rsync -avz "$LOCAL_DIR/config/settings.py" "$REMOTE/config/"
    echo "✅ 代码同步完成"
}

sync_data() {
    echo "📊 同步数据..."
    rsync -avz "$LOCAL_DIR/data/valuation.db" "$REMOTE/data/"
    rsync -avz "$LOCAL_DIR/data/dollar_volume.db" "$REMOTE/data/" 2>/dev/null || true
    rsync -avz "$LOCAL_DIR/data/fundamental/" "$REMOTE/data/fundamental/"
    rsync -avz "$LOCAL_DIR/data/pool/" "$REMOTE/data/pool/"
    # 量价数据通常云端自己更新，除非需要可以取消注释
    # rsync -avz "$LOCAL_DIR/data/price/" "$REMOTE/data/price/"
    echo "✅ 数据同步完成"
}

verify_cloud() {
    echo "🔍 验证云端..."
    ssh aliyun "cd /root/workspace/Finance && python3 -c \"
from config.settings import FMP_API_KEY
from src.data.pool_manager import get_symbols
print(f'API Key: OK')
print(f'股票池: {len(get_symbols())} 只')
\""
    echo "✅ 云端验证通过"
}

case "${1:-all}" in
    --code)
        sync_code
        ;;
    --data)
        sync_data
        ;;
    --all|*)
        sync_code
        sync_data
        verify_cloud
        ;;
esac

echo ""
echo "🚀 同步完成! 云端定时任务将自动运行"
