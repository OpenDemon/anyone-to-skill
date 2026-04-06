# Anyone to Skill

**把任何人蒸馏成可安装的 AI Skill。**

给一个 YouTube 频道链接、一堆 PDF、聊天记录、电子书——系统自动提取此人的心智模型、决策启发式、表达风格，输出一个可以让 AI 像他一样思考的 `SKILL.md`。

作者：[OPENDEMON](https://github.com/OpenDemon)

---

## 安装

```bash
npx skills add OpenDemon/anyone-to-skill
```

或手动克隆：

```bash
git clone https://github.com/OpenDemon/anyone-to-skill
cd anyone-to-skill
pip install openai PyMuPDF python-docx yt-dlp openai-whisper beautifulsoup4 requests
export OPENAI_API_KEY=sk-...
```

---

## 快速开始

### 交互模式（推荐）

```bash
python scripts/distill.py
```

启动后会看到：

```
  ╔═══════════════════════════════════════════════════════╗
  ║          A N Y O N E   T O   S K I L L               ║
  ║        把任何人蒸馏成可安装的 Skill                    ║
  ╚═══════════════════════════════════════════════════════╝

▶ 选择蒸馏模式:
    ● [1] 本地文件     — 丢入视频/PDF/聊天记录/电子书等任意文件
    ○ [2] YouTube 频道 — 给频道链接，自动采集并蒸馏（公开人物首选）
    ○ [3] NotebookLM   — 批量导入 YouTube 到 NotebookLM 再蒸馏
    ○ [q] 退出
```

### 非交互模式

```bash
# Mode 1：本地文件
python scripts/distill.py --target "乔布斯" --files interview.mp4 bio.pdf chats.json

# Mode 2：YouTube 频道一键蒸馏
python scripts/distill.py --url https://www.youtube.com/@DanKoeTalks

# Mode 3：自我蒸馏
python scripts/distill.py --target "我" --files my_chats.json notes.txt --self-mode
```

---

## 支持的输入格式

| 格式 | 说明 |
|------|------|
| `.mp4` `.mp3` `.mov` | 视频/音频，自动转录 |
| `.pdf` | PDF 文档，自动提取文本 |
| `.docx` `.txt` `.md` | 文字材料 |
| `.json` | 聊天记录（微信/Telegram/WhatsApp 导出格式） |
| `.epub` | 电子书 |
| YouTube URL | 频道主页或单个视频链接 |

---

## 工作原理

```
输入材料
    │
    ▼
Phase 0 · 多模态接入层
  视频 → Gemini/Whisper 转录
  PDF  → PyMuPDF 提取
  聊天 → 结构化解析
    │
    ▼
Phase 1 · 六路并行提取（6 个专项 Agent 同时运行）
  [著作Agent]   核心观点与论证结构
  [对话Agent]   访谈中的即兴表达与真实立场
  [表达Agent]   语言风格、隐喻、句式 DNA
  [外部Agent]   批评者视角与他者评价
  [决策Agent]   决策记录与行为模式
  [关系Agent]   关系记忆与角色切换
    │
    ▼
Phase 2 · 三重验证 + 知识图谱合成
  ✓ 跨域复现（2+ 个领域出现过）
  ✓ 有生成力（能推断对新问题的立场）
  ✓ 有排他性（不是所有聪明人都会这么想）
  保留内在张力，不强行调和矛盾
    │
    ▼
Phase 3 · Skill 组装
  Persona → Mental Models → Heuristics → Voice DNA → Boundaries
    │
    ▼
Phase 4 · QA 验证闭环（最多 3 次重试）
  Sanity Check  — 3 个已知问题方向一致
  Edge Case     — 1 个未知问题表现适度不确定
  Voice Check   — 风格高度还原
    │
    ▼
输出：SKILL.md + qa_report.json + meta.json
```

---

## 视频分析策略

系统内置四种视频分析策略，交互模式下可自由选择：

| 策略 | 原理 | 速度 | 费用 |
|------|------|------|------|
| `gemini` | Gemini 2.5 Flash 直接理解 YouTube URL | 最快 | Gemini API |
| `whisper_api` | yt-dlp 下载音频 + OpenAI Whisper 转录 | 中等 | OpenAI API |
| `whisper_local` | yt-dlp 下载音频 + 本地 Whisper 模型 | 较慢 | 免费（离线） |
| `subtitles` | youtube_transcript_api 获取字幕 | 最快 | 免费 |
| `auto` | 依次尝试以上策略，自动降级 | — | — |

---

## 输出结构

```
output/{target_slug}/
├── SKILL.md          ← 可安装的 Skill（直接复制到 ~/.skills/）
├── qa_report.json    ← QA 验证报告（含质量分）
├── meta.json         ← 元数据（来源、版本、时间）
├── corpus/           ← 处理后的语料文件
└── research/         ← 中间提取结果和知识图谱
```

---

## 示例输出

- [Dan Koe](examples/dan-koe/SKILL.md) — YouTube 创作者，一人企业思想家（QA: 95/100）

---

## 环境变量

```bash
OPENAI_API_KEY=sk-...   # 必填，用于 GPT 分析和 Whisper API
```

---

## 项目结构

```
anyone-to-skill/
├── SKILL.md                          ← Skill 本体（触发词：蒸馏XX / 造skill）
├── README.md
├── references/
│   └── extraction-framework.md       ← 三重验证规则 + QA 评分标准
├── examples/
│   └── dan-koe/SKILL.md              ← Dan Koe 示例（QA 95/100）
└── scripts/
    ├── distill.py                    ← 主入口（交互式 CLI）
    ├── analyze_video.py              ← 开源视频分析（Gemini/Whisper/字幕）
    ├── ingest.py                     ← 多模态数据接入层
    ├── extract.py                    ← 六路并行 Agent + 知识图谱合成
    ├── assemble.py                   ← Skill 组装 + QA 验证闭环
    ├── crawl.py                      ← YouTube 频道采集
    └── notebooklm.py                 ← NotebookLM 批量导入自动化
```

---

## License

MIT
