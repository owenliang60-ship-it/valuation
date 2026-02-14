#!/bin/bash
# 周度 RS Universe Scan wrapper - 加载环境变量
source /root/workspace/Finance/.env 2>/dev/null
cd /root/workspace/Finance
python3 scripts/rs_universe_scan.py
