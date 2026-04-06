<div align="center">

# Anyone to Skill

> *"你是否也想与先贤对话，无论你想和任何人对话，学习任何人的思维模式，Anyone to Skill都能满足你。现在，你可以直接和马斯克、黄仁勋、孔子对话了。"*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

丢进去视频、PDF、聊天记录、电子书——任何材料。<br>
系统提取心智模型、决策启发式、表达风格。<br>
输出一个可安装的 `SKILL.md`，在任何 AI 工具里激活。<br>

**把任何人蒸馏成可安装的 AI Skill，随时回答你的问题。**

<br>

[数据来源](#支持的数据来源) · [安装](#安装) · [使用](#使用) · [效果示例](#效果示例) · [**English**](README_EN.md) · [**繁體中文**](README_ZH_TW.md) · [**日本語**](README_JA.md) · [**한국어**](README_KO.md)

</div>

---

## 效果示例

> 这不是 ChatGPT 套了个名人面具。每段回应都在运用该人物的具体心智模型和表达 DNA。

### 场景一：Naval 谈精力管理

```
用户      ❯ 我同时想做自媒体、写书、做独立开发，精力完全不够

Naval     ❯ 你列了三个欲望。每个欲望都是你跟不快乐签的一份合同。
            不是精力不够，是合同太多。
            
            问你自己：哪一个做起来你会忘记时间？
            那个就是你的特定知识所在。
            
            不是三选一。是先一，再一，再一。
            串行复利，不是并行内耗。
```

### 场景二：乔布斯谈产品设计

```
用户      ❯ 我们的新产品加了 15 个新功能，但用户反馈说太复杂了，怎么优化？

Steve Jobs ❯ 砍掉 14 个。
             你为什么要在产品里塞满垃圾？是因为你不知道用户真正想要什么，所以你试图用数量来掩盖你的无知。
             
             回到白板前。问自己：这个产品存在的唯一理由是什么？
             如果你不能用一句话说清楚，那就不要做。
             
             简单比复杂更难。你必须努力让你的想法变得清晰，才能做到简单。
```

### 场景三：马斯克谈成本控制

```
用户      ❯ 我们的电池成本降不下来，供应商说已经是极限了。

Elon Musk ❯ 供应商说的是废话。
            用第一性原理来思考：电池是由什么组成的？碳、镍、铝、聚合物、钢。
            这些材料在伦敦金属交易所的现货价格是多少？
            
            如果你自己买材料，自己造，成本是多少？
            如果这个数字比供应商的报价低 80%，那就说明他们在收智商税。
            
            不要接受现有的解决方案。自己造。
```

---

## 已蒸馏人物库

你可以直接安装以下已经蒸馏好的人物 Skill：

| 人物 | 领域 | 安装命令 |
|------|------|---------|
| [马斯克](https://github.com/OpenDemon/elon-musk-skill) | 科技创业 · 第一性原理 | `npx skills add OpenDemon/elon-musk-skill` |
| [乔布斯](https://github.com/OpenDemon/steve-jobs-skill) | 产品设计 · 极简主义 | `npx skills add OpenDemon/steve-jobs-skill` |
| [比尔盖茨](https://github.com/OpenDemon/bill-gates-skill) | 软件战略 · 全球健康 | `npx skills add OpenDemon/bill-gates-skill` |
| [段永平](https://github.com/OpenDemon/duan-yongping-skill) | 价值投资 · 本分哲学 | `npx skills add OpenDemon/duan-yongping-skill` |
| [纳瓦尔](https://github.com/OpenDemon/naval-ravikant-skill) | 财富自由 · 特定知识 | `npx skills add OpenDemon/naval-ravikant-skill` |
| [张雪峰](https://github.com/OpenDemon/zhang-xue-feng-skill) | 教育规划 · 务实主义 | `npx skills add OpenDemon/zhang-xue-feng-skill` |
| [孔子](https://github.com/OpenDemon/kong-zi-skill) | 仁义礼学 · 修身齐家 | `npx skills add OpenDemon/kong-zi-skill` |
| [庄子](https://github.com/OpenDemon/zhuang-zi-skill) | 逍遥哲学 · 齐物论 | `npx skills add OpenDemon/zhuang-zi-skill` |
| [Karpathy](https://github.com/OpenDemon/andrej-karpathy-skill) | 深度学习 · AI 教育 | `npx skills add OpenDemon/andrej-karpathy-skill` |
| [黄仁勋](https://github.com/OpenDemon/jensen-huang-skill) | 芯片战略 · 加速主义 | `npx skills add OpenDemon/jensen-huang-skill` |
| [Dan Koe](https://github.com/OpenDemon/dan-koe-skill) | 一人企业 · 个人品牌 | `npx skills add OpenDemon/dan-koe-skill` |

---

## 使用

### 方式一：终端直接对话（推荐）

无需任何 AI 工具，直接在终端里和他们聊天：

```bash
git clone https://github.com/OpenDemon/anyone-to-skill
cd anyone-to-skill
pip install openai

# 设置你的 API Key（支持 OpenAI / Gemini / GLM智谱）
export OPENAI_API_KEY="sk-..."

# 启动聊天
python chat.py
```

### 方式二：安装到 AI 编程工具

如果你使用 Claude Code、Cursor 等工具，可以直接安装：

```bash
npx skills add OpenDemon/elon-musk-skill
```

安装后在工具内直接提问：`用马斯克的视角帮我分析这个商业模式`

---

## 自己蒸馏新人物

```bash
# 安装依赖
pip install openai PyMuPDF python-docx yt-dlp beautifulsoup4 requests

# 方式一：丢本地文件
python scripts/distill.py --target "Dan Koe" --files video.mp4 book.pdf

# 方式二：直接给 YouTube 频道
python scripts/distill.py --url https://www.youtube.com/@DanKoeTalks

# 方式三：交互模式（推荐新手）
python scripts/distill.py
```

---

## 支持的数据来源

| 来源 | 支持状态 | 备注 |
|------|:-------:|------|
| YouTube 频道/视频 | ✅ | 自动下载字幕或音频转录 |
| 本地视频/音频 | ✅ | 支持 mp4, mp3, wav 等 |
| PDF 文档 | ✅ | 自动提取文本 |
| Word 文档 | ✅ | 支持 docx |
| 聊天记录 JSON | ✅ | 支持标准导出格式 |
| 纯文本/Markdown | ✅ | 直接解析 |

---

Created by [@OpenDemon](https://github.com/OpenDemon)
