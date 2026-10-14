# NOTICE — 文件级来源、许可与署名

本仓库 `yixiu-patent` 汇集并增补了两套开源技能的内容。**上游许可与版权声明保留在各技能目录内**
（`skills/patent-disclosure/LICENSE`、`skills/paper2patent/LICENSE`），本文件说明逐文件来源。

## 1. skills/patent-disclosure

**上游**：[yjmm10/patent-skills](https://github.com/yjmm10/patent-skills) — MIT，Copyright (c) 2026 patent-skills contributors（vendored 2026-08）。

沿用上游的文件（未作实质修改）：

- `prompts/`：`intake.md`、`review.md`、`convert.md`、`search.md`、`standards_lookup.md`、`iterate.md`、`merger.md`、`correction_handler.md`、`iteration_context.md`
- `references/`：`regulatory-standards.md`、`patent-law-basics.md`、`patentability-criteria.md`、`claims-rules.md`、`disclosure-structure.md`、`desensitization.md`、`delivery-naming.md`
- `tools/`：`extract_docx_text.py`、`extract_pdf_text_min.py`、`cnipa_epub_search.py`、`cnipa_epub_crawler.py`、`cnipa_epub_parse.py`、`requirements-cnipa.txt`

**本仓库新增**（上游没有，由本仓库整理撰写）：

| 文件 | 说明 |
|---|---|
| `prompts/draw_figures.md` | draw 模式：交底书 → 图幅清单 → 节点/边抽取 → 引擎生成与校验 → 目视复核 → 交付 |
| `prompts/draft.md` | draft 模式分步指令（前置 Read、落盘双格式、定稿前机械扫查） |
| `prompts/export.md` | export 模式分步指令（A4 导出、回读校验、导出前扫查） |
| `prompts/upgrade.md` | upgrade 模式分步指令（申请书五大部分、六条转换硬规则） |
| `references/patent-figure-spec.md` | 专利附图规范：法定要求、引擎 JSON 契约、三条硬规则、校验清单 |
| `references/implementation-writing.md` | 具体实施方式规范：功能定位、10 段骨架、附图引用规则、公式七规则、退稿自查 |
| `references/output-layout-style.md` | 交付体裁与版面规范（九段【】式与申请书式对照、公式顺号、语言质量红线） |
| `references/disclosure-checklist.md` | 交底书完稿检查清单（含机械扫查节） |
| `references/lessons-learned.md` | 实战复盘清单（补点方法、测量类客体强化、转述他人框架类写法、读料技巧） |
| `references/spec-quality-redlines.md` | 说明书质量红线：十类判退缺陷（公式引导句空悬、符号重定义、术语漂移、错字成窝、权利要求用语混入、实施例复制、AI 腔、无源量化数字、背景评述失焦、附图脱节），每类含真实坏例与修法 |
| `assets/default-disclosure-template.md` | 机构交底书九段【】式默认模板（背景四段叙事、不足"其一…其N"、效果"其一…其N"带数据、`$$…$$` 公式格式） |
| `tools/verify_figures.py` | 附图程序化复核（SVG 标签齐全 + PNG 像素统计） |
| `tools/consistency_scan.py` | 成稿机械扫查（错字、双标点、术语变体、公式空悬、符号重定义、无源数字、段落重复等），draft/upgrade/export 定稿前必跑 |
| `tools/cnipa_batch.py` | CNIPA 公布公告站批量检索（多词逐词检索，输出 UTF-8 摘要，规避 Windows GBK 控制台截断） |
| `tools/md_to_docx_min.py` | MD → A4 DOCX（标题层级、居中公式行、带框表格、下标上标、`![图注](png)` 嵌图） |

**本仓库修改过的上游文件**：

| 文件 | 修改内容 |
|---|---|
| `SKILL.md` | 增加 DSH 运行适配、draw 模式路由、模板策略第 0 步、检查清单条目（含机械扫查与体裁复核）、本地新增参考索引、CNIPA 查新通道与工具状态；上游版权与版本信息保留 |
| `prompts/draft.md` | 增加 spec-quality-redlines 前置 Read 与定稿前 consistency_scan 必做步骤 |
| `prompts/upgrade.md` | 前置 Read 补 implementation-writing / output-layout-style / spec-quality-redlines；转换原则补六条硬规则（说明书禁"其特征在于"、实施例禁复制、效果句三段式、数字可溯源、术语一致、背景禁套话） |
| `prompts/export.md` | 增加导出前机械扫查步骤 |
| `references/output-layout-style.md` | §2 两种体裁对照表改写（九段【】式为默认体裁）+ 公式必须用 `$$…$$` 的告警；§4 语言红线扩充：AI 腔高频禁词、背景技术起句限制、效果句三段式、量化数字可溯源、公式引导句紧随公式 |
| `references/disclosure-checklist.md` | 新增"机械扫查"节（对应 consistency_scan.py 的检查项） |
| `assets/default-disclosure-template.md` | 由上游通用六节式改写为机构交底书九段【】式，并附体裁说明与"一~六"改写对应关系 |
| `tools/md_to_docx_min.py` | 增加 `![图注](png)` 嵌图支持（标准库解析 PNG IHDR、生成最小 `w:drawing` 部件与 `word/media`、`word/_rels`） |
| `tools/extract_pdf_text_min.py` | 修正 pdflatex 输出的十六进制字符串与 Form XObject 正文提取 |

撰写方法论另参考（**未复制其文件，仅作方法来源**；许可证情况经 GitHub API 核验，2026-10-13）：

- [xstongxue/best-skills](https://github.com/xstongxue/best-skills)（Apache-2.0）→ `skills/patent-write/**`：具体实施方式的撰写规则、附图引用规则、公式七规则、drawio 制图惯例；
- [cat-xierluo/legal-skills](https://github.com/cat-xierluo/legal-skills)（仓库未附许可证文件）→ `skills/code2patent/**`：交底书结构与模板思路；
- 广州凯东《发明专利授权率提升关键：最优实施例原则的撰写与应用策略》：最优实施例原则与特征储备库写法。

由于上述上游许可与本仓库不同（Apache-2.0 / 无许可声明），本仓库**未收录**这两个仓库的任何文件；
如你希望引用其内容，请自行获取并遵守其各自许可。

## 2. skills/paper2patent

**上游**：[7toCR/paper2patent](https://github.com/7toCR/paper2patent)（MIT，Copyright (c) 2026-present [7toCR]；URL 经 GitHub API 核验，2026-10-13）。
本仓库随附其 17 个文件（`SKILL.md`、`LICENSE`、`references/`×10、`scripts/`×5、`assets/example_patent_content.json`、`agents/openai.yaml`）。

**本仓库修改过的文件**：

| 文件 | 修改内容 |
|---|---|
| `SKILL.md` | 增加 DSH 运行适配节（工具名映射、离线工具、补拉通道、降级规则、与 `patent-disclosure` 的 draw 模式衔接），并记录冒烟运行结论（本机无 LibreOffice，PDF 导出步骤不可用时应降级） |
| `references/quality-checklist.md` | 新增 §A2「文本层缺陷」：指向 `patent-disclosure` 的 `tools/consistency_scan.py` 与 `references/spec-quality-redlines.md`，补齐上游 checker 未覆盖的成稿文本缺陷（公式空悬、错字、术语漂移、权利要求用语混入、无源数字、段落复制、附图引用不符） |

其余文件保持上游原样。**署名与许可要求**：再分发或以本仓库为基础发布衍生作品时，请保留
`skills/paper2patent/LICENSE` 与 `skills/patent-disclosure/LICENSE` 中的完整版权与许可声明。

## 3. 示例内容

`examples/figures-spec-example.json` 中的发明名称为**虚构脱敏示例**，仅用于演示附图引擎的输入契约与运行方式，
不代表任何真实申请、真实技术方案或真实数据。
