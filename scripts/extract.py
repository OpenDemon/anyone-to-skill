"""
extract.py — 多智能体并行提取引擎（Phase 1-2）

6 个 Specialist Agents 并发运行，各自从语料中提取不同维度的认知特征：
  1. writings   — 著作与长文：系统性思考、核心论点、自创术语
  2. dialogues  — 对话与即兴：即兴类比、被追问时的反应
  3. expression — 表达 DNA：句式指纹、高频词、禁忌词
  4. external   — 他者视角：外部批评、争议、盲点
  5. decisions  — 决策记录：真实行为、事后反思
  6. relations  — 关系与记忆：人际互动模式（针对个人/同事）

Phase 2：知识图谱合成 + 三重验证（跨域复现、有生成力、有排他性）
"""

import os
import json
import concurrent.futures
from pathlib import Path
from typing import Optional
from openai import OpenAI

client = OpenAI()
MODEL = "gpt-4.1-mini"


def log(msg: str):
    print(f"[extract] {msg}", flush=True)


# ─── 6 个专项 Agent 的 System Prompt ─────────────────────────────────────────

AGENT_PROMPTS = {
    "writings": """你是「著作分析师」。
任务：从提供的语料中提取目标人物的系统性思维特征。
重点关注：
- 在不同场合重复出现（≥2次）的核心论点
- 自创的术语、概念或框架（非通用词汇）
- 跨越多个领域的底层逻辑
- 对某类问题的一贯立场

输出格式（严格 JSON）：
{
  "core_arguments": [{"claim": "...", "occurrences": ["来源1", "来源2"], "domain": "..."}],
  "coined_terms": [{"term": "...", "definition": "...", "context": "..."}],
  "underlying_logic": ["..."],
  "consistent_positions": [{"topic": "...", "position": "...", "evidence": "..."}]
}""",

    "dialogues": """你是「对话分析师」。
任务：从提供的语料中提取目标人物在即兴对话、访谈、播客中的思维模式。
重点关注：
- 被追问时的典型反应方式（转移、深化、反问）
- 即兴使用的类比和比喻（往往最能暴露真实思维）
- 明确拒绝回答或回避的话题
- 在压力下的决策风格

输出格式（严格 JSON）：
{
  "response_patterns": [{"trigger": "...", "pattern": "...", "example": "..."}],
  "signature_analogies": [{"analogy": "...", "used_for": "...", "source": "..."}],
  "avoided_topics": ["..."],
  "pressure_behavior": "..."
}""",

    "expression": """你是「表达 DNA 分析师」。
任务：量化分析目标人物的语言风格特征，提取可复现的表达指纹。
重点关注：
- 句式特征（平均句长、疑问句比例、断句习惯）
- 高频词汇（前 20 个特征词）
- 绝对禁忌词（从不使用的词汇或表达）
- 幽默风格（自嘲、反讽、荒诞）
- 情绪调节方式（如何处理愤怒/不确定）

输出格式（严格 JSON）：
{
  "sentence_style": {"avg_length": "短/中/长", "question_ratio": "高/中/低", "punctuation_habit": "..."},
  "signature_words": ["词1", "词2", "..."],
  "forbidden_words": ["词1", "词2", "..."],
  "humor_style": "...",
  "emotion_regulation": "...",
  "voice_sample": "用目标人物的风格写一段 50 字的示例文本"
}""",

    "external": """你是「他者视角分析师」。
任务：从提供的语料中提取外部对目标人物的评价、批评和争议。
重点关注：
- 最常见的批评（即使目标人物本人不认同）
- 公认的盲点或认知局限
- 与他人的核心分歧
- 随时间变化的争议

输出格式（严格 JSON）：
{
  "common_criticisms": [{"criticism": "...", "source": "...", "validity": "高/中/低"}],
  "blind_spots": ["..."],
  "key_disagreements": [{"opponent": "...", "topic": "...", "core_tension": "..."}],
  "evolving_controversies": ["..."]
}""",

    "decisions": """你是「决策记录分析师」。
任务：从提供的语料中提取目标人物的真实决策模式。
重点关注：
- 真实行为与公开声称的差异（言行不一的地方往往最真实）
- 高压情境下的决策启发式
- 事后反思和自我修正的模式
- 重大决策的底层权衡逻辑

输出格式（严格 JSON）：
{
  "heuristics": [{"rule": "...", "evidence": "...", "domain": "..."}],
  "say_vs_do_gaps": [{"said": "...", "did": "...", "interpretation": "..."}],
  "self_corrections": [{"original_view": "...", "revised_view": "...", "trigger": "..."}],
  "decision_weights": {"speed_vs_accuracy": "...", "intuition_vs_data": "...", "individual_vs_consensus": "..."}
}""",

    "relations": """你是「关系记忆分析师」。
任务：从提供的语料中提取目标人物的人际互动模式。
重点关注：
- 对不同关系（下属/平级/上级/陌生人）的不同态度
- 建立信任的方式
- 冲突处理风格
- 情感表达的边界

输出格式（严格 JSON）：
{
  "role_switching": [{"relationship": "...", "style": "...", "example": "..."}],
  "trust_building": "...",
  "conflict_style": "...",
  "emotional_boundaries": "...",
  "memorable_interactions": ["..."]
}"""
}


# ─── 单个 Agent 执行 ──────────────────────────────────────────────────────────

def run_agent(agent_name: str, corpus: str, target_name: str) -> dict:
    """运行单个专项 Agent，返回提取结果"""
    log(f"Agent [{agent_name}] 开始提取...")
    
    system_prompt = AGENT_PROMPTS[agent_name]
    user_content = f"""目标人物：{target_name}

以下是关于该人物的语料（可能来自多个来源）：

---
{corpus[:12000]}  
---

请严格按照 JSON 格式输出分析结果，不要添加任何额外说明。"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        raw = response.choices[0].message.content
        result = json.loads(raw)
        log(f"Agent [{agent_name}] 完成 ✓")
        return {"agent": agent_name, "status": "ok", "data": result}
    except Exception as e:
        log(f"Agent [{agent_name}] 失败: {e}")
        return {"agent": agent_name, "status": "error", "error": str(e), "data": {}}


# ─── Phase 1: 并行提取 ────────────────────────────────────────────────────────

def run_parallel_extraction(corpus: str, target_name: str, output_dir: Path) -> dict:
    """
    6 个 Agent 并发运行，收集所有维度的提取结果。
    返回合并后的 raw_features 字典。
    """
    log(f"启动 6 路并行提取，目标：{target_name}")
    
    raw_features = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        futures = {
            executor.submit(run_agent, name, corpus, target_name): name
            for name in AGENT_PROMPTS.keys()
        }
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            raw_features[result["agent"]] = result
    
    # 保存原始提取结果
    raw_path = output_dir / "raw_features.json"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(raw_features, f, ensure_ascii=False, indent=2)
    log(f"原始特征已保存: {raw_path}")
    
    return raw_features


# ─── Phase 2: 知识图谱合成 + 三重验证 ────────────────────────────────────────

SYNTHESIS_PROMPT = """你是「知识图谱合成师」。
你将收到 6 个专项分析师的提取结果，需要将它们合成为一个连贯的认知图谱。

核心任务：从所有提取结果中识别「心智模型候选项」，并对每个候选项执行三重验证：

验证标准：
1. 跨域复现：该模式在≥2个不同领域/话题中出现过（不是随口一说）
2. 有生成力：能推断目标人物对新问题的立场（有预测力）
3. 有排他性：体现独特视角，不是所有聪明人都会这么想

只有通过三重验证的才能成为「心智模型」。

同时，请识别并保留内在张力（不要强行调和矛盾，矛盾本身就是真实性的一部分）。

输出格式（严格 JSON）：
{
  "mental_models": [
    {
      "name": "模型名称（3-6字）",
      "description": "一句话描述",
      "cross_domain_evidence": ["领域1中的体现", "领域2中的体现"],
      "predictive_power": "对什么类型的新问题有预测力",
      "exclusivity": "为什么这是独特的，而非通用常识",
      "passed_triple_check": true
    }
  ],
  "decision_heuristics": [
    {
      "rule": "决策启发式（一句话）",
      "trigger": "在什么情况下触发",
      "evidence": "原始证据",
      "traceable_to": "可追溯到哪个来源/时间点"
    }
  ],
  "internal_tensions": [
    {
      "tension_type": "时间性/领域性/本质性",
      "description": "张力描述",
      "side_a": "一面",
      "side_b": "另一面"
    }
  ],
  "honest_boundaries": [
    "该人物做不到的事或信息盲区（至少3条）"
  ]
}"""


def run_synthesis(raw_features: dict, target_name: str, output_dir: Path) -> dict:
    """Phase 2：合成知识图谱，执行三重验证"""
    log("Phase 2: 启动知识图谱合成...")
    
    # 将所有 Agent 结果整合为输入
    features_text = json.dumps(
        {k: v.get("data", {}) for k, v in raw_features.items()},
        ensure_ascii=False, indent=2
    )
    
    user_content = f"""目标人物：{target_name}

以下是 6 个专项分析师的提取结果：

{features_text[:15000]}

请执行知识图谱合成和三重验证，严格按 JSON 格式输出。"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYNTHESIS_PROMPT},
                {"role": "user", "content": user_content}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        graph = json.loads(response.choices[0].message.content)
        
        # 保存知识图谱
        graph_path = output_dir / "knowledge_graph.json"
        with open(graph_path, "w", encoding="utf-8") as f:
            json.dump(graph, f, ensure_ascii=False, indent=2)
        log(f"知识图谱已保存: {graph_path}")
        
        # 统计通过三重验证的心智模型数量
        models = graph.get("mental_models", [])
        passed = [m for m in models if m.get("passed_triple_check")]
        log(f"心智模型：{len(models)} 个候选，{len(passed)} 个通过三重验证")
        
        return graph
    except Exception as e:
        log(f"知识图谱合成失败: {e}")
        raise


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="多智能体并行提取引擎")
    parser.add_argument("corpus_dir", help="语料目录（ingest.py 的输出目录）")
    parser.add_argument("--target", required=True, help="目标人物名称")
    parser.add_argument("--output-dir", default="./research", help="提取结果输出目录")
    args = parser.parse_args()

    # 读取所有语料文件
    corpus_dir = Path(args.corpus_dir)
    all_text = []
    for f in corpus_dir.glob("*.md"):
        all_text.append(f.read_text(encoding="utf-8"))
    corpus = "\n\n---\n\n".join(all_text)
    
    if not corpus.strip():
        print("ERROR: 语料目录为空，请先运行 ingest.py")
        exit(1)

    out = Path(args.output_dir)
    raw = run_parallel_extraction(corpus, args.target, out)
    graph = run_synthesis(raw, args.target, out)
    print(f"\n提取完成。知识图谱: {out}/knowledge_graph.json")
