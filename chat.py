#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chat.py — Anyone to Skill 终端对话入口

支持的 API：
  - OpenAI      OPENAI_API_KEY=sk-...
  - Gemini      GEMINI_API_KEY=AIza...
  - GLM（智谱）  GLM_API_KEY=...

用法：
    python chat.py                          # 交互式选择人物
    python chat.py --person 马斯克
    python chat.py --person Karpathy
    python chat.py --skill path/to/SKILL.md
    python chat.py --api gemini             # 强制指定 API

依赖：pip install openai
"""

import os
import sys
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

# ── API 配置 ──────────────────────────────────────────────────────────────────
API_CONFIGS = {
    "openai": {
        "name": "OpenAI",
        "env":  "OPENAI_API_KEY",
        "base_url": None,           # 使用默认
        "models": ["gpt-4.1-mini", "gpt-4o-mini", "gpt-4o"],
        "default_model": "gpt-4.1-mini",
        "hint": "export OPENAI_API_KEY=sk-..."
    },
    "gemini": {
        "name": "Gemini",
        "env":  "GEMINI_API_KEY",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "models": ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
        "default_model": "gemini-2.0-flash",
        "hint": "export GEMINI_API_KEY=AIza..."
    },
    "glm": {
        "name": "GLM（智谱）",
        "env":  "GLM_API_KEY",
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "models": ["glm-4-flash", "glm-4-air", "glm-4"],
        "default_model": "glm-4-flash",
        "hint": "export GLM_API_KEY=your-zhipu-key"
    },
}

# ── 内置人物库 ─────────────────────────────────────────────────────────────────
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


def read_line() -> str:
    """跨平台读取一行输入，正确处理 UTF-8"""
    try:
        if hasattr(sys.stdin, "buffer"):
            raw = sys.stdin.buffer.readline()
        else:
            raw = sys.stdin.readline().encode()
        return raw.decode("utf-8", errors="replace").rstrip("\n").rstrip("\r").strip()
    except (KeyboardInterrupt, EOFError):
        raise KeyboardInterrupt


def detect_api() -> tuple[str, str]:
    """自动检测可用的 API key，返回 (api_name, api_key)"""
    for name, cfg in API_CONFIGS.items():
        key = os.environ.get(cfg["env"], "")
        if key:
            return name, key
    return None, None


def select_api() -> tuple[str, str]:
    """交互式选择 API"""
    print(f"\n  {Y}{B}未检测到 API Key，请选择要使用的 API：{R}\n")
    items = list(API_CONFIGS.items())
    for i, (name, cfg) in enumerate(items, 1):
        key = os.environ.get(cfg["env"], "")
        status = f"{G}✓ 已设置{R}" if key else f"{DIM}未设置{R}"
        print(f"  {C}{B}[{i}]{R}  {B}{cfg['name']:<12}{R}  {status}")
    print()

    while True:
        sys.stdout.write(f"  {C}{B}输入编号 >{R} ")
        sys.stdout.flush()
        try:
            choice = read_line()
        except KeyboardInterrupt:
            sys.exit(0)

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                api_name, cfg = items[idx]
                key = os.environ.get(cfg["env"], "")
                if not key:
                    print(f"\n  {Y}请先设置环境变量：{R}")
                    print(f"  {DIM}{cfg['hint']}{R}")
                    print(f"  {DIM}Windows: $env:{cfg['env']}=\"your-key\"{R}\n")
                    sys.stdout.write(f"  {C}直接粘贴 API Key（回车确认）>{R} ")
                    sys.stdout.flush()
                    try:
                        key = read_line()
                    except KeyboardInterrupt:
                        sys.exit(0)
                    if not key:
                        print(f"  {Y}未输入 key，退出。{R}")
                        sys.exit(1)
                    os.environ[cfg["env"]] = key
                return api_name, key
        except ValueError:
            pass
        print(f"  {Y}请输入 1-{len(items)} 之间的数字{R}")


def build_client(api_name: str) -> tuple[OpenAI, str]:
    """构建 OpenAI 兼容客户端，返回 (client, model)"""
    cfg = API_CONFIGS[api_name]
    key = os.environ.get(cfg["env"], "")
    kwargs = {"api_key": key}
    if cfg["base_url"]:
        kwargs["base_url"] = cfg["base_url"]
    client = OpenAI(**kwargs)
    return client, cfg["default_model"]


def fetch_skill_md(repo: str, person_name: str) -> str | None:
    """从 GitHub 拉取 SKILL.md，优先用本地缓存"""
    cache_path = CACHE_DIR / repo.replace("/", "_") / "SKILL.md"
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")

    import urllib.request
    url = f"https://raw.githubusercontent.com/{repo}/master/SKILL.md"
    try:
        print(f"  {DIM}正在获取 {person_name} 的 Skill...{R}", end="", flush=True)
        with urllib.request.urlopen(url, timeout=15) as resp:
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
    print(f"""
{M}{B}  ╔══════════════════════════════════════════════════════╗
  ║         A N Y O N E   T O   S K I L L               ║
  ║       与任何人直接对话 · 在终端里                     ║
  ╚══════════════════════════════════════════════════════╝{R}

  {B}选择你想对话的人物：{R}
""")
    for i, fig in enumerate(BUILTIN_FIGURES, 1):
        print(f"  {C}{B}[{i:2d}]{R}  {B}{fig['name']:<12}{R}  {DIM}{fig['domain']}{R}")
    print(f"\n  {C}{B}[ 0]{R}  {DIM}加载本地 SKILL.md 文件{R}")
    print(f"  {C}{B}[ q]{R}  {DIM}退出{R}\n")

    while True:
        sys.stdout.write(f"  {C}{B}输入编号 >{R} ")
        sys.stdout.flush()
        try:
            choice = read_line()
        except KeyboardInterrupt:
            print(f"\n  {DIM}再见。{R}")
            sys.exit(0)

        if choice.lower() == "q":
            print(f"\n  {DIM}再见。{R}")
            sys.exit(0)

        if choice == "0":
            sys.stdout.write(f"  {C}SKILL.md 路径 >{R} ")
            sys.stdout.flush()
            try:
                path = read_line().strip('"')
            except KeyboardInterrupt:
                continue
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
                    print(f"  {Y}加载失败，请检查网络或选择本地文件（输入 0）{R}")
            else:
                print(f"  {Y}请输入 0-{len(BUILTIN_FIGURES)} 之间的数字{R}")
        except ValueError:
            print(f"  {Y}无效输入{R}")


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


def chat_loop(person_name: str, skill_md: str, client: OpenAI, model: str, api_name: str):
    """主对话循环"""
    history = [{"role": "system", "content": build_system_prompt(person_name, skill_md)}]
    api_label = API_CONFIGS[api_name]["name"]

    print(f"""
{G}{B}  ╔══════════════════════════════════════════════════════╗
  ║  与 {person_name:<20} 对话                          ║
  ╚══════════════════════════════════════════════════════╝{R}
  {DIM}API: {api_label} · 模型: {model}{R}
  {DIM}输入问题后按 Enter · /reset 清空历史 · /quit 退出{R}
""")

    while True:
        sys.stdout.write(f"{C}{B}你 >{R} ")
        sys.stdout.flush()
        try:
            user_input = read_line()
        except KeyboardInterrupt:
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

        print(f"\n{G}{B}{person_name} ❯{R} ", end="", flush=True)
        try:
            response = client.chat.completions.create(
                model=model,
                messages=history,
                temperature=0.85,
                max_tokens=1000,
            )
            reply = response.choices[0].message.content.strip()
            lines = reply.split("\n")
            formatted = ("\n" + " " * 12).join(lines)
            print(f"{G}{formatted}{R}\n")
            history.append({"role": "assistant", "content": reply})

        except Exception as e:
            err = str(e)
            print(f"\n  {Y}出错了: {err}{R}")
            # 如果是模型不存在，提示换模型
            if "model" in err.lower() or "404" in err:
                cfg = API_CONFIGS[api_name]
                print(f"  {DIM}可用模型: {', '.join(cfg['models'])}{R}")
                print(f"  {DIM}用 --model 参数指定，例如: python chat.py --model {cfg['models'][-1]}{R}\n")
            history.pop()


def main():
    parser = argparse.ArgumentParser(
        description="与任何人在终端里直接对话",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python chat.py                          # 交互式选择人物和 API
  python chat.py --person 马斯克          # 直接对话马斯克
  python chat.py --person Karpathy        # 直接对话 Karpathy
  python chat.py --api gemini             # 强制使用 Gemini API
  python chat.py --api glm --person 孔子  # 用 GLM 对话孔子
  python chat.py --skill my/SKILL.md      # 加载自定义 skill
        """
    )
    parser.add_argument("--person", "-p", help="人物名称（如：马斯克、Karpathy）")
    parser.add_argument("--skill",  "-s", help="本地 SKILL.md 文件路径")
    parser.add_argument("--api",    "-a", choices=["openai", "gemini", "glm"],
                        help="指定 API（默认自动检测）")
    parser.add_argument("--model",  "-m", help="指定模型名称（覆盖默认）")
    args = parser.parse_args()

    # ── 确定使用哪个 API ──
    if args.api:
        api_name = args.api
        key = os.environ.get(API_CONFIGS[api_name]["env"], "")
        if not key:
            cfg = API_CONFIGS[api_name]
            print(f"\n  {Y}未设置 {cfg['env']}，请先配置：{R}")
            print(f"  {DIM}{cfg['hint']}{R}")
            print(f"  {DIM}Windows: $env:{cfg['env']}=\"your-key\"{R}\n")
            sys.stdout.write(f"  {C}直接粘贴 API Key >{R} ")
            sys.stdout.flush()
            try:
                key = read_line()
            except KeyboardInterrupt:
                sys.exit(0)
            if not key:
                sys.exit(1)
            os.environ[cfg["env"]] = key
    else:
        api_name, _ = detect_api()
        if not api_name:
            api_name, _ = select_api()

    client, default_model = build_client(api_name)
    model = args.model or default_model

    # ── 确定对话人物 ──
    if args.skill:
        p = Path(args.skill)
        if not p.exists():
            print(f"  {Y}文件不存在: {args.skill}{R}")
            sys.exit(1)
        person_name = p.parent.name or "未知人物"
        skill_md = p.read_text(encoding="utf-8")
    elif args.person:
        found = next((f for f in BUILTIN_FIGURES if args.person in f["name"]), None)
        if found:
            skill_md = fetch_skill_md(found["repo"], found["name"])
            person_name = found["name"]
            if not skill_md:
                sys.exit(1)
        else:
            print(f"  {Y}未找到 '{args.person}'，可用人物：{R}")
            for f in BUILTIN_FIGURES:
                print(f"  {DIM}  {f['name']}{R}")
            sys.exit(1)
    else:
        person_name, skill_md = select_figure()

    chat_loop(person_name, skill_md, client, model, api_name)


if __name__ == "__main__":
    main()
