#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""consistency_scan.py —— 专利文本一致性 / AI 腔 / 公式完整性机械扫查（纯标准库）

用法：
    python consistency_scan.py 说明书.md
    python consistency_scan.py 说明书.md --strict          # 有 ERROR/WARN 即退出码 1
    python consistency_scan.py 权利要求书.md --allow-claims # 允许"其特征在于"（权利要求书用）

设计目标：把 `references/spec-quality-redlines.md` 的十类缺陷变成可执行检查。
报告中 [ERROR] 必修，[WARN] 逐条人工确认（部分是提示性，需结合语境判断）。

注意：本工具读的是**源稿文本**。若输入是从 .docx 提取的文本且原稿公式用 Word 公式对象
（OMML）书写，提取时公式会整体丢失，此时"公式引导句空悬"可能是提取假阳性——但同样说明
原稿不该依赖 OMML：源稿应以 $$…$$ 写公式。
"""

import argparse
import re
import sys
from collections import defaultdict

try:  # 中文输出兼容
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ---------------------------------------------------------------- 规则数据

# 错字 / 用词黑名单：命中词 -> 建议（见 spec-quality-redlines.md §4）
TYPO_MAP = {
    "长时续": "长时序",
    "短时续": "短时序",
    "涂零": "除零",
    "相像素": "像素",
    "的的": "的",
    "了了": "了",
    "ReLu": "ReLU",
    "Relu": "ReLU",
    "Min-MAX": "Min-Max",
    "本专利": "本发明",
    "一位卷积": "1×1 卷积（若确指 1x1）",
    "需拟": "虚拟",
}

# AI 腔 / 营销腔 / 论文腔黑名单（见 output-layout-style.md §4）
AI_PHRASES = [
    "飞速发展", "日益迫切", "亟待解决", "关键技术难题", "广阔的市场需求",
    "应用前景", "极大地", "真正实现", "赋能", "底座", "闭环生态",
    "核心优势在于", "系统性引入", "并非简单", "值得注意的是", "综上所述",
    "不难发现", "我们认为", "笔者", "领先", "SOTA", "首次提出",
]

# 防御性表达黑名单（见 anti-defensive-writing.md：交底书是技术主张书，不是自我审查报告）
DEFENSIVE_PHRASES = [
    "需要指出的是", "需要说明的是", "应当注意", "有必要说明",
    "这并不意味着", "不能简单认为", "不能简单地认为", "并不只是", "并不是说",
    "在一定程度上", "从多个维度", "多维度综合", "综合分析", "可以看出",
    "不难看出", "众所周知", "毋庸置疑", "遗憾", "存在严重不足",
    "效果有限", "仍有待改进", "仍有不足", "未能超过", "明显落后",
    "本文", "我们", "本团队", "可选地", "在需要",
]

# 效果句中的量化数字（须可溯源，见 redlines §8）
QUANT = re.compile(r"(\d+(?:\.\d+)?\s*%|\d+(?:\.\d+)?\s*(?:ms|毫秒|倍|帧))")
EFFECT_WORD = re.compile(r"(显著|大幅|有效|准确识别|提升|降低|提前|优于|增强)")

# 公式引导句（其后必须紧跟公式本体）
LEAD_IN = re.compile(
    r"(公式如下|公式为|计算公式为|计算公式如下|表示如下|公式如下所示|具体公式为|"
    r"如下所示|如下表示|表示为以下公式|由以下公式)[：:]?\s*$")
FORMULAISH = re.compile(r"(\$\$|＝|=|∑|\\sum|\\frac|∈)")

# 符号定义句（支持 _{下标}、^{上标}、以及不带花括号的 _下标）
DEF_PATTERNS = [
    re.compile(r"([A-Za-z][A-Za-z0-9]*(?:_(?:\{[^}]{1,12}\}|[A-Za-z0-9]{1,12}))?"
                r"(?:\^\{[^}]{1,12}\})?)\s*(?:为|表示)"),
    re.compile(r"其中[，,]\s*([A-Za-z][A-Za-z0-9]*(?:_(?:\{[^}]{1,12}\}|[A-Za-z0-9]{1,12}))?"
                r"(?:\^\{[^}]{1,12}\})?)\s*(?:为|表示)"),
]
SYM_NORM = re.compile(r"[\s_{}^]")

# 名词短语（模块/单元/网络…）用于术语变体聚类
NOUN_PHRASE = re.compile(
    r"[\u4e00-\u9fffA-Za-z0-9\-]{2,12}"
    r"(?:模块|单元|子系统|系统|网络|编码器|解码器|生成器|鉴别器|检测头|引擎|框架|机制)")
# 名词短语内含功能词的视为句子片段而非术语，跳过
NOISE_CHARS = set("的中与和及或在对将其了所这根据使用通过采用包含进行得到以及其中")


def is_clean_noun(t):
    return not any(c in NOISE_CHARS for c in t)

EN_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9\-]{2,}")

# 名词短语前的功能词/引导语，匹配后需剥离，避免把「本发明基于抗背景干扰模块」当成独立术语
TERM_PREFIXES = [
    "本发明利利用", "本发明基于", "本发明", "所述", "上述的", "上述", "该", "本", "其",
    "并将", "并且", "然后", "以及", "和", "与", "在", "对", "将", "利用", "采用",
    "通过", "一种", "其中", "这", "此", "由", "使", "把", "为", "是", "包括", "含有",
    "它还有", "它", "引入", "结合", "另有", "设有", "还包括", "包括有",
]
# 这些通用词的大小写混用不算技术术语漂移
ENGLISH_CASE_OK = {
    "python", "docx", "doc", "license", "readme", "markdown", "word", "excel",
    "github", "gitlab", "git", "api", "json", "yaml", "xml", "html", "url",
    "png", "jpg", "jpeg", "svg", "pdf", "csv", "tsv", "zip", "tar", "cli",
    "windows", "linux", "macos", "ubuntu", "main", "master", "email", "http",
    "https", "utf", "ack", "todo", "fixme", "gpu", "cpu", "ram", "sql",
}
# 合法的叠字（不作为衍字报出）
DOUBLE_OK = {
    "某某", "渐渐", "常常", "仅仅", "稍稍", "刚刚", "恰恰", "往往", "屡屡", "多多",
    "试试", "看看", "想想", "天天", "人人", "处处", "个个", "件件", "种种", "层层",
    "步步", "次次", "家家", "点点", "阵阵", "丝丝", "微微", "慢慢", "牢牢", "紧紧",
    "深深", "一一", "时时", "事事", "年年", "月月", "日日", "刚刚", "统统", "慢慢",
    "两两", "双双", "层层", "面面", "条条", "样样", "步步", "串串", "块块", "组组",
}
# 叠用高风险的函数字/单语素字（真衍字几乎都发生在这些字上）
DOUBLED_RISK = set("的了用为是在有和与及将所就也都各相可能要会于而并或被给让使")

FIG_LISTED = re.compile(r"^图\s*(\d+)\s*(?:为|是)")
FIG_REFERENCED = re.compile(r"图\s*(\d+)\s*(?:所示|中|所示，|所示的)")


def read_text(path):
    for enc in ("utf-8", "utf-8-sig", "gbk"):
        try:
            with open(path, "r", encoding=enc) as fh:
                return fh.read()
        except (UnicodeDecodeError, LookupError):
            continue
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def edit_distance_leq(a, b, limit=2):
    if abs(len(a) - len(b)) > limit:
        return False
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        if min(cur) > limit:
            return False
        prev = cur
    return prev[-1] <= limit


class Scan:
    def __init__(self, path, allow_claims=False):
        self.path = path
        self.lines = read_text(path).splitlines()
        self.allow_claims = allow_claims
        self.findings = []  # (level, check, line_no, message)

    def add(self, level, check, lineno, msg):
        self.findings.append((level, check, lineno, msg))

    # ------------------------------------------------------------ 各项检查
    def check_punctuation(self):
        for i, ln in enumerate(self.lines, 1):
            for m in re.finditer(r"([，。；：、！？])\1+", ln):
                self.add("ERROR", "双标点", i, f"重复标点「{m.group(0)}」")
            if ln.strip() in ("。", "；", "，", "、", "."):
                self.add("ERROR", "孤立标点行", i, "整行只有标点，疑为公式占位残留")

    def check_typos(self):
        for i, ln in enumerate(self.lines, 1):
            for bad, good in TYPO_MAP.items():
                if bad in ln:
                    self.add("ERROR", "错字/用词", i, f"「{bad}」→ 应为「{good}」")

    def check_formula_leads(self):
        for i, ln in enumerate(self.lines, 1):
            if not LEAD_IN.search(ln.strip()):
                continue
            nxt = ""
            for j in range(i, len(self.lines)):
                if self.lines[j].strip():
                    nxt = self.lines[j].strip()
                    break
            if not FORMULAISH.search(nxt):
                self.add("ERROR", "公式引导句空悬", i,
                         f"引导句后未跟公式本体，紧接内容为：{nxt[:40]}")

    def check_claim_language(self):
        if self.allow_claims:
            return
        for i, ln in enumerate(self.lines, 1):
            if "其特征在于" in ln:
                self.add("ERROR", "权利要求用语混入", i,
                         "说明书正文不得使用「其特征在于」（仅权利要求书可用）")

    def check_symbols(self):
        defs = defaultdict(list)
        for i, ln in enumerate(self.lines, 1):
            if not re.search(r"(其中|式中|式中，)", ln) and "为" not in ln:
                continue
            for pat in DEF_PATTERNS:
                for m in pat.finditer(ln):
                    raw = m.group(1)
                    sym = SYM_NORM.sub("", raw)
                    if len(sym) < 1 or sym.isdigit():
                        continue
                    if len(sym) == 1 and sym.islower():
                        continue  # 单个小写字母（如 t、x）定义句太常见，不作为重定义证据
                    defs[sym].append((i, ln.strip()[:90]))
        for sym, occ in defs.items():
            texts = {t for _, t in occ}
            if len(occ) >= 2 and len(texts) >= 2:
                locs = ", ".join(str(n) for n, _ in occ[:6])
                self.add("WARN", "符号重定义待核", occ[0][0],
                         f"符号「{sym}」出现 {len(occ)} 处定义句（行 {locs}），确认是否同一含义")

    @staticmethod
    def clean_term(t):
        changed = True
        while changed:
            changed = False
            for p in TERM_PREFIXES:
                if t.startswith(p):
                    t = t[len(p):]
                    changed = True
            if t.startswith("的"):
                t = t[1:]
                changed = True
        return t

    def check_term_variants(self):
        hits = defaultdict(list)
        for i, ln in enumerate(self.lines, 1):
            for m in NOUN_PHRASE.finditer(ln):
                t = self.clean_term(m.group(0))
                if len(t) >= 3 and is_clean_noun(t):
                    hits[t].append(i)
        terms = list(hits)
        reported = set()
        for a in terms:
            for b in terms:
                if a >= b or (a, b) in reported:
                    continue
                if (a in b or b in a) and min(len(a), len(b)) >= 4:
                    short, long = (a, b) if a in b else (b, a)
                    # 短词必须存在独立出现（否则它只是长词的一部分，不构成"多名"）
                    if self.standalone_count(short, long) == 0:
                        continue
                    reported.add((a, b))
                    self.add("WARN", "术语变体", hits[a][0],
                             f"「{a}」({len(hits[a])}次) 与「{b}」({len(hits[b])}次) 疑为同一对象多名")
                elif len(a) >= 5 and len(b) >= 5 and a[-2:] == b[-2:] and edit_distance_leq(a, b, 2):
                    reported.add((a, b))
                    self.add("WARN", "术语变体", hits[a][0],
                             f"「{a}」与「{b}」拼写高度相近，疑为同一对象")

    def standalone_count(self, short, long):
        text = "\n".join(self.lines)
        total = len(re.findall(re.escape(short), text))
        inside = len(re.findall(re.escape(long), text))
        return total - inside

    def check_doubled_chars(self):
        # 只报"函数字/单语素字"的叠用（真衍字高发），避免"槽位位置""环境噪声声压级"这类跨词边界误报
        for i, ln in enumerate(self.lines, 1):
            for m in re.finditer(r"([\u4e00-\u9fff])\1", ln):
                pair = m.group(0)
                if pair in DOUBLE_OK:
                    continue
                if pair[0] not in DOUBLED_RISK:
                    continue
                self.add("WARN", "叠字疑似衍字", i, f"「{pair}」——确认是否衍字（如「利利用」「的的」）")

    def check_english_casing(self):
        variants = defaultdict(set)
        counts = defaultdict(lambda: defaultdict(int))
        for i, ln in enumerate(self.lines, 1):
            for m in EN_TOKEN.finditer(ln):
                tok = m.group(0)
                if m.start() > 0 and ln[m.start() - 1] in "/.@":  # URL / 域名 / 邮箱内不参与
                    continue
                variants[tok.lower()].add(tok)
                counts[tok.lower()][tok] += 1
        for low, forms in variants.items():
            if low in ENGLISH_CASE_OK:
                continue
            if len(forms) > 1 and len(low) >= 4:
                detail = ", ".join(f"{f}×{counts[low][f]}" for f in sorted(forms))
                self.add("WARN", "英文大小写/拼写不一", 0, f"「{low}」存在多种写法：{detail}")

    def check_ai_phrases(self):
        for i, ln in enumerate(self.lines, 1):
            for p in AI_PHRASES:
                if p in ln:
                    self.add("WARN", "AI腔/营销腔", i, f"命中禁词「{p}」")
            for p in DEFENSIVE_PHRASES:
                if p in ln:
                    self.add("WARN", "防御性表达", i,
                             f"命中防御性表达「{p}」——正面改写或删除（见 anti-defensive-writing.md）")
            if "研究表明" in ln:
                self.add("WARN", "无引证表述", i, "「研究表明」须给出引证，否则删除")
            for m in re.finditer(r"(此步骤|此方法|该方法|本方案|该系统)(能够|可以|能)", ln):
                self.add("WARN", "自我表扬段", i, f"命中「{m.group(0)}」，效果应写在效果段并带证据")

    def check_unsourced_numbers(self):
        for i, ln in enumerate(self.lines, 1):
            if QUANT.search(ln) and EFFECT_WORD.search(ln):
                self.add("WARN", "量化效果待溯源", i,
                         f"效果句含量化数字，确认可溯源：{ln.strip()[:80]}")

    def check_duplicate_blocks(self):
        seen = {}
        buf, start = [], 0
        for i, ln in enumerate(self.lines, 1):
            if ln.strip():
                if not buf:
                    start = i
                buf.append(ln.strip())
            else:
                self._flush_block(buf, start, seen)
                buf = []
        self._flush_block(buf, start, seen)

    def _flush_block(self, buf, start, seen):
        if not buf:
            return
        text = "".join(buf)
        if len(text) < 120:
            return
        key = re.sub(r"[\s，。；：、（）()【】\[\]“”\"'`]", "", text)
        if key in seen:
            self.add("WARN", "段落重复", start,
                     f"与第 {seen[key]} 行起的段落重复（{len(text)} 字），实施例不得复制发明内容")
        else:
            seen[key] = start

    def check_lead_phrase_repeat(self):
        counter = defaultdict(list)
        for i, ln in enumerate(self.lines, 1):
            m = re.match(r"^(上述[^，,]{0,8}技术方案中|进一步地|优选的)[，,、]", ln.strip())
            if m:
                counter[m.group(1)].append(i)
        for phrase, locs in counter.items():
            if len(locs) > 8:
                self.add("WARN", "段首短语复读", locs[0],
                         f"「{phrase}」作为段首出现 {len(locs)} 次，建议改为编号分条")

    def check_figures(self):
        listed, refd = set(), set()
        fig_all = re.compile(r"图\s*(\d+)")
        for ln in self.lines:
            s = ln.strip()
            for m in FIG_REFERENCED.finditer(s):
                refd.add(int(m.group(1)))
            # "列出"判定：出现 图N 且该行不是正文引用（无 如图/所示/参见），
            # 兼容「图1 为…」「**图1** 系统框图」与「相关附图包括：图1…」等格式
            if "如图" in s or "所示" in s or "参见" in s:
                continue
            for m in fig_all.finditer(s):
                listed.add(int(m.group(1)))
        for n in sorted(listed - refd):
            self.add("WARN", "附图未引用", 0, f"图{n} 在附图说明中列出，但正文无「如图{n}所示」")
        for n in sorted(refd - listed):
            self.add("WARN", "引用未列出", 0, f"正文引用图{n}，但附图说明未列出")

    def run(self):
        self.check_punctuation()
        self.check_typos()
        self.check_formula_leads()
        self.check_claim_language()
        self.check_symbols()
        self.check_term_variants()
        self.check_doubled_chars()
        self.check_english_casing()
        self.check_ai_phrases()
        self.check_unsourced_numbers()
        self.check_duplicate_blocks()
        self.check_lead_phrase_repeat()
        self.check_figures()
        return self.findings


def main():
    ap = argparse.ArgumentParser(description="专利文本一致性 / AI 腔 / 公式完整性扫查")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--strict", action="store_true", help="有 ERROR/WARN 时退出码 1")
    ap.add_argument("--allow-claims", action="store_true", help="允许权利要求用语（分析权利要求书时）")
    ap.add_argument("--max-per-check", type=int, default=12, help="每类检查最多打印条数")
    args = ap.parse_args()

    total_err = total_warn = 0
    for path in args.files:
        findings = Scan(path, allow_claims=args.allow_claims).run()
        errs = [f for f in findings if f[0] == "ERROR"]
        warns = [f for f in findings if f[0] == "WARN"]
        total_err += len(errs)
        total_warn += len(warns)
        print(f"\n=== {path} ===")
        print(f"ERROR {len(errs)} 项 / WARN {len(warns)} 项")
        by_check = defaultdict(list)
        for lvl, check, ln, msg in findings:
            by_check[(lvl, check)].append((ln, msg))
        for (lvl, check), items in sorted(by_check.items()):
            print(f"\n[{lvl}] {check}（{len(items)}）")
            for ln, msg in items[: args.max_per_check]:
                loc = f"L{ln}" if ln else "-"
                print(f"  {loc:>7}  {msg}")
            if len(items) > args.max_per_check:
                print(f"  ... 其余 {len(items) - args.max_per_check} 条略")

    print(f"\n合计：ERROR {total_err} 项，WARN {total_warn} 项")
    if total_err == 0 and total_warn == 0:
        print("未发现机械可查缺陷。")
    if args.strict and (total_err or total_warn):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
