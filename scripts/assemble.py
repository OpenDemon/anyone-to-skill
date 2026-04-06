"""
assemble.py — Skill 组装与 QA 验证闭环（Phase 3-4）

Phase 3: 从知识图谱生成结构化的 SKILL.md
Phase 4: 意图驱动的 QA 验证（Sanity Check + Edge Case + Voice Check）
         失败则打回重新调整，最多重试 3 次
"""

import os
import json
import re
from pathlib import Path
from openai import OpenAI

client = OpenAI()
MODEL = "gpt-4.1-mini"
MAX_QA_RETRIES = 3


def log(msg: str):
    print(f"[assemble] {msg}", flush=True)


# ─── Phase 3: Skill 组装 ──────────────────────────────────────────────────────

ASSEMBLY_PROMPT = """你是「Skill 架构师」。
你将收到一个人物的知识图谱，需要将其组装为一个可执行的 SKILL.md 文件。

SKILL.md 的结构必须严格遵循以下格式：

```
---
name: {slug}
description: |
  {一句话描述：这个 Skill 是谁，能做什么，何时触发}
---

# {人物名} · 认知操作系统

## 核心人格（Persona）
{2-3 段，描述这个人的核心性格特质，用第一人称或第三人称均可，但要有辨识度}

## 心智模型（Mental Models）
{3-7 个通过三重验证的心智模型，每个包含：名称、一句话描述、典型应用场景}

## 决策启发式（Decision Heuristics）
{5-10 条决策规则，格式：「在[情境]时，我倾向于[行动]，因为[底层逻辑]」}

## 表达 DNA（Voice & Style）
{句式特征、标志性词汇、禁忌词、幽默风格，附一段示例文本}

## 价值观与反模式（Values & Anti-patterns）
{核心价值观 3-5 条，以及明确的反模式（什么是这个人绝对不会做的）}

## 诚实边界（Honest Limits）
{至少 3 条：这个 Skill 做不到的事、信息盲区、不确定的领域}

## 内在张力（Internal Tensions）
{保留真实的矛盾，不强行调和，每条注明类型：时间性/领域性/本质性}
```

重要原则：
- 用第一人称写作（"我认为..."），让 Skill 像一个真实的人在说话
- 每个心智模型必须有具体的应用场景，不能只是抽象概念
- 诚实边界是质量的核心，不能省略
- 内在张力让 Skill 更真实，不能删除
- 总长度控制在 400-500 行以内"""


def assemble_skill(graph: dict, target_name: str, extra_feedback: str = "") -> str:
    """从知识图谱生成 SKILL.md 内容"""
    log(f"Phase 3: 组装 Skill for {target_name}...")
    
    slug = re.sub(r'[^\w\-]', '-', target_name.lower().strip())
    
    graph_text = json.dumps(graph, ensure_ascii=False, indent=2)
    
    feedback_section = ""
    if extra_feedback:
        feedback_section = f"\n\n上一次 QA 验证失败，请根据以下反馈修正：\n{extra_feedback}"
    
    user_content = f"""目标人物：{target_name}
Skill slug：{slug}

知识图谱：
{graph_text[:12000]}
{feedback_section}

请生成完整的 SKILL.md 内容（包含 YAML frontmatter）。"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": ASSEMBLY_PROMPT},
            {"role": "user", "content": user_content}
        ],
        temperature=0.4
    )
    
    skill_content = response.choices[0].message.content
    
    # 清理可能的 markdown 代码块包裹
    skill_content = re.sub(r'^```(?:markdown|yaml)?\n', '', skill_content.strip())
    skill_content = re.sub(r'\n```$', '', skill_content.strip())
    
    log(f"Skill 草稿生成完成（{len(skill_content)} 字符）")
    return skill_content


# ─── Phase 4: QA 验证闭环 ─────────────────────────────────────────────────────

QA_PROMPT = """你是「Skill 质量审核员」，你的工作是挑毛病，而不是夸奖。
你将收到一个关于特定人物的 SKILL.md，以及原始语料摘要。

执行三项测试：

**测试 1 — Sanity Check（已知问题测试）**
从语料中找出 3 个该人物已经公开回答过的问题，用 Skill 模拟回答，
检查方向是否一致（不要求措辞完全相同，但核心立场必须吻合）。

**测试 2 — Edge Case（边缘测试）**
提出 1 个该人物从未公开讨论过的问题，用 Skill 回答，
检查是否表现出「适度不确定」而非「斩钉截铁」。

**测试 3 — Voice Check（风格测试）**
生成一段 100 字的示例文本，对比 Skill 中的表达 DNA，
检查句式指纹偏差是否 < 15%（主观判断：高度还原/基本还原/偏差较大）。

输出格式（严格 JSON）：
{
  "sanity_check": {
    "tests": [
      {"question": "...", "expected_direction": "...", "skill_answer": "...", "aligned": true/false}
    ],
    "passed": true/false
  },
  "edge_case": {
    "question": "...",
    "skill_answer": "...",
    "shows_uncertainty": true/false,
    "passed": true/false
  },
  "voice_check": {
    "sample_text": "...",
    "voice_fidelity": "高度还原/基本还原/偏差较大",
    "passed": true/false
  },
  "overall_verdict": "PASS/FAIL",
  "fail_reasons": ["如果 FAIL，列出具体原因和修改建议"],
  "quality_score": 0-100
}"""


def run_qa(skill_content: str, corpus_summary: str, target_name: str) -> dict:
    """执行 QA 验证，返回验证结果"""
    log("Phase 4: 启动 QA 验证...")
    
    user_content = f"""目标人物：{target_name}

原始语料摘要（前 3000 字）：
{corpus_summary[:3000]}

待验证的 SKILL.md：
{skill_content[:8000]}

请执行三项测试并输出 JSON 结果。"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": QA_PROMPT},
            {"role": "user", "content": user_content}
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    
    result = json.loads(response.choices[0].message.content)
    verdict = result.get("overall_verdict", "FAIL")
    score = result.get("quality_score", 0)
    log(f"QA 结果: {verdict}（质量分: {score}/100）")
    
    if verdict == "FAIL":
        reasons = result.get("fail_reasons", [])
        for r in reasons:
            log(f"  ✗ {r}")
    
    return result


# ─── 主流程：组装 + QA 闭环 ──────────────────────────────────────────────────

def assemble_with_qa_loop(
    graph: dict,
    target_name: str,
    corpus_summary: str,
    output_dir: Path
) -> tuple[str, dict]:
    """
    带 QA 闭环的 Skill 组装。
    最多重试 MAX_QA_RETRIES 次，返回 (skill_content, qa_result)。
    """
    feedback = ""
    skill_content = ""
    qa_result = {}
    
    for attempt in range(1, MAX_QA_RETRIES + 1):
        log(f"\n=== 第 {attempt}/{MAX_QA_RETRIES} 次组装 ===")
        
        # Phase 3: 组装
        skill_content = assemble_skill(graph, target_name, feedback)
        
        # Phase 4: QA 验证
        qa_result = run_qa(skill_content, corpus_summary, target_name)
        
        if qa_result.get("overall_verdict") == "PASS":
            log(f"QA 通过！质量分: {qa_result.get('quality_score')}/100")
            break
        
        if attempt < MAX_QA_RETRIES:
            fail_reasons = qa_result.get("fail_reasons", [])
            feedback = "上次失败原因：\n" + "\n".join(f"- {r}" for r in fail_reasons)
            log(f"QA 失败，准备第 {attempt + 1} 次重试...")
        else:
            log(f"警告：已达最大重试次数（{MAX_QA_RETRIES}），使用最后一次结果")
    
    # 保存最终结果
    output_dir.mkdir(parents=True, exist_ok=True)
    
    skill_path = output_dir / "SKILL.md"
    with open(skill_path, "w", encoding="utf-8") as f:
        f.write(skill_content)
    log(f"SKILL.md 已保存: {skill_path}")
    
    qa_path = output_dir / "qa_report.json"
    with open(qa_path, "w", encoding="utf-8") as f:
        json.dump(qa_result, f, ensure_ascii=False, indent=2)
    log(f"QA 报告已保存: {qa_path}")
    
    return skill_content, qa_result


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Skill 组装与 QA 验证")
    parser.add_argument("graph_path", help="知识图谱 JSON 文件路径")
    parser.add_argument("corpus_dir", help="原始语料目录")
    parser.add_argument("--target", required=True, help="目标人物名称")
    parser.add_argument("--output-dir", default="./output", help="输出目录")
    args = parser.parse_args()

    # 读取知识图谱
    with open(args.graph_path, encoding="utf-8") as f:
        graph = json.load(f)
    
    # 读取语料摘要
    corpus_dir = Path(args.corpus_dir)
    all_text = []
    for f in corpus_dir.glob("*.md"):
        all_text.append(f.read_text(encoding="utf-8"))
    corpus_summary = "\n\n---\n\n".join(all_text)
    
    skill_content, qa_result = assemble_with_qa_loop(
        graph, args.target, corpus_summary, Path(args.output_dir)
    )
    
    print(f"\n最终质量分: {qa_result.get('quality_score', 'N/A')}/100")
    print(f"SKILL.md: {args.output_dir}/SKILL.md")
