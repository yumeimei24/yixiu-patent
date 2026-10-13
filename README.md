# yixiu-patent · 中国发明专利撰写全流程技能集

把「论文 / 技术材料 → 技术交底书 → 专利附图 → A4 Word →（可选）完整申请书」这条链路，
做成可被 AI Agent（Claude Code / Cursor / Codex / DeepSeek Harness 等）直接调用的技能包。

> **A skill pack for drafting Chinese invention-patent disclosures and drawings with an AI agent.**
> It routes the whole pipeline — prior-art check → material conversion → disclosure drafting →
> black-and-white patent figures → A4 Word export → optional full application draft — and ships
> offline Python tools (no pandoc / LibreOffice / graphviz needed).

---

## 目录结构

```
yixiu-patent/
├── skills/
│   ├── patent-disclosure/     # 主技能：全流程路由 + 撰写规范 + 离线工具
│   │   ├── SKILL.md           #   模式路由、模板策略、主流程检查清单、固定免责声明
│   │   ├── prompts/           #   review / convert / search / standards / draft / draw / iterate / export / upgrade
│   │   ├── references/        #   法规基线、权利要求、附图规范、实施方式规范、体裁规范、复盘清单
│   │   ├── tools/             #   docx/pdf 文本提取、MD→A4 Word、附图程序化复核
│   │   └── assets/            #   默认交底书模板
│   └── paper2patent/          # 配套技能：论文转专利申请书 + 黑白附图引擎
│       ├── SKILL.md
│       ├── references/        #   权利要求起草、说明书标准、充分公开审计、附图生成
│       ├── scripts/           #   附图引擎、申请书 DOCX、自检脚本、PDF 导出
│       ├── assets/            #   示例申请书内容 JSON
│       └── agents/
├── examples/
│   ├── figures-spec-example.json   # 脱敏示例：可直接跑通的四图规格
│   └── disclosure-skeleton-example.md  # 结构骨架示例：八节模板与写法要点
├── scripts/
│   ├── vendor_upstream.py     # 维护用：按文件清单从上游仓库补拉/校验（urllib + contents API + SHA-1）
│   ├── sync_yixiu_skills.py   # 把本仓库 skills/ 安装或更新到本地 Agent 技能目录（单请求 tarball + 自动备份）
│   └── verify_published_repo.py  # 验收：本地目录与已发布仓库逐文件比对 + 泄漏扫描
├── NOTICE.md                  # 文件级上游来源与署名
├── LICENSE                    # MIT
├── PUBLISHING.md              # 发布/更新到 GitHub 的步骤
└── .gitignore
```

## 安装

把 `skills/<技能名>/` 整个目录复制到你的 Agent 技能目录：

| 宿主 | 技能目录 |
|---|---|
| Claude Code | `~/.claude/skills/` 或 `<project>/.claude/skills/` |
| Cursor | `~/.cursor/skills/` 或 `<project>/.cursor/skills/` |
| Codex CLI | `~/.codex/skills/` |
| DeepSeek Harness (DSH) | `<project>/.dsh/skills/` |

两个技能是配套关系：`patent-disclosure` 的 draw 模式会调用
`../paper2patent/scripts/generate_patent_drawings.py`，因此请保持二者的同级目录结构。

## 快速开始

```bash
# 1) 生成专利附图：黑白线条 SVG + 300dpi PNG，并内置校验（节点数/字高/内容区占比）
python skills/paper2patent/scripts/generate_patent_drawings.py \
  examples/figures-spec-example.json -o examples/out --prefix 示例 --update-json

# 2) 图面程序化复核（SVG 标签齐全 + PNG 像素统计；构图美学仍需人工目视）
python skills/patent-disclosure/tools/verify_figures.py \
  examples/figures-spec-example.json examples/out 示例

# 3) Markdown → A4 Word（标题层级、居中公式行、带框表格、_{下标}、![图注](png) 嵌图）
python skills/patent-disclosure/tools/md_to_docx_min.py <in.md> <out.docx>

# 4) Word 回读校验（交付前必做）
python skills/patent-disclosure/tools/extract_docx_text.py <out.docx> <check.txt>
```

依赖：Python 3.9+；附图输出 PNG 需 `Pillow`（可选 `numpy` 用于像素统计）。
**不需要** pandoc、LibreOffice、graphviz、inkscape。

## 更新（本仓库 → 本地技能目录）

```bash
# 首次安装或后续更新：下载 tarball、安装 skills/*、把同名旧技能备份到 .dsh/skills-archive/
python scripts/sync_yixiu_skills.py --repo <owner>/yixiu-patent --retire <旧技能名>

# 验收：本地目录与已发布仓库逐文件比对（内容 + 泄漏扫描）
python scripts/verify_published_repo.py <owner>/yixiu-patent <本地目录>
```

安装结果写入 `.dsh/skills/.yixiu-manifest.json`（仓库、分支、时间、各技能文件数），便于回溯版本。

## 工作流

```
材料（论文/技术说明/现有交底书）
   │
   ├─ review      可专利性初判（客体、三性、公开风险）
   ├─ standards   联网核验国知局撰写规范（draft/upgrade 前置）
   ├─ convert     材料 → 专利素材（缺口追问，不臆造）
   ├─ search      查新与区别论述（含可核验 URL）
   ├─ draft       技术交底书（体裁：用户样稿 ＞ 机构模板 ＞ 内置）
   ├─ draw        专利附图（编号与正文一致；图1 线性主流程）
   ├─ iterate     已有稿的合并 / 纠正（新时间戳不覆盖旧稿 + 修订记录留痕）
   ├─ export      A4 .md + .docx（回读校验）
   └─ upgrade     完整申请书：摘要 / 权利要求书 / 说明书 / 说明书附图
```

## 三条附图硬规则（踩过坑才写下来的）

1. **编号与正文一致**：图1 节点编号 = 正文一级步骤号（S1—SN）；细化图用图号系列二级编号（图2→201…、图3→301…、图4→401…），判断框不带编号，并在正文写明"二级步骤201至209"。
2. **图1 采线性主流程**：整体流程只画主线，不画判断框、分支与回边；判断框、回边与闭环放细化图。
3. **每图至少一次正文引用**：写完具体实施方式后对照【相关附图】逐图检查"如图N所示"是否各出现至少一次。

## 具体实施方式骨架（10 段）

引导段（预告细化图与二级步骤）→ 对象与数据界定 → **参数配置表** → 逐步骤实施细节 →
结果呈现 → 对照实验 → 替代实施方式（编号列举）→ 系统/装置实施例 →
电子设备/存储介质/程序产品 → 收尾句。
配套的**公式七规则**（铺垫语、变量定义、独立成行、其中行、约束不内嵌、数值例子、与权项一一对应）见
`skills/patent-disclosure/references/implementation-writing.md`。

## 与上游的关系

本仓库是若干开源技能与规范的**整合与增补版**，不是从零自研：

- `skills/patent-disclosure/**` 基于 [yjmm10/patent-skills](https://github.com/yjmm10/patent-skills)（MIT），
  新增 draw 模式、附图规范、实施方式规范、交付体裁规范、离线工具与实战复盘。
- `skills/paper2patent/**` 基于上游 paper2patent（MIT，Copyright (c) 2026-present 7toCR），
  新增 DSH 运行适配与个人使用中的修正。

逐文件来源、许可与哪些文件属本仓库新增，见 **[NOTICE.md](NOTICE.md)**。
撰写方法论另参考了 `xstongxue/best-skills`、`cat-xierluo/legal-skills` 与公开专利撰写攻略（仅作为方法来源引用，未复制其文件）。

## License

MIT（见 [LICENSE](LICENSE)）；上游文件的版权与许可随附在各技能目录的 `LICENSE` 中并保留原样。

## 免责声明

本仓库提供的模板、规范与工具**不构成法律意见、专利代理意见或正式专利申请文件**，不具有法律效力。
涉及专利申请、权利要求布局、保护范围判断、侵权风险评估及其他法律事项，
请由具备资质的专利代理师或律师结合具体情况审核确认。
