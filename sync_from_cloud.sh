#!/bin/bash
# 从云端拉取最新数据到本地
# 用法: ./sync_from_cloud.sh [--price|--all]
set -e

LOCAL_DIR="/Users/owen/CC workspace/Finance"
REMOTE="aliyun:/root/workspace/Finance"

sync_price() {
    echo "📥 同步价格数据 (云端→本地)..."
    rsync -avz "$REMOTE/data/price/" "$LOCAL_DIR/data/price/"
    echo "✅ 价格数据同步完成"
}

sync_all_data() {
    sync_price
    echo "📥 同步基本面数据..."
    rsync -avz "$REMOTE/data/fundamental/" "$LOCAL_DIR/data/fundamental/"
    echo "📥 同步数据库..."
    rsync -avz "$REMOTE/data/valuation.db" "$LOCAL_DIR/data/"
    echo "✅ 全部数据同步完成"
}

case "${1:---price}" in
    --price) sync_price ;;
    --all)   sync_all_data ;;
    *)
        echo "用法: $0 [--price|--all]"
        echo "  --price  只同步价格CSV (默认)"
        echo "  --all    同步所有数据 (价格+基本面+数据库)"
        exit 1
        ;;
esac
