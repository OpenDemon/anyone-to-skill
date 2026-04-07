# -*- coding: utf-8 -*-
"""
Anyone to Skill — 终端对话入口
在终端里直接与任何人对话

支持的 API：
  - OpenAI      OPENAI_API_KEY=sk-...
  - Gemini      GEMINI_API_KEY=AIza...
  - GLM（智谱）  GLM_API_KEY=...

用法：
    anyone2skill                          # 交互式选择人物
    anyone2skill --person 马斯克
    anyone2skill --person Karpathy
    anyone2skill --api glm --person 孔子
    anyone2skill --skill path/to/SKILL.md

依赖：pip install openai
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

# ── 配置目录 ───────────────────────────────────────────────────────────────────
CONFIG_DIR  = Path.home() / ".anyone2skill"
CONFIG_FILE = CONFIG_DIR / "config.json"
CACHE_DIR   = CONFIG_DIR / "skills"

# ── API 配置 ──────────────────────────────────────────────────────────────────
API_CONFIGS = {
    "openai": {
        "name": "OpenAI",
        "env":  "OPENAI_API_KEY",
        "base_url": None,
        "models": ["gpt-4.1-mini", "gpt-4o-mini", "gpt-4o"],
        "default_model": "gpt-4.1-mini",
        "hint": "https://platform.openai.com/api-keys"
    },
    "gemini": {
        "name": "Gemini",
        "env":  "GEMINI_API_KEY",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "models": ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
        "default_model": "gemini-2.0-flash",
        "hint": "https://aistudio.google.com/app/apikey"
    },
    "glm": {
        "name": "GLM（智谱）",
        "env":  "GLM_API_KEY",
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "models": ["glm-4-flash", "glm-4-air", "glm-4"],
        "default_model": "glm-4-flash",
        "hint": "https://open.bigmodel.cn/usercenter/apikeys"
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


# ── 持久化配置 ─────────────────────────────────────────────────────────────────

def load_config() -> dict:
    """从 ~/.anyone2skill/config.json 加载保存的 API key（兼容 BOM）"""
    if CONFIG_FILE.exists():
        try:
            # utf-8-sig 自动去掉 BOM（Windows PowerShell 写入的文件常带 BOM）
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8-sig"))
        except Exception:
            pass
    return {}


def save_config(config: dict):
    """保存 API key 到 ~/.anyone2skill/config.json（无 BOM）"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    # 用 utf-8（无 BOM）写入，避免下次读取时 key 带 BOM 前缀
    CONFIG_FILE.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def load_saved_keys():
    """把保存的 key 加载到环境变量（优先级低于已有环境变量）"""
    config = load_config()
    for api_name, cfg in API_CONFIGS.items():
        env_key = cfg["env"]
        if not os.environ.get(env_key) and config.get(env_key):
            os.environ[env_key] = config[env_key]


# ── 输入工具 ───────────────────────────────────────────────────────────────────

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


# ── API 选择 ───────────────────────────────────────────────────────────────────

def select_api() -> tuple[str, str]:
    """交互式选择 API，显示所有已检测到的 key，选完后持久化保存"""
    items = list(API_CONFIGS.items())
    available_count = sum(1 for _, cfg in items if os.environ.get(cfg["env"], ""))

    if available_count > 1:
        print(f"\n  {Y}{B}检测到多个 API Key，请选择要使用的：{R}\n")
    else:
        print(f"\n  {B}请选择要使用的 API：{R}\n")

    for i, (name, cfg) in enumerate(items, 1):
        key = os.environ.get(cfg["env"], "")
        if key:
            masked = key[:4] + "****" + key[-4:] if len(key) > 8 else "****"
            status = f"{G}✓ 已设置  {DIM}{masked}{R}"
        else:
            status = f"{DIM}未设置{R}"
        print(f"  {C}{B}[{i}]{R}  {B}{cfg['name']:<14}{R}  {status}")
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
                existing_key = os.environ.get(cfg["env"], "")

                if existing_key:
                    masked = existing_key[:4] + "****" + existing_key[-4:] if len(existing_key) > 8 else "****"
                    print(f"\n  {G}当前 Key: {masked}{R}")
                    sys.stdout.write(f"  {DIM}直接回车使用当前 Key，或粘贴新 Key 替换 >{R} ")
                    sys.stdout.flush()
                    try:
                        new_key = read_line()
                    except KeyboardInterrupt:
                        sys.exit(0)
                    key = new_key.strip() if new_key.strip() else existing_key
                else:
                    print(f"\n  {Y}未检测到 {cfg['name']} Key{R}")
                    print(f"  {DIM}获取地址：{cfg['hint']}{R}")
                    sys.stdout.write(f"  {C}粘贴 API Key >{R} ")
                    sys.stdout.flush()
                    try:
                        key = read_line().strip()
                    except KeyboardInterrupt:
                        sys.exit(0)
                    if not key:
                        print(f"  {Y}未输入 key，请重新选择{R}")
                        continue

                # 写入环境变量
                os.environ[cfg["env"]] = key

                # 持久化保存到配置文件
                config = load_config()
                config[cfg["env"]] = key
                save_config(config)
                print(f"  {G}✓ Key 已保存，下次启动无需重新输入{R}\n")

                return api_name, key
        except ValueError:
            pass
        print(f"  {Y}请输入 1-{len(items)} 之间的数字{R}")


def build_client(api_name: str, key: str = None) -> tuple[OpenAI, str]:
    """构建 OpenAI 兼容客户端，返回 (client, model)"""
    cfg = API_CONFIGS[api_name]
    if key is None:
        key = os.environ.get(cfg["env"], "")
    kwargs = {"api_key": key}
    if cfg["base_url"]:
        kwargs["base_url"] = cfg["base_url"]
    client = OpenAI(**kwargs)
    return client, cfg["default_model"]


# ── Skill 加载 ─────────────────────────────────────────────────────────────────

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


# ── System Prompt ──────────────────────────────────────────────────────────────

def build_system_prompt(person_name: str, skill_md: str) -> str:
    return f"""你现在是 {person_name}，不是在扮演他，就是他本人。

以下是 {person_name} 的认知操作系统，包含其核心心智模型、决策启发式、表达风格和价值观：

---
{skill_md}
---

【绝对禁止】
- 禁止用编号列表（1. 2. 3.）回答，这是 AI 的模板，不是人的说话方式
- 禁止说「首先」「其次」「最后」「总结来说」「希望对你有帮助」
- 禁止给出面面俱到的「全面建议」，真实的人只会说自己真正相信的那一点
- 禁止用「作为一个创业者」「作为一个思想家」这类自我标榜的开头
- 禁止把问题当作文章题目来回答

【必须做到】
- 用 {person_name} 真实的说话方式：他/她会用什么词？什么句式？什么节奏？
- 只说他/她真正相信的东西，不说他/她不会说的废话
- 允许有情绪，允许有偏见，允许不完整——真实的人就是这样
- 如果问题触碰到他/她的核心信念，要有力量感，不要温吞
- 如果问题超出他/她的认知边界，要直接说「这个我没想清楚」或转向他/她熟悉的框架
- 回答可以很短，一两句话就够，不需要把每个角度都覆盖到
- 说完就停，不要画蛇添足

【正确的风格示例】
问：如果你现在 18 岁一无所有，你会怎么开始？
✓ 短促有力，直接说他真正会做的第一件事
✓ 可以反问，可以挑战问题本身
✓ 不超过 150 字，除非问题本身需要深度展开
✗ 不是列出 10 条建议"""


# ── 对话循环 ───────────────────────────────────────────────────────────────────

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
            stream = client.chat.completions.create(
                model=model,
                messages=history,
                temperature=0.85,
                max_tokens=1000,
                stream=True,
            )
            reply_chunks = []
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    text = delta.content
                    reply_chunks.append(text)
                    for ch in text:
                        if ch == "\n":
                            sys.stdout.write(f"{G}\n            {R}")
                        else:
                            sys.stdout.write(f"{G}{ch}{R}")
                    sys.stdout.flush()
            print("\n")
            reply = "".join(reply_chunks).strip()
            history.append({"role": "assistant", "content": reply})

        except Exception as e:
            err = str(e)
            # 流式不支持时回退到普通模式
            if any(kw in err.lower() for kw in ["stream", "streaming", "not supported"]) or "400" in err:
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
                    continue
                except Exception as e2:
                    err = str(e2)

            # 连接错误：给出更明确的提示
            if "connection" in err.lower() or "connect" in err.lower():
                print(f"\n  {Y}连接失败。可能的原因：{R}")
                print(f"  {DIM}1. 网络问题或需要代理（VPN）{R}")
                print(f"  {DIM}2. API Key 无效或已过期{R}")
                cfg = API_CONFIGS[api_name]
                print(f"  {DIM}3. 重新获取 Key：{cfg['hint']}{R}\n")
            else:
                print(f"\n  {Y}出错了: {err}{R}")
                if "model" in err.lower() or "404" in err:
                    cfg = API_CONFIGS[api_name]
                    print(f"  {DIM}可用模型: {', '.join(cfg['models'])}{R}\n")
            history.pop()


# ── 主入口 ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="与任何人在终端里直接对话，或蒸馏新人物",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  anyone2skill                              # 交互式选择人物和 API
  anyone2skill --person 马斯克              # 直接对话马斯克
  anyone2skill --person Karpathy            # 直接对话 Karpathy
  anyone2skill --api gemini                 # 强制使用 Gemini API
  anyone2skill --api glm --person 孔子      # 用 GLM 对话孔子
  anyone2skill --skill my/SKILL.md          # 加载自定义 skill
  anyone2skill distill --name 黄仁勋        # 自动蒸馏新人物（搜索15个视频）
  anyone2skill distill --name 黄仁勋 --videos 20  # 搜索20个视频
  anyone2skill distill --name 黄仁勋 --file interview.pdf  # 加入本地文件
        """
    )

    # 检查是否是 distill 子命令
    if len(sys.argv) > 1 and sys.argv[1] == "distill":
        distill_parser = argparse.ArgumentParser(description="自动蒸馏新人物")
        distill_parser.add_argument("--name", "-n", required=True, help="人物名称（如：黄仁勋）")
        distill_parser.add_argument("--videos", type=int, default=15, help="搜索视频数量（默认15）")
        distill_parser.add_argument("--youtube", action="append", metavar="URL", help="额外指定 YouTube URL（可多次使用）")
        distill_parser.add_argument("--file", action="append", metavar="PATH", help="额外指定本地文件（PDF/TXT，可多次使用）")
        distill_parser.add_argument("--api", "-a", choices=["openai", "gemini", "glm"], help="指定 API")
        distill_parser.add_argument("--model", "-m", help="指定模型名称")
        distill_args = distill_parser.parse_args(sys.argv[2:])

        # 加载 key
        load_saved_keys()
        if distill_args.api:
            api_name = distill_args.api
        else:
            available = [(n, os.environ.get(c["env"], "")) for n, c in API_CONFIGS.items() if os.environ.get(c["env"], "")]
            if not available:
                api_name, _ = select_api()
            else:
                config = load_config()
                last_api = None
                for env_key in config:
                    for n, c in API_CONFIGS.items():
                        if c["env"] == env_key and config.get(env_key):
                            last_api = n
                api_name = last_api or available[0][0]

        client, default_model = build_client(api_name)
        model = distill_args.model or default_model

        from anyone2skill.distill import run_distill
        run_distill(distill_args, client, model)
        return

    parser.add_argument("--person", "-p", help="人物名称（如：马斯克、Karpathy）")
    parser.add_argument("--skill",  "-s", help="本地 SKILL.md 文件路径")
    parser.add_argument("--api",    "-a", choices=["openai", "gemini", "glm"],
                        help="指定 API（默认自动检测）")
    parser.add_argument("--model",  "-m", help="指定模型名称（覆盖默认）")
    args = parser.parse_args()

    # 先加载保存的 key（从 ~/.anyone2skill/config.json）
    load_saved_keys()

    # ── 确定使用哪个 API ──
    if args.api:
        api_name = args.api
        key = os.environ.get(API_CONFIGS[api_name]["env"], "")
        if not key:
            cfg = API_CONFIGS[api_name]
            print(f"\n  {Y}未设置 {cfg['name']} Key{R}")
            print(f"  {DIM}获取地址：{cfg['hint']}{R}")
            sys.stdout.write(f"  {C}直接粘贴 API Key >{R} ")
            sys.stdout.flush()
            try:
                key = read_line()
            except KeyboardInterrupt:
                sys.exit(0)
            if not key:
                sys.exit(1)
            os.environ[cfg["env"]] = key
            # 持久化保存
            config = load_config()
            config[cfg["env"]] = key
            save_config(config)
            print(f"  {G}✓ Key 已保存，下次启动无需重新输入{R}\n")
    else:
        # 检测可用 key
        available = [(n, os.environ.get(c["env"], "")) for n, c in API_CONFIGS.items() if os.environ.get(c["env"], "")]
        if len(available) == 0:
            api_name, _ = select_api()
        elif len(available) == 1:
            api_name = available[0][0]
        elif args.person or args.skill:
            # 非交互模式：config.json 中最后写入的 Key 优先级最高（不受系统环境变量干扰）
            config = load_config()
            last_api = None
            for env_key in config:
                for n, c in API_CONFIGS.items():
                    if c["env"] == env_key and config.get(env_key):
                        last_api = n
            if last_api:
                api_name = last_api
                os.environ[API_CONFIGS[api_name]["env"]] = config[API_CONFIGS[api_name]["env"]]
            else:
                api_name = available[0][0]
            api_label = API_CONFIGS[api_name]["name"]
            print(f"  {DIM}使用 API: {api_label}  (可用 --api glm/openai/gemini 切换){R}\n")
        else:
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
