<div align="center">

# Anyone to Skill

> *"Do you want to converse with the sages? Whether you want to talk to anyone or learn anyone's mental models, Anyone to Skill has you covered. Now, you can talk directly to Elon Musk, Jensen Huang, and Confucius."*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

Drop in videos, PDFs, chat logs, ebooks — any material.<br>
The system extracts mental models, decision heuristics, and voice DNA.<br>
Outputs an installable `SKILL.md` that activates in any AI tool.<br>

**Distill anyone into an installable AI Skill, ready to answer your questions anytime.**

<br>

[Data Sources](#supported-data-sources) · [Install](#installation) · [Usage](#usage) · [Examples](#examples) · [**简体中文**](README.md) · [**繁體中文**](README_ZH_TW.md) · [**日本語**](README_JA.md) · [**한국어**](README_KO.md)

</div>

---

## Examples

> This isn't just ChatGPT wearing a celebrity mask. Every response applies the specific mental models and voice DNA of the figure.

### Scenario 1: Naval on Energy Management

```
User      ❯ I want to do content creation, write a book, and be an indie hacker all at once, but I don't have enough energy.

Naval     ❯ You listed three desires. Every desire is a contract you make with yourself to be unhappy until you get what you want.
            It's not a lack of energy; it's too many contracts.
            
            Ask yourself: Which one makes you forget about time?
            That is where your specific knowledge lies.
            
            It's not pick one of three. It's one first, then the next, then the next.
            Sequential compounding, not parallel friction.
```

### Scenario 2: Steve Jobs on Product Design

```
User      ❯ Our new product has 15 new features, but users say it's too complex. How do we optimize it?

Steve Jobs ❯ Cut 14 of them.
             Why are you stuffing your product with garbage? Because you don't know what users actually want, so you try to cover up your ignorance with quantity.
             
             Go back to the whiteboard. Ask yourself: What is the single reason this product exists?
             If you can't explain it in one sentence, don't build it.
             
             Simple can be harder than complex. You have to work hard to get your thinking clean to make it simple.
```

### Scenario 3: Elon Musk on Cost Control

```
User      ❯ We can't lower our battery costs. The supplier says this is the absolute limit.

Elon Musk ❯ The supplier is talking nonsense.
            Think from first principles: What is a battery made of? Carbon, nickel, aluminum, polymers, steel.
            What is the spot market value of those materials on the London Metal Exchange?
            
            If you bought the materials yourself and built it yourself, what would it cost?
            If that number is 80% lower than the supplier's quote, they are charging you an idiot tax.
            
            Don't accept existing solutions. Build it yourself.
```

---

## Pre-distilled Figures

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

---

## Usage

### Method 1: Direct Terminal Chat (Recommended)

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

### Method 2: Install to AI Coding Tools

If you use tools like Claude Code or Cursor, you can install directly:

```bash
npx skills add OpenDemon/elon-musk-skill
```

Then ask in the tool: `Analyze this business model from Elon Musk's perspective`

---

## Distill a New Figure

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

## Supported Data Sources

| Source | Status | Notes |
|--------|:------:|-------|
| YouTube Channels/Videos | ✅ | Auto-downloads subtitles or audio transcripts |
| Local Video/Audio | ✅ | Supports mp4, mp3, wav, etc. |
| PDF Documents | ✅ | Auto-extracts text |
| Word Documents | ✅ | Supports docx |
| Chat Logs JSON | ✅ | Supports standard export formats |
| Plain Text/Markdown | ✅ | Direct parsing |

---

Created by [@OpenDemon](https://github.com/OpenDemon)
