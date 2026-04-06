<div align="center">

# Anyone to Skill

> *"你是否也想與先賢對話，無論你想和任何人對話，學習任何人的思維模式，Anyone to Skill都能滿足你。現在，你可以直接和馬斯克、黃仁勳、孔子對話了。"*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

丟進去影片、PDF、聊天記錄、電子書——任何材料。<br>
系統提取心智模型、決策啟發式、表達風格。<br>
輸出一個可安裝的 `SKILL.md`，在任何 AI 工具裡啟動。<br>

**把任何人蒸餾成可安裝的 AI Skill，隨時回答你的問題。**

<br>

[數據來源](#支持的數據來源) · [安裝](#安裝) · [使用](#使用) · [效果示例](#效果示例) · [**简体中文**](README.md) · [**English**](README_EN.md) · [**日本語**](README_JA.md) · [**한국어**](README_KO.md)

</div>

---

## 效果示例

> 這不是 ChatGPT 套了個名人面具。每段回應都在運用該人物的具體心智模型和表達 DNA。

### 場景一：Naval 談精力管理

```
用戶      ❯ 我同時想做自媒體、寫書、做獨立開發，精力完全不夠

Naval     ❯ 你列了三個慾望。每個慾望都是你跟不快樂簽的一份合約。
            不是精力不夠，是合約太多。
            
            問你自己：哪一個做起來你會忘記時間？
            那個就是你的特定知識所在。
            
            不是三選一。是先一，再一，再一。
            串行複利，不是並行內耗。
```

### 場景二：賈伯斯談產品設計

```
用戶      ❯ 我們的新產品加了 15 個新功能，但用戶反饋說太複雜了，怎麼優化？

Steve Jobs ❯ 砍掉 14 個。
             你為什麼要在產品裡塞滿垃圾？是因為你不知道用戶真正想要什麼，所以你試圖用數量來掩蓋你的無知。
             
             回到白板前。問自己：這個產品存在的唯一理由是什麼？
             如果你不能用一句話說清楚，那就不要做。
             
             簡單比複雜更難。你必須努力讓你的想法變得清晰，才能做到簡單。
```

### 場景三：馬斯克談成本控制

```
用戶      ❯ 我們的電池成本降不下來，供應商說已經是極限了。

Elon Musk ❯ 供應商說的是廢話。
            用第一性原理來思考：電池是由什麼組成的？碳、鎳、鋁、聚合物、鋼。
            這些材料在倫敦金屬交易所的現貨價格是多少？
            
            如果你自己買材料，自己造，成本是多少？
            如果這個數字比供應商的報價低 80%，那就說明他們在收智商稅。
            
            不要接受現有的解決方案。自己造。
```

---

## 已蒸餾人物庫

你可以直接安裝以下已經蒸餾好的人物 Skill：

| 人物 | 領域 | 安裝命令 |
|------|------|---------|
| [馬斯克](https://github.com/OpenDemon/elon-musk-skill) | 科技創業 · 第一性原理 | `npx skills add OpenDemon/elon-musk-skill` |
| [賈伯斯](https://github.com/OpenDemon/steve-jobs-skill) | 產品設計 · 極簡主義 | `npx skills add OpenDemon/steve-jobs-skill` |
| [比爾蓋茲](https://github.com/OpenDemon/bill-gates-skill) | 軟體戰略 · 全球健康 | `npx skills add OpenDemon/bill-gates-skill` |
| [段永平](https://github.com/OpenDemon/duan-yongping-skill) | 價值投資 · 本分哲學 | `npx skills add OpenDemon/duan-yongping-skill` |
| [納瓦爾](https://github.com/OpenDemon/naval-ravikant-skill) | 財富自由 · 特定知識 | `npx skills add OpenDemon/naval-ravikant-skill` |
| [張雪峰](https://github.com/OpenDemon/zhang-xue-feng-skill) | 教育規劃 · 務實主義 | `npx skills add OpenDemon/zhang-xue-feng-skill` |
| [孔子](https://github.com/OpenDemon/kong-zi-skill) | 仁義禮學 · 修身齊家 | `npx skills add OpenDemon/kong-zi-skill` |
| [莊子](https://github.com/OpenDemon/zhuang-zi-skill) | 逍遙哲學 · 齊物論 | `npx skills add OpenDemon/zhuang-zi-skill` |
| [Karpathy](https://github.com/OpenDemon/andrej-karpathy-skill) | 深度學習 · AI 教育 | `npx skills add OpenDemon/andrej-karpathy-skill` |
| [黃仁勳](https://github.com/OpenDemon/jensen-huang-skill) | 晶片戰略 · 加速主義 | `npx skills add OpenDemon/jensen-huang-skill` |
| [Dan Koe](https://github.com/OpenDemon/dan-koe-skill) | 一人企業 · 個人品牌 | `npx skills add OpenDemon/dan-koe-skill` |

---

## 使用

### 方式一：終端直接對話（推薦）

無需任何 AI 工具，直接在終端機裡和他們聊天：

```bash
git clone https://github.com/OpenDemon/anyone-to-skill
cd anyone-to-skill
pip install openai

# 設定你的 API Key（支援 OpenAI / Gemini / GLM智譜）
export OPENAI_API_KEY="sk-..."

# 啟動聊天
python chat.py
```

### 方式二：安裝到 AI 程式設計工具

如果你使用 Claude Code、Cursor 等工具，可以直接安裝：

```bash
npx skills add OpenDemon/elon-musk-skill
```

安裝後在工具內直接提問：`用馬斯克的視角幫我分析這個商業模式`

---

## 自己蒸餾新人物

```bash
# 安裝依賴
pip install openai PyMuPDF python-docx yt-dlp beautifulsoup4 requests

# 方式一：丟本地文件
python scripts/distill.py --target "Dan Koe" --files video.mp4 book.pdf

# 方式二：直接給 YouTube 頻道
python scripts/distill.py --url https://www.youtube.com/@DanKoeTalks

# 方式三：交互模式（推薦新手）
python scripts/distill.py
```

---

## 支持的數據來源

| 來源 | 支持狀態 | 備註 |
|------|:-------:|------|
| YouTube 頻道/影片 | ✅ | 自動下載字幕或音訊轉錄 |
| 本地影片/音訊 | ✅ | 支援 mp4, mp3, wav 等 |
| PDF 文件 | ✅ | 自動提取文本 |
| Word 文件 | ✅ | 支援 docx |
| 聊天記錄 JSON | ✅ | 支援標準導出格式 |
| 純文本/Markdown | ✅ | 直接解析 |

---

Created by [@OpenDemon](https://github.com/OpenDemon)
