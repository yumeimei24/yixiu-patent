# yixiu-patent

中国发明专利撰写技能集。把论文、技术说明或已有交底书，整理成技术交底书，配专利附图，导出 A4 Word，必要时再生成完整申请书。

仓库里有两个可以独立安装的技能，加一组离线 Python 工具。工具只用标准库，不需要 pandoc、LibreOffice、graphviz 或 inkscape。

- `skills/patent-disclosure/` 主技能，负责流程路由与撰写规范。
- `skills/paper2patent/` 配套技能，负责论文转申请书与黑白附图引擎。

## 目录结构

```
yixiu-patent/
├── skills/
│   ├── patent-disclosure/
│   │   ├── SKILL.md           模式路由、模板策略、检查清单、免责声明
│   │   ├── prompts/           review / convert / search / standards / draft / draw / iterate / export / upgrade
│   │   ├── references/        法规基线、权利要求、附图规范、实施方式规范、质量红线、体裁规范、复盘清单
│   │   ├── tools/             docx、pdf 文本提取；MD 转 A4 Word；附图复核；成稿扫查
│   │   └── assets/            默认交底书模板
│   └── paper2patent/
│       ├── SKILL.md
│       ├── references/        权利要求起草、说明书标准、充分公开审计、附图生成
│       ├── scripts/           附图引擎、申请书 DOCX、自检脚本、PDF 导出
│       ├── assets/            示例申请书内容 JSON
│       └── agents/
├── examples/
│   ├── figures-spec-example.json          脱敏示例，可直接跑通四图规格
│   └── disclosure-skeleton-example.md     结构骨架示例
├── scripts/
│   ├── vendor_upstream.py                 从上游仓库补拉或校验文件
│   ├── sync_yixiu_skills.py               把本仓库技能安装或更新到本地 Agent 技能目录
│   └── verify_published_repo.py           本地目录与已发布仓库逐文件比对，并做泄漏扫描
├── NOTICE.md                  文件级上游来源与署名
├── LICENSE                    MIT
├── PUBLISHING.md              发布与更新步骤
└── .gitignore
```

## 安装

把 `skills/<技能名>/` 整个目录复制到 Agent 的技能目录：

| 宿主 | 技能目录 |
|---|---|
| Claude Code | `~/.claude/skills/` 或 `<project>/.claude/skills/` |
| Cursor | `~/.cursor/skills/` 或 `<project>/.cursor/skills/` |
| Codex CLI | `~/.codex/skills/` |
| DeepSeek Harness | `<project>/.dsh/skills/` |

两个技能是配套关系。`patent-disclosure` 的 draw 模式会调用 `../paper2patent/scripts/generate_patent_drawings.py`，安装时保持同级目录结构。

## 快速开始

```bash
# 生成专利附图：黑白线条 SVG 与 300dpi PNG，并做节点数、字高、内容区占比校验
python skills/paper2patent/scripts/generate_patent_drawings.py \
  examples/figures-spec-example.json -o examples/out --prefix 示例 --update-json

# 图面程序化复核：SVG 标签齐全、PNG 像素统计（构图美学仍需人工目视）
python skills/patent-disclosure/tools/verify_figures.py \
  examples/figures-spec-example.json examples/out 示例

# Markdown 转 A4 Word：标题层级、居中公式行、带框表格、_{下标}、^{上标}、![图注](png)
python skills/patent-disclosure/tools/md_to_docx_min.py <in.md> <out.docx>

# Word 回读校验，交付前必做
python skills/patent-disclosure/tools/extract_docx_text.py <out.docx> <check.txt>

# 成稿机械扫查，交付前必做
python skills/patent-disclosure/tools/consistency_scan.py <成稿.md>
```

依赖 Python 3.9 及以上；附图输出 PNG 需要 Pillow，像素统计可选装 numpy。

`consistency_scan.py` 检查的是文本本身的缺陷：错字与双标点、术语一物多名、英文大小写漂移、公式引导句后没有公式、符号重定义、说明书里混入权利要求用语、量化效果数字无出处、实施例与发明内容大段重复、附图说明与正文引用不匹配。输出分 `[ERROR]` 与 `[WARN]` 两级，前者必修，后者逐条确认。它是纯文本检查，和用 `extract_docx_text.py` 检查"DOCX 有没有丢段落和公式"是两件事。

## 更新本地技能

```bash
# 首次安装或后续更新：下载 tarball、安装 skills/*、把同名旧技能备份到 .dsh/skills-archive/
python scripts/sync_yixiu_skills.py --repo <owner>/yixiu-patent --retire <旧技能名>

# 验收：本地目录与已发布仓库逐文件比对，含内容比对与泄漏扫描
python scripts/verify_published_repo.py <owner>/yixiu-patent <本地目录>
```

安装结果写入 `.dsh/skills/.yixiu-manifest.json`，记录仓库、分支、时间与各技能文件数。

## 工作流

```
材料（论文 / 技术说明 / 现有交底书）
   │
   ├─ review      可专利性初判：客体、三性、公开风险
   ├─ standards   联网核验国知局撰写规范，draft 与 upgrade 的前置
   ├─ convert     材料转专利素材，缺口追问，不臆造
   ├─ search      查新与区别论述，结论含可核验 URL
   ├─ draft       技术交底书，体裁按用户样稿、机构模板、内置模板依次降级
   ├─ draw        专利附图，编号与正文一致
   ├─ iterate     已有稿的合并与纠错，新时间戳不覆盖旧稿，另留修订记录
   ├─ export      A4 的 .md 与 .docx，回读校验
   └─ upgrade     完整申请书：摘要、权利要求书、说明书、说明书附图
```

撰写过程中有三处最容易出问题，规范里都做成了硬规则。

附图。图1 的节点编号等于正文一级步骤号，细化图用二级编号并在正文写明"二级步骤 201 至 209"；图1 只画线性主流程，判断框、分支与回边放进细化图；每张图在具体实施方式里至少有一次"如图N所示"。

具体实施方式。按引导段、对象与数据界定、参数配置表、逐步骤细节、结果呈现、对照实验、替代实施方式、系统与装置实施例、电子设备与存储介质、收尾句这十段写。公式遵守七条规则：铺垫语、变量定义、独立成行、"其中"行、约束不内嵌、数值例子、与权项一一对应。细则见 `skills/patent-disclosure/references/implementation-writing.md`。

质量红线。十类直接判退的缺陷写在 `skills/patent-disclosure/references/spec-quality-redlines.md`，每类附坏例与修法，来源是两份真实说明书的评审记录；配套的 `consistency_scan.py` 把其中能机械判定的部分做成检查项。

## 与上游的关系

本仓库是若干开源技能与规范的整合与增补，不是从零自研。

- `skills/patent-disclosure/**` 基于 [yjmm10/patent-skills](https://github.com/yjmm10/patent-skills)（MIT），新增 draw 模式、附图规范、实施方式规范、质量红线与扫查工具、交付体裁规范、离线工具与实战复盘。
- `skills/paper2patent/**` 基于上游 paper2patent（MIT，Copyright (c) 2026-present 7toCR），新增 DSH 运行适配与使用中的修正。

逐文件来源、许可与哪些文件属本仓库新增，见 [NOTICE.md](NOTICE.md)。撰写方法论另参考了 `xstongxue/best-skills`、`cat-xierluo/legal-skills` 与公开专利撰写攻略，仅作方法来源，未复制其文件。

## License

MIT，见 [LICENSE](LICENSE)。上游文件的版权与许可随附在各技能目录的 `LICENSE` 中，保留原样。

## 免责声明

本仓库提供的模板、规范与工具不构成法律意见、专利代理意见或正式专利申请文件，不具有法律效力。涉及专利申请、权利要求布局、保护范围判断、侵权风险评估及其他法律事项，请由具备资质的专利代理师或律师结合具体情况审核确认。
