<div align="center">

# Anyone to Skill

> *"선현들과 대화하고 싶으신가요? 누구와 대화하고 싶든, 누구의 사고 방식을 배우고 싶든, Anyone to Skill이 해결해 드립니다. 이제 일론 머스크, 젠슨 황, 공자와 직접 대화할 수 있습니다."*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

비디오, PDF, 채팅 기록, 전자책 등 어떤 자료든 넣으세요.<br>
시스템이 멘탈 모델, 의사 결정 휴리스틱, 표현 DNA를 추출합니다.<br>
설치 가능한 `SKILL.md`를 출력하여 모든 AI 도구에서 활성화할 수 있습니다.<br>

**누구든 설치 가능한 AI Skill로 증류하여 언제든 질문에 답하게 하세요.**

<br>

[데이터 소스](#지원되는-데이터-소스) · [설치](#설치) · [사용법](#사용법) · [실행 예시](#실행-예시) · [**简体中文**](README.md) · [**English**](README_EN.md) · [**繁體中文**](README_ZH_TW.md) · [**日本語**](README_JA.md)

</div>

---

## 실행 예시

> 이것은 단순히 유명인의 가면을 쓴 ChatGPT가 아닙니다. 모든 답변은 해당 인물의 구체적인 멘탈 모델과 표현 DNA를 적용합니다.

### 시나리오 1: Naval의 에너지 관리

```
사용자    ❯ 콘텐츠 제작, 책 집필, 1인 개발을 동시에 하고 싶은데 에너지가 부족합니다.

Naval     ❯ 당신은 세 가지 욕망을 나열했습니다. 모든 욕망은 당신이 불행해지기로 스스로와 맺은 계약입니다.
            에너지가 부족한 것이 아니라 계약이 너무 많은 것입니다.
            
            스스로에게 물어보세요: 어떤 일을 할 때 시간을 잊습니까?
            그곳에 당신의 '특정 지식'이 있습니다.
            
            셋 중 하나를 고르는 것이 아닙니다. 먼저 하나, 그다음 하나, 그리고 또 하나.
            직렬 복리이지, 병렬 소모가 아닙니다.
```

### 시나리오 2: 스티브 잡스의 제품 디자인

```
사용자    ❯ 새 제품에 15개의 새로운 기능을 추가했는데, 사용자들이 너무 복잡하다고 합니다. 어떻게 최적화해야 할까요?

Steve Jobs ❯ 14개를 잘라내세요.
             왜 제품에 쓰레기를 채워 넣습니까? 사용자가 진정으로 원하는 것이 무엇인지 모르기 때문에 양으로 무지를 덮으려는 것입니다.
             
             화이트보드로 돌아가세요. 스스로에게 물어보세요: 이 제품이 존재하는 단 하나의 이유는 무엇입니까?
             한 문장으로 설명할 수 없다면 만들지 마세요.
             
             단순함은 복잡함보다 어렵습니다. 생각을 명확하게 하고 단순하게 만들기 위해 열심히 노력해야 합니다.
```

### 시나리오 3: 일론 머스크의 비용 통제

```
사용자    ❯ 배터리 비용을 낮출 수 없습니다. 공급업체는 이것이 한계라고 말합니다.

Elon Musk ❯ 공급업체의 말은 헛소리입니다.
            제1원칙에서 생각하세요: 배터리는 무엇으로 만들어집니까? 탄소, 니켈, 알루미늄, 폴리머, 강철입니다.
            런던 금속 거래소에서 이 재료들의 현물 가격은 얼마입니까?
            
            직접 재료를 사서 직접 만든다면 비용이 얼마일까요?
            그 숫자가 공급업체의 견적보다 80% 낮다면, 그들은 당신에게 '바보 세금'을 청구하고 있는 것입니다.
            
            기존의 해결책을 받아들이지 마세요. 직접 만드세요.
```

---

## 증류된 인물 라이브러리

다음 증류된 Skill을 직접 설치할 수 있습니다:

| 인물 | 분야 | 설치 명령어 |
|------|------|-------------|
| [일론 머스크](https://github.com/OpenDemon/elon-musk-skill) | 기술 창업 · 제1원칙 | `npx skills add OpenDemon/elon-musk-skill` |
| [스티브 잡스](https://github.com/OpenDemon/steve-jobs-skill) | 제품 · 미니멀리즘 | `npx skills add OpenDemon/steve-jobs-skill` |
| [빌 게이츠](https://github.com/OpenDemon/bill-gates-skill) | 소프트웨어 전략 · 글로벌 헬스 | `npx skills add OpenDemon/bill-gates-skill` |
| [Naval](https://github.com/OpenDemon/naval-ravikant-skill) | 경제적 자유 · 특정 지식 | `npx skills add OpenDemon/naval-ravikant-skill` |
| [Andrej Karpathy](https://github.com/OpenDemon/andrej-karpathy-skill) | 딥러닝 · AI 교육 | `npx skills add OpenDemon/andrej-karpathy-skill` |
| [젠슨 황](https://github.com/OpenDemon/jensen-huang-skill) | 반도체 전략 · 가속주의 | `npx skills add OpenDemon/jensen-huang-skill` |
| [Dan Koe](https://github.com/OpenDemon/dan-koe-skill) | 1인 기업 · 퍼스널 브랜드 | `npx skills add OpenDemon/dan-koe-skill` |

---

## 사용법

### 방법 1: 터미널에서 직접 채팅 (권장)

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

### 방법 2: AI 코딩 도구에 설치

Claude Code나 Cursor 같은 도구를 사용한다면 직접 설치할 수 있습니다:

```bash
npx skills add OpenDemon/elon-musk-skill
```

설치 후 도구 내에서 직접 질문하세요: `일론 머스크의 관점에서 이 비즈니스 모델을 분석해 줘`

---

## 새로운 인물 증류하기

```bash
# 종속성 설치
pip install openai PyMuPDF python-docx yt-dlp beautifulsoup4 requests

# 방법 1: 로컬 파일
python scripts/distill.py --target "Dan Koe" --files video.mp4 book.pdf

# 방법 2: YouTube 채널 URL
python scripts/distill.py --url https://www.youtube.com/@DanKoeTalks

# 방법 3: 대화형 모드 (권장)
python scripts/distill.py
```

---

## 지원되는 데이터 소스

| 소스 | 상태 | 비고 |
|------|:----:|------|
| YouTube 채널/비디오 | ✅ | 자막 또는 오디오 전사 자동 다운로드 |
| 로컬 비디오/오디오 | ✅ | mp4, mp3, wav 등 지원 |
| PDF 문서 | ✅ | 텍스트 자동 추출 |
| Word 문서 | ✅ | docx 지원 |
| 채팅 기록 JSON | ✅ | 표준 내보내기 형식 지원 |
| 일반 텍스트/Markdown | ✅ | 직접 구문 분석 |

---

Created by [@OpenDemon](https://github.com/OpenDemon)
