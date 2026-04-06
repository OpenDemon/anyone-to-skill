#!/bin/bash
# Anyone to Skill — 一键安装脚本（Mac / Linux）
# 用法：curl -fsSL https://raw.githubusercontent.com/OpenDemon/anyone-to-skill/master/install.sh | bash

set -e

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${CYAN}${BOLD}  ╔══════════════════════════════════════════════════════╗"
echo -e "  ║         A N Y O N E   T O   S K I L L               ║"
echo -e "  ║       一键安装脚本 · Mac / Linux                     ║"
echo -e "  ╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# ── 检查 Python ──────────────────────────────────────────────────────────────
echo -e "  ${BOLD}[1/4] 检查 Python 环境...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON=python3
    PY_VER=$(python3 --version 2>&1)
    echo -e "  ${GREEN}✓ 已找到 ${PY_VER}${NC}"
elif command -v python &>/dev/null; then
    PYTHON=python
    PY_VER=$(python --version 2>&1)
    echo -e "  ${GREEN}✓ 已找到 ${PY_VER}${NC}"
else
    echo -e "  ${RED}✗ 未找到 Python，请先安装 Python 3.9+${NC}"
    echo -e "  ${YELLOW}  下载地址：https://www.python.org/downloads/${NC}"
    exit 1
fi

# ── 安装 pip 包 ───────────────────────────────────────────────────────────────
echo ""
echo -e "  ${BOLD}[2/4] 安装 anyone2skill...${NC}"
$PYTHON -m pip install --quiet --upgrade "git+https://github.com/OpenDemon/anyone-to-skill.git"
echo -e "  ${GREEN}✓ 安装完成${NC}"

# ── 配置 API Key ──────────────────────────────────────────────────────────────
echo ""
echo -e "  ${BOLD}[3/4] 配置 API Key${NC}"
echo -e "  ${YELLOW}支持 OpenAI / Gemini / GLM（智谱），至少配置一个${NC}"
echo ""

CONFIG_DIR="$HOME/.anyone2skill"
CONFIG_FILE="$CONFIG_DIR/config.json"
mkdir -p "$CONFIG_DIR"

# 读取已有配置
EXISTING_OPENAI=""
EXISTING_GEMINI=""
EXISTING_GLM=""
if [ -f "$CONFIG_FILE" ]; then
    EXISTING_OPENAI=$(python3 -c "import json; d=json.load(open('$CONFIG_FILE')); print(d.get('OPENAI_API_KEY',''))" 2>/dev/null || echo "")
    EXISTING_GEMINI=$(python3 -c "import json; d=json.load(open('$CONFIG_FILE')); print(d.get('GEMINI_API_KEY',''))" 2>/dev/null || echo "")
    EXISTING_GLM=$(python3 -c "import json; d=json.load(open('$CONFIG_FILE')); print(d.get('GLM_API_KEY',''))" 2>/dev/null || echo "")
fi

prompt_key() {
    local name="$1"
    local env_key="$2"
    local hint="$3"
    local existing="$4"

    if [ -n "$existing" ]; then
        masked="${existing:0:4}****${existing: -4}"
        echo -e "  ${GREEN}${name}: 已配置 (${masked})${NC}"
        echo -n -e "  ${CYAN}回车保留，或粘贴新 Key 替换 > ${NC}"
        read new_key
        if [ -n "$new_key" ]; then
            echo "$new_key"
        else
            echo "$existing"
        fi
    else
        echo -e "  ${YELLOW}${name}: 未配置${NC}"
        echo -e "  ${CYAN}获取地址：${hint}${NC}"
        echo -n -e "  ${CYAN}粘贴 Key（直接回车跳过）> ${NC}"
        read new_key
        echo "$new_key"
    fi
}

OPENAI_KEY=$(prompt_key "OpenAI" "OPENAI_API_KEY" "https://platform.openai.com/api-keys" "$EXISTING_OPENAI")
GEMINI_KEY=$(prompt_key "Gemini" "GEMINI_API_KEY" "https://aistudio.google.com/app/apikey" "$EXISTING_GEMINI")
GLM_KEY=$(prompt_key "GLM（智谱）" "GLM_API_KEY" "https://open.bigmodel.cn/usercenter/apikeys" "$EXISTING_GLM")

# 保存配置
python3 - <<EOF
import json, os
config = {}
try:
    with open('$CONFIG_FILE') as f:
        config = json.load(f)
except:
    pass
if '$OPENAI_KEY': config['OPENAI_API_KEY'] = '$OPENAI_KEY'
if '$GEMINI_KEY': config['GEMINI_API_KEY'] = '$GEMINI_KEY'
if '$GLM_KEY': config['GLM_API_KEY'] = '$GLM_KEY'
with open('$CONFIG_FILE', 'w') as f:
    json.dump(config, f, indent=2)
print('  配置已保存到 $CONFIG_FILE')
EOF

# ── 完成 ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "  ${BOLD}[4/4] 安装完成！${NC}"
echo ""
echo -e "  ${GREEN}${BOLD}现在可以运行：${NC}"
echo ""
echo -e "  ${CYAN}  anyone2skill${NC}               # 交互式选择人物"
echo -e "  ${CYAN}  anyone2skill --person 马斯克${NC}  # 直接对话马斯克"
echo -e "  ${CYAN}  anyone2skill --person Karpathy${NC} # 直接对话 Karpathy"
echo -e "  ${CYAN}  anyone2skill --api glm${NC}       # 指定使用 GLM API"
echo ""
echo -e "  ${YELLOW}如果命令未找到，请重新打开终端或运行：${NC}"
echo -e "  ${CYAN}  source ~/.bashrc  # 或 source ~/.zshrc${NC}"
echo ""
