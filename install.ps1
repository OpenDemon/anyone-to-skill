# Anyone to Skill - One-click installer for Windows PowerShell
# Usage: iwr -useb https://raw.githubusercontent.com/OpenDemon/anyone-to-skill/master/install.ps1 | iex
# Version: 1.3

# Force UTF-8 output to avoid garbled text
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "  +------------------------------------------------------+" -ForegroundColor Cyan
Write-Host "  |         A N Y O N E   T O   S K I L L               |" -ForegroundColor Cyan
Write-Host "  |         Windows PowerShell Installer                 |" -ForegroundColor Cyan
Write-Host "  +------------------------------------------------------+" -ForegroundColor Cyan
Write-Host ""

# - Step 1: Check Python -
Write-Host "  [1/4] Checking Python..." -ForegroundColor White

$python = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3") {
            $python = $cmd
            Write-Host "  OK  Found $ver" -ForegroundColor Green
            break
        }
    } catch {}
}

if (-not $python) {
    Write-Host "  ERR Python not found. Please install Python 3.9+ first." -ForegroundColor Red
    Write-Host "      Download: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "      NOTE: Check 'Add Python to PATH' during install." -ForegroundColor Yellow
    exit 1
}

# - Step 2: Install package -
Write-Host ""
Write-Host "  [2/4] Installing anyone2skill..." -ForegroundColor White
& $python -m pip install --quiet --upgrade "git+https://github.com/OpenDemon/anyone-to-skill.git"
Write-Host "  OK  Installed successfully." -ForegroundColor Green

# - Step 3: Configure API Key -
Write-Host ""
Write-Host "  [3/4] Configure API Key" -ForegroundColor White
Write-Host "  Supports OpenAI / Gemini / GLM. Configure at least one." -ForegroundColor Yellow
Write-Host ""

$homeDir = if ($env:USERPROFILE) { $env:USERPROFILE } elseif ($env:HOME) { $env:HOME } else { $env:USERPROFILE }
$configDir = Join-Path $homeDir ".anyone2skill"
$configFile = Join-Path $configDir "config.json"

if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir | Out-Null
}

$config = @{}
if (Test-Path $configFile) {
    try {
        $raw = Get-Content $configFile -Raw -Encoding UTF8
        $config = $raw | ConvertFrom-Json -AsHashtable
    } catch {
        $config = @{}
    }
}

function Prompt-Key {
    param($Label, $EnvKey, $Hint)
    $existing = $config[$EnvKey]
    if ($existing) {
        $len = $existing.Length
        $masked = $existing.Substring(0, [Math]::Min(4, $len)) + "****" + $existing.Substring([Math]::Max(0, $len - 4))
        Write-Host "  $Label : already set ($masked)" -ForegroundColor Green
        $new = Read-Host "  Press Enter to keep, or paste new key to replace"
        if ($new -and $new.Trim()) { return $new.Trim() } else { return $existing }
    } else {
        Write-Host "  $Label : not set" -ForegroundColor Yellow
        Write-Host "  Get key: $Hint" -ForegroundColor Cyan
        $new = Read-Host "  Paste key (Enter to skip)"
        if ($new) { return $new.Trim() } else { return "" }
    }
}

$openaiKey = Prompt-Key "OpenAI    " "OPENAI_API_KEY" "https://platform.openai.com/api-keys"
$geminiKey = Prompt-Key "Gemini    " "GEMINI_API_KEY" "https://aistudio.google.com/app/apikey"
$glmKey    = Prompt-Key "GLM (Zhipu)" "GLM_API_KEY"  "https://open.bigmodel.cn/usercenter/apikeys"

if ($openaiKey) { $config["OPENAI_API_KEY"] = $openaiKey }
if ($geminiKey) { $config["GEMINI_API_KEY"] = $geminiKey }
if ($glmKey)    { $config["GLM_API_KEY"]    = $glmKey    }

$config | ConvertTo-Json | Set-Content $configFile -Encoding UTF8
Write-Host "  OK  Config saved to $configFile" -ForegroundColor Green

# - Step 4: Done -
Write-Host ""
Write-Host "  [4/4] Done! Now run:" -ForegroundColor White
Write-Host ""
Write-Host "    anyone2skill                    # interactive mode" -ForegroundColor Cyan
Write-Host "    anyone2skill --person Musk      # chat with Elon Musk" -ForegroundColor Cyan
Write-Host "    anyone2skill --person Karpathy  # chat with Karpathy" -ForegroundColor Cyan
Write-Host "    anyone2skill --api glm          # use GLM API" -ForegroundColor Cyan
Write-Host ""
Write-Host "  If 'anyone2skill' is not found, reopen PowerShell and try again." -ForegroundColor Yellow
Write-Host ""
