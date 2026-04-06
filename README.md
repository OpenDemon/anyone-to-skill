<div align="center">

# Anyone to Skill

> *"你崇拜的那个人，你永远约不到他。你想学的那套思维，淹没在几千小时的视频里。你的偶像在讲台上说了一辈子，你却只记住了一句金句。"*

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

[**简体中文**](#简体中文) · [**English**](#english) · [**繁體中文**](#繁體中文) · [**日本語**](#日本語) · [**한국어**](#한국어)

</div>

---

## 简体中文

### 效果示例

> 这不是 ChatGPT 套了个名人面具。每段回应都在运用该人物的具体心智模型和表达 DNA。

**问：我同时想做自媒体、写书、做独立开发，精力完全不够**

```
用户      ❯ 我同时想做自媒体、写书、做独立开发，精力完全不够

Naval     ❯ 你列了三个欲望。每个欲望都是你跟不快乐签的一份合同。
            不是精力不够，是合同太多。
            
            问你自己：哪一个做起来你会忘记时间？
            那个就是你的特定知识所在。
            
            不是三选一。是先一，再一，再一。
            串行复利，不是并行内耗。
```

### 已蒸馏人物库

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

### 终端直接对话

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

### 自己蒸馏新人物

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

## English

### Example

> This isn't just ChatGPT wearing a celebrity mask. Every response applies the specific mental models and voice DNA of the figure.

**Q: I want to do content creation, write a book, and be an indie hacker all at once, but I don't have enough energy.**

```
User      ❯ I want to do content creation, write a book, and be an indie hacker all at once, but I don't have enough energy.

Naval     ❯ You listed three desires. Every desire is a contract you make with yourself to be unhappy until you get what you want.
            It's not a lack of energy; it's too many contracts.
            
            Ask yourself: Which one makes you forget about time?
            That is where your specific knowledge lies.
            
            It's not pick one of three. It's one first, then the next, then the next.
            Sequential compounding, not parallel friction.
```

### Pre-distilled Figures

You can directly install these pre-distilled Skills:

| Figure | Domain | Install Command |
|--------|--------|-----------------|
| [Elon Musk](https://github.com/OpenDemon/elon-musk-skill) | Tech · First Principles | `npx skills add OpenDemon/elon-musk-skill` |
| [Steve Jobs](https://github.com/OpenDemon/steve-jobs-skill) | Product · Minimalism | `npx skills add OpenDemon/steve-jobs-skill` |
| [Bill Gates](https://github.com/OpenDemon/bill-gates-skill) | Software · Global Health | `npx skills add OpenDemon/bill-gates-skill` |
| [Naval](https://github.com/OpenDemon/naval-ravikant-skill) | Wealth · Specific Knowledge | `npx skills add OpenDemon/naval-ravikant-skill` |
| [Andrej Karpathy](https://github.com/OpenDemon/andrej-karpathy-skill) | Deep Learning · AI Ed | `npx skills add OpenDemon/andrej-karpathy-skill` |
| [Jensen Huang](https://github.com/OpenDemon/jensen-huang-skill) | Chips · Accelerationism | `npx skills add OpenDemon/jensen-huang-skill` |
| [Dan Koe](https://github.com/OpenDemon/dan-koe-skill) | One-Person Biz · Brand | `npx skills add OpenDemon/dan-koe-skill` |

### Direct Terminal Chat

Chat with them directly in your terminal without any AI tools:

```bash
git clone https://github.com/OpenDemon/anyone-to-skill
cd anyone-to-skill
pip install openai

# Set your API Key (Supports OpenAI / Gemini / GLM)
export OPENAI_API_KEY="sk-..."

# Start chatting
python chat.py
```

### Distill a New Figure

```bash
# Install dependencies
pip install openai PyMuPDF python-docx yt-dlp beautifulsoup4 requests

# Method 1: Local files
python scripts/distill.py --target "Dan Koe" --files video.mp4 book.pdf

# Method 2: YouTube Channel URL
python scripts/distill.py --url https://www.youtube.com/@DanKoeTalks

# Method 3: Interactive Mode (Recommended)
python scripts/distill.py
```

---

## 繁體中文

### 效果示例

> 這不是 ChatGPT 套了個名人面具。每段回應都在運用該人物的具體心智模型和表達 DNA。

**問：我同時想做自媒體、寫書、做獨立開發，精力完全不夠**

```
用戶      ❯ 我同時想做自媒體、寫書、做獨立開發，精力完全不夠

Naval     ❯ 你列了三個慾望。每個慾望都是你跟不快樂簽的一份合約。
            不是精力不夠，是合約太多。
            
            問你自己：哪一個做起來你會忘記時間？
            那個就是你的特定知識所在。
            
            不是三選一。是先一，再一，再一。
            串行複利，不是並行內耗。
```

### 終端直接對話

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

---

## 日本語

### 実行例

> これは単に有名人のマスクを被った ChatGPT ではありません。すべての回答は、その人物の具体的なメンタルモデルと表現の DNA を適用しています。

**問：コンテンツ制作、執筆、個人開発を同時にやりたいのですが、エネルギーが足りません。**

```
ユーザー  ❯ コンテンツ制作、執筆、個人開発を同時にやりたいのですが、エネルギーが足りません。

Naval     ❯ あなたは3つの欲望を挙げました。すべての欲望は、あなたが不幸になるために自分と結んだ契約です。
            エネルギーが足りないのではなく、契約が多すぎるのです。
            
            自分に問いかけてください：どれをやっている時、時間を忘れますか？
            そこにあなたの「特定の知識」があります。
            
            3つから1つを選ぶのではありません。まず1つ、次に1つ、そしてまた1つ。
            直列の複利であり、並列の消耗ではありません。
```

### ターミナルで直接チャット

AI ツールなしで、ターミナルから直接彼らとチャットできます：

```bash
git clone https://github.com/OpenDemon/anyone-to-skill
cd anyone-to-skill
pip install openai

# API Key を設定（OpenAI / Gemini / GLM 対応）
export OPENAI_API_KEY="sk-..."

# チャットを開始
python chat.py
```

---

## 한국어

### 실행 예시

> 이것은 단순히 유명인의 가면을 쓴 ChatGPT가 아닙니다. 모든 답변은 해당 인물의 구체적인 멘탈 모델과 표현 DNA를 적용합니다.

**문: 콘텐츠 제작, 책 집필, 1인 개발을 동시에 하고 싶은데 에너지가 부족합니다.**

```
사용자    ❯ 콘텐츠 제작, 책 집필, 1인 개발을 동시에 하고 싶은데 에너지가 부족합니다.

Naval     ❯ 당신은 세 가지 욕망을 나열했습니다. 모든 욕망은 당신이 불행해지기로 스스로와 맺은 계약입니다.
            에너지가 부족한 것이 아니라 계약이 너무 많은 것입니다.
            
            스스로에게 물어보세요: 어떤 일을 할 때 시간을 잊습니까?
            그곳에 당신의 '특정 지식'이 있습니다.
            
            셋 중 하나를 고르는 것이 아닙니다. 먼저 하나, 그다음 하나, 그리고 또 하나.
            직렬 복리이지, 병렬 소모가 아닙니다.
```

### 터미널에서 직접 채팅

AI 도구 없이 터미널에서 직접 그들과 채팅하세요:

```bash
git clone https://github.com/OpenDemon/anyone-to-skill
cd anyone-to-skill
pip install openai

# API Key 설정 (OpenAI / Gemini / GLM 지원)
export OPENAI_API_KEY="sk-..."

# 채팅 시작
python chat.py
```
