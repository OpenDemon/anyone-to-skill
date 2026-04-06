#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chat.py — Anyone to Skill 终端对话入口

用法：
    python chat.py              # 交互式选择人物
    python chat.py --person 马斯克
    python chat.py --skill path/to/SKILL.md

依赖：pip install openai
环境变量：OPENAI_API_KEY=sk-...
"""

import os
import sys
import json
import argparse
from pathlib import Path
from openai import OpenAI

# ── 颜色 ──────────────────────────────────────────────────────────────────────
R   = "\033[0m"
B   = "\033[1m"
DIM = "\033[2m"
C   = "\033[96m"    # 青色（用户）
G   = "\033[92m"    # 绿色（人物）
Y   = "\033[93m"    # 黄色（警告）
M   = "\033[95m"    # 紫色（标题）
W   = "\033[97m"    # 白色

# ── 内置人物库（从 GitHub 拉取） ───────────────────────────────────────────────
BUILTIN_FIGURES = [
    {"name": "马斯克",      "repo": "OpenDemon/elon-musk-skill",         "domain": "科技创业 · 第一性原理"},
    {"name": "乔布斯",      "repo": "OpenDemon/steve-jobs-skill",        "domain": "产品设计 · 极简主义"},
    {"name": "比尔盖茨",    "repo": "OpenDemon/bill-gates-skill",        "domain": "软件战略 · 全球健康"},
    {"name": "段永平",      "repo": "OpenDemon/duan-yongping-skill",     "domain": "价值投资 · 本分哲学"},
    {"name": "纳瓦尔",      "repo": "OpenDemon/naval-ravikant-skill",    "domain": "财富自由 · 特定知识"},
    {"name": "张雪峰",      "repo": "OpenDemon/zhang-xue-feng-skill",    "domain": "教育规划 · 务实主义"},
    {"name": "孔子",        "repo": "OpenDemon/kong-zi-skill",           "domain": "仁义礼学 · 修身齐家"},
    {"name": "庄子",        "repo": "OpenDemon/zhuang-zi-skill",         "domain": "逍遥哲学 · 齐物论"},
    {"name": "Karpathy",   "repo": "OpenDemon/andrej-karpathy-skill",   "domain": "深度学习 · AI 教育"},
    {"name": "黄仁勋",      "repo": "OpenDemon/jensen-huang-skill",      "domain": "芯片战略 · 加速主义"},
    {"name": "Dan Koe",    "repo": "OpenDemon/dan-koe-skill",           "domain": "一人企业 · 个人品牌"},
]

CACHE_DIR = Path.home() / ".anyone_to_skill" / "skills"

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    print(f"""
{M}{B}
  ╔══════════════════════════════════════════════════════╗
  ║         A N Y O N E   T O   S K I L L               ║
  ║       与任何人直接对话 · 在终端里                     ║
  ╚══════════════════════════════════════════════════════╝{R}
""")

def fetch_skill_md(repo: str, person_name: str) -> str | None:
    """从 GitHub 拉取 SKILL.md，优先用本地缓存"""
    cache_path = CACHE_DIR / repo.replace("/", "_") / "SKILL.md"
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")

    # 从 GitHub raw 拉取
    import urllib.request
    url = f"https://raw.githubusercontent.com/{repo}/master/SKILL.md"
    try:
        print(f"  {DIM}正在获取 {person_name} 的 Skill...{R}", end="", flush=True)
        with urllib.request.urlopen(url, timeout=10) as resp:
            content = resp.read().decode("utf-8")
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(content, encoding="utf-8")
        print(f"\r  {G}✓ 已加载 {person_name} 的认知操作系统{R}          ")
        return content
    except Exception as e:
        print(f"\r  {Y}✗ 获取失败: {e}{R}")
        return None

def select_figure() -> tuple[str, str]:
    """交互式选择人物，返回 (person_name, skill_md_content)"""
    banner()
    print(f"  {B}选择你想对话的人物：{R}\n")

    for i, fig in enumerate(BUILTIN_FIGURES, 1):
        print(f"  {C}{B}[{i:2d}]{R}  {B}{fig['name']:<12}{R}  {DIM}{fig['domain']}{R}")

    print(f"\n  {C}{B}[ 0]{R}  {DIM}加载本地 SKILL.md 文件{R}")
    print(f"  {C}{B}[ q]{R}  {DIM}退出{R}\n")

    while True:
        try:
            sys.stdout.write(f"  {C}{B}输入编号 >{R} ")
            sys.stdout.flush()
            raw = sys.stdin.buffer.read1(64) if hasattr(sys.stdin, "buffer") else sys.stdin.readline().encode()
            choice = raw.decode("utf-8", errors="replace").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n  {DIM}再见。{R}")
            sys.exit(0)

        if choice.lower() == "q":
            print(f"\n  {DIM}再见。{R}")
            sys.exit(0)

        if choice == "0":
            sys.stdout.write(f"  {C}SKILL.md 路径 >{R} ")
            sys.stdout.flush()
            raw = sys.stdin.buffer.read1(512) if hasattr(sys.stdin, "buffer") else sys.stdin.readline().encode()
            path = raw.decode("utf-8", errors="replace").strip().strip('"')
            p = Path(path)
            if p.exists():
                return path, p.read_text(encoding="utf-8")
            else:
                print(f"  {Y}文件不存在，请重新输入{R}")
                continue

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(BUILTIN_FIGURES):
                fig = BUILTIN_FIGURES[idx]
                skill_md = fetch_skill_md(fig["repo"], fig["name"])
                if skill_md:
                    return fig["name"], skill_md
                else:
                    print(f"  {Y}加载失败，请检查网络或手动指定本地文件{R}")
            else:
                print(f"  {Y}请输入 0-{len(BUILTIN_FIGURES)} 之间的数字{R}")
        except ValueError:
            print(f"  {Y}无效输入，请重新输入{R}")

def build_system_prompt(person_name: str, skill_md: str) -> str:
    return f"""你现在完全扮演 {person_name}。

以下是关于 {person_name} 的认知操作系统（Skill），包含其核心心智模型、决策启发式、表达风格和价值观：

---
{skill_md}
---

【角色扮演规则】
1. 始终以第一人称回答，就像 {person_name} 本人在说话
2. 使用上述 Skill 中描述的表达风格、标志性词汇和句式
3. 运用其具体的心智模型来分析问题，不是简单复读语录
4. 保留其内在张力和矛盾，不要把他/她塑造成完美的人
5. 遇到其认知盲区或不擅长的领域，要诚实表达不确定性
6. 回答长度适中，有质感，不要流水账式列举
7. 不要在回答末尾加「希望这对你有帮助」之类的套话"""

def chat_loop(person_name: str, skill_md: str):
    """主对话循环"""
    client = OpenAI()
    history = [{"role": "system", "content": build_system_prompt(person_name, skill_md)}]

    clear()
    print(f"""
{G}{B}
  ╔══════════════════════════════════════════════════════╗
  ║  与 {person_name:<20} 对话                          ║
  ╚══════════════════════════════════════════════════════╝{R}
  {DIM}输入问题后按 Enter · /reset 清空历史 · /quit 或 Ctrl+C 退出{R}
""")

    while True:
        # 读取用户输入
        try:
            sys.stdout.write(f"{C}{B}你 >{R} ")
            sys.stdout.flush()
            raw = sys.stdin.buffer.read1(4096) if hasattr(sys.stdin, "buffer") else sys.stdin.readline().encode()
            user_input = raw.decode("utf-8", errors="replace").rstrip("\n").rstrip("\r").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n  {DIM}对话结束。再见。{R}\n")
            break

        if not user_input:
            continue

        if user_input.lower() in ("/quit", "/exit", "q"):
            print(f"\n  {DIM}对话结束。再见。{R}\n")
            break

        if user_input.lower() == "/reset":
            history = [{"role": "system", "content": build_system_prompt(person_name, skill_md)}]
            print(f"  {DIM}对话历史已清空。{R}\n")
            continue

        history.append({"role": "user", "content": user_input})

        # 调用 API
        print(f"\n{G}{B}{person_name} ❯{R} ", end="", flush=True)
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=history,
                temperature=0.85,
                max_tokens=1000,
            )
            reply = response.choices[0].message.content.strip()

            # 格式化输出：每行加缩进
            lines = reply.split("\n")
            formatted = ("\n" + " " * 12).join(lines)
            print(f"{G}{formatted}{R}\n")

            history.append({"role": "assistant", "content": reply})

        except Exception as e:
            print(f"\n  {Y}出错了: {e}{R}\n")
            history.pop()

def main():
    parser = argparse.ArgumentParser(description="与任何人在终端里直接对话")
    parser.add_argument("--person", "-p", help="人物名称（如：马斯克）")
    parser.add_argument("--skill", "-s", help="本地 SKILL.md 文件路径")
    args = parser.parse_args()

    # 检查 API Key
    if not os.environ.get("OPENAI_API_KEY"):
        print(f"\n  {Y}请先设置 OPENAI_API_KEY 环境变量：{R}")
        print(f"  {DIM}Windows:  $env:OPENAI_API_KEY = 'sk-...'{R}")
        print(f"  {DIM}Mac/Linux: export OPENAI_API_KEY=sk-...{R}\n")
        sys.exit(1)

    if args.skill:
        p = Path(args.skill)
        if not p.exists():
            print(f"  {Y}文件不存在: {args.skill}{R}")
            sys.exit(1)
        person_name = p.parent.name or "未知人物"
        skill_md = p.read_text(encoding="utf-8")
    elif args.person:
        # 从内置列表查找
        found = next((f for f in BUILTIN_FIGURES if args.person in f["name"]), None)
        if found:
            skill_md = fetch_skill_md(found["repo"], found["name"])
            person_name = found["name"]
            if not skill_md:
                sys.exit(1)
        else:
            print(f"  {Y}未找到 '{args.person}'，请用 --skill 指定本地 SKILL.md{R}")
            sys.exit(1)
    else:
        person_name, skill_md = select_figure()

    chat_loop(person_name, skill_md)

if __name__ == "__main__":
    main()
