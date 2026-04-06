---
name: anyone-to-skill
description: |
  将任意多媒体材料（视频、音频、PDF、电子书、聊天记录等）蒸馏为可安装的 SKILL.md。
  触发条件：用户说「造skill」「蒸馏XX」「把这些材料做成skill」「分析这个视频/文件生成skill」，
  或上传文件并要求提取某人的思维模式、决策风格、认知框架时。
---

# Anyone to Skill · 多模态认知蒸馏引擎

将任意多媒体材料蒸馏为可安装的 AI Skill，支持视频、PDF、聊天记录、电子书等任意格式。

## 工作流程

### Step 1: 确认输入

收集以下信息（如用户未提供则询问）：
- **目标人物**：要蒸馏谁？（人名、主题、或"我自己"）
- **输入材料**：文件路径、URL 或已上传的文件
- **用途**：思维顾问 / 决策参考 / 角色扮演 / 自我复盘

### Step 2: 运行蒸馏流水线

```bash
python /home/ubuntu/skills/anyone-to-skill/scripts/distill.py \
  --target "目标人物名称" \
  --files 文件1 文件2 URL1 \
  --output ./output
```

自我蒸馏模式（用户上传自己的材料）：
```bash
python /home/ubuntu/skills/anyone-to-skill/scripts/distill.py \
  --target "我" \
  --files 聊天记录.json 笔记.txt \
  --self-mode
```

流水线自动执行：
1. **数据接入**：解析视频/PDF/聊天记录，统一格式化语料
2. **6 路并行提取**：著作分析、对话分析、表达 DNA、他者视角、决策记录、关系记忆
3. **知识图谱合成**：三重验证（跨域复现 + 有生成力 + 有排他性）
4. **Skill 组装**：生成 SKILL.md（Persona + 心智模型 + 决策启发式 + 表达 DNA + 诚实边界）
5. **QA 验证闭环**：Sanity Check + Edge Case + Voice Check，失败自动重试（最多 3 次）

### Step 3: 处理输出

流水线完成后，输出目录结构：
```
output/{target_slug}/
├── SKILL.md         ← 最终可安装的 Skill
├── qa_report.json   ← QA 验证报告（含质量分）
├── meta.json        ← 元数据（版本、来源、时间）
├── corpus/          ← 处理后的语料
└── research/        ← 知识图谱和提取结果
```

将生成的 `SKILL.md` 路径发送给用户（系统会自动打包为可安装的 `.skill` 文件）。

### Step 4: 质量把关

如果 QA 质量分 < 70，主动告知用户并建议：
- 补充更多材料（尤其是对话/访谈类）
- 指定更精确的目标人物名称
- 运行 `--self-mode` 进行自我蒸馏时，确保聊天记录包含足够的决策场景

## 支持的输入格式

| 格式 | 示例 | 说明 |
|------|------|------|
| 视频 | `.mp4`, `.mkv`, `.mov` | 自动转录，提取声学特征 |
| 音频 | `.mp3`, `.wav`, `.m4a` | 直接转录 |
| 在线视频 | YouTube/B站 URL | 自动下载并转录 |
| PDF | `.pdf` | 保留标题层级结构 |
| 电子书 | `.epub`, `.txt` | 保留章节结构 |
| Word 文档 | `.docx` | 保留段落层级 |
| 聊天记录 | `.json`, `.txt` | 支持微信/Telegram/WhatsApp 导出格式 |
| Markdown | `.md` | 直接处理 |

## 依赖安装

```bash
pip install openai PyMuPDF python-docx yt-dlp openai-whisper beautifulsoup4
```

## 详细方法论

见 `references/extraction-framework.md`（三重验证规则、知识图谱构建规范、QA 评分标准）。
