# Anyone to Skill — 一键安装脚本（Windows PowerShell）
# 用法：iwr -useb https://raw.githubusercontent.com/OpenDemon/anyone-to-skill/master/install.ps1 | iex

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "  ╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║         A N Y O N E   T O   S K I L L               ║" -ForegroundColor Cyan
Write-Host "  ║       一键安装脚本 · Windows PowerShell              ║" -ForegroundColor Cyan
Write-Host "  ╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ── 检查 Python ──────────────────────────────────────────────────────────────
Write-Host "  [1/4] 检查 Python 环境..." -ForegroundColor White

$python = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3") {
            $python = $cmd
            Write-Host "  ✓ 已找到 $ver" -ForegroundColor Green
            break
        }
    } catch {}
}

if (-not $python) {
    Write-Host "  ✗ 未找到 Python，请先安装 Python 3.9+" -ForegroundColor Red
    Write-Host "    下载地址：https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "    安装时请勾选 'Add Python to PATH'" -ForegroundColor Yellow
    exit 1
}

# ── 安装 pip 包 ───────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  [2/4] 安装 anyone2skill..." -ForegroundColor White
& $python -m pip install --quiet --upgrade "git+https://github.com/OpenDemon/anyone-to-skill.git"
Write-Host "  ✓ 安装完成" -ForegroundColor Green

# ── 配置 API Key ──────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  [3/4] 配置 API Key" -ForegroundColor White
Write-Host "  支持 OpenAI / Gemini / GLM（智谱），至少配置一个" -ForegroundColor Yellow
Write-Host ""

$configDir = Join-Path $env:USERPROFILE ".anyone2skill"
$configFile = Join-Path $configDir "config.json"

if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir | Out-Null
}

# 读取已有配置
$config = @{}
if (Test-Path $configFile) {
    try {
        $config = Get-Content $configFile | ConvertFrom-Json -AsHashtable
    } catch {
        $config = @{}
    }
}

function Prompt-Key {
    param($Name, $EnvKey, $Hint)
    $existing = $config[$EnvKey]
    if ($existing) {
        $masked = $existing.Substring(0, [Math]::Min(4, $existing.Length)) + "****" + $existing.Substring([Math]::Max(0, $existing.Length - 4))
        Write-Host "  ${Name}: 已配置 ($masked)" -ForegroundColor Green
        $new = Read-Host "  回车保留，或粘贴新 Key 替换"
        if ($new) { return $new } else { return $existing }
    } else {
        Write-Host "  ${Name}: 未配置" -ForegroundColor Yellow
        Write-Host "  获取地址：$Hint" -ForegroundColor Cyan
        $new = Read-Host "  粘贴 Key（直接回车跳过）"
        return $new
    }
}

$openaiKey = Prompt-Key "OpenAI" "OPENAI_API_KEY" "https://platform.openai.com/api-keys"
$geminiKey = Prompt-Key "Gemini" "GEMINI_API_KEY" "https://aistudio.google.com/app/apikey"
$glmKey    = Prompt-Key "GLM（智谱）" "GLM_API_KEY" "https://open.bigmodel.cn/usercenter/apikeys"

if ($openaiKey) { $config["OPENAI_API_KEY"] = $openaiKey }
if ($geminiKey) { $config["GEMINI_API_KEY"] = $geminiKey }
if ($glmKey)    { $config["GLM_API_KEY"]    = $glmKey    }

$config | ConvertTo-Json | Set-Content $configFile -Encoding UTF8
Write-Host "  ✓ 配置已保存到 $configFile" -ForegroundColor Green

# ── 完成 ──────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  [4/4] 安装完成！" -ForegroundColor White
Write-Host ""
Write-Host "  现在可以运行：" -ForegroundColor Green
Write-Host ""
Write-Host "    anyone2skill                    # 交互式选择人物" -ForegroundColor Cyan
Write-Host "    anyone2skill --person 马斯克    # 直接对话马斯克" -ForegroundColor Cyan
Write-Host "    anyone2skill --person Karpathy  # 直接对话 Karpathy" -ForegroundColor Cyan
Write-Host "    anyone2skill --api glm          # 指定使用 GLM API" -ForegroundColor Cyan
Write-Host ""
Write-Host "  如果命令未找到，请重新打开 PowerShell 窗口。" -ForegroundColor Yellow
Write-Host ""
