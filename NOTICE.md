# NOTICE — 文件级来源、许可与署名

本仓库 `yixiu-patent` 汇集并增补了两套开源技能的内容。**上游许可与版权声明保留在各技能目录内**
（`skills/patent-disclosure/LICENSE`、`skills/paper2patent/LICENSE`），本文件说明逐文件来源。

## 1. skills/patent-disclosure

**上游**：[yjmm10/patent-skills](https://github.com/yjmm10/patent-skills) — MIT，Copyright (c) 2026 patent-skills contributors（vendored 2026-08）。

沿用上游的文件（未作实质修改）：

- `prompts/`：`intake.md`、`review.md`、`convert.md`、`search.md`、`standards_lookup.md`、`draft.md`、`iterate.md`、`merger.md`、`correction_handler.md`、`export.md`、`upgrade.md`、`iteration_context.md`
- `references/`：`regulatory-standards.md`、`patent-law-basics.md`、`patentability-criteria.md`、`claims-rules.md`、`disclosure-structure.md`、`disclosure-checklist.md`、`desensitization.md`、`delivery-naming.md`
- `assets/default-disclosure-template.md`
- `tools/`：`extract_docx_text.py`

**本仓库新增**（上游没有，由本仓库整理撰写）：

| 文件 | 说明 |
|---|---|
| `prompts/draw_figures.md` | draw 模式：交底书 → 图幅清单 → 节点/边抽取 → 引擎生成与校验 → 目视复核 → 交付 |
| `references/patent-figure-spec.md` | 专利附图规范：法定要求、引擎 JSON 契约、三条硬规则、校验清单 |
| `references/implementation-writing.md` | 具体实施方式规范：功能定位、10 段骨架、附图引用规则、公式七规则、退稿自查 |
| `references/output-layout-style.md` | 交付体裁与版面规范（样稿优先、公式顺号、语言质量红线） |
| `references/lessons-learned.md` | 实战复盘清单（补点方法、测量类客体强化、转述他人框架类写法、读料技巧） |
| `tools/verify_figures.py` | 附图程序化复核（SVG 标签齐全 + PNG 像素统计） |

**本仓库修改过的上游文件**：

| 文件 | 修改内容 |
|---|---|
| `SKILL.md` | 增加 DSH 运行适配、draw 模式路由、模板策略第 0 步、检查清单条目、本地新增参考索引；上游版权与版本信息保留 |
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

其余文件保持上游原样。**署名与许可要求**：再分发或以本仓库为基础发布衍生作品时，请保留
`skills/paper2patent/LICENSE` 与 `skills/patent-disclosure/LICENSE` 中的完整版权与许可声明。

## 3. 示例内容

`examples/figures-spec-example.json` 中的发明名称为**虚构脱敏示例**，仅用于演示附图引擎的输入契约与运行方式，
不代表任何真实申请、真实技术方案或真实数据。
