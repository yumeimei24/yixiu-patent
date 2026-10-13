# draw 模式 — 专利附图 / 技术路线图生成

触发：用户要求画专利附图、技术路线图、流程图、系统框图、示意图；或 draft/export 完成后需要配图。
前置：`Read` `references/patent-figure-spec.md`（本模式规范）。

## 工具链（离线可用）

- **引擎**：`paper2patent` 技能的 `scripts/generate_patent_drawings.py`（纯标准库 SVG 渲染 + Pillow 出 PNG；Sugiyama 分层布局、正交连线、内置附图校验）。`${SKILL_DIR}` 指向本技能时，引擎在同级 `paper2patent` 技能目录：`${SKILL_DIR}/../paper2patent\scripts\`。
- **输入**：一个"专利内容 JSON"，其中 `drawings` 数组每项一幅图的显式节点/边规格（契约见 `references/patent-figure-spec.md` §2）。
- **命令**：
  ```bash
  python <paper2patent>/scripts/generate_patent_drawings.py <content.json> -o <outdir> --prefix <案件名> --update-json
  ```
  输出 `<prefix>_图{n}.svg` 与 `.png`（300dpi），并把 `drawing_assets` 校验结果写回 JSON。

## 工作流

1. **从交底书抽取图幅清单**：逐条对照正文【相关附图】/附图说明，确定每幅图的类型（整体流程 / 模块流程 / 系统框图 / 结构示意 / 数据流）与对应正文小节（写进每幅图 `source` 字段，供校验与迭代）。
2. **节点/边抽取（只画正文有的）**：节点 = 正文步骤或系统模块；边 = 正文明示的先后/分支/循环关系。**禁止推断正文没有的连接**；判断分支（是/否）、环回（回到某步）必须在正文中有依据。**编号与正文一致**：图1 节点=正文一级步骤号（S1—SN）；细化图用二级编号（201…、301…、401…），并在实施方式中定义；**图1 采线性主流程**（判断框/回边放细化图，见 `references/patent-figure-spec.md` §2）。
3. **附图标记与编号**：图1 用正文一级步骤号（S1…SN）；细化图用二级编号；模块/部件用 101、102…；同一标记全文同义。标记可写在标签内（"S1 获取岗位文本"）或节点 `ref` 字段（画在框旁）。
4. **生成与校验**：运行引擎（`python <paper2patent>/scripts/generate_patent_drawings.py <规格.json> -o <输出目录> --prefix <案件名> --update-json`）；逐图读取返回的 validation：`passes=false` 或 `issues` 非空时按提示改规格（拆图、缩短标签、调整 `nodes` 顺序）重跑，直至每图 `[ok]`；`--update-json` 会把校验结果写回规格 JSON 备查。
5. **目视复核（必做）**：逐张打开 PNG 检查框体、文字、箭头方向、有无重叠或串行（上游规范的硬要求）。若当前会话模型不能读图，改用 SVG 文本核对（`grep` 每个节点标签与边）＋ PIL 像素统计（灰度极值非 0/255 且非空白、长宽比合理），并在交付信息中明确请用户人工目视复核；宁可报告"未能目视"也不要默认通过。
6. **回写与交付**：附图说明中的"图N为…"与生成图一一对应；`.md` 交付时在文末附图清单中列出 SVG/PNG 相对路径；`.docx` 交付时用 `generate_patent_docx.py` 或 `md_to_docx_min.py`（已支持 `![图注](png)` 嵌图）。交付信息中报告每图的校验结论与目视复核状态。

## 硬性红线（规范全文见 references/patent-figure-spec.md）

- 纯黑白线条、白底；禁彩色渲染、照片、灰度、渐变、logo、商标。
- 图内不写图号与图题（"图1"写在正文，不画进图内）；引擎会拒绝标签中含"图\d"字样。
- 标签换行不断字；每图节点 ≤16，超出必须拆分或分（a）（b）幅。
- 文字打印后高度 ≥2.2mm；图幅适配 A4 内容区（15cm×20cm），引擎按此校验。
- 流程图单入口单出口优先；判断框菱形并标注"是/否"分支；环回走侧通道，不与主流交叉。

## 迭代

用户对某图提修改时：只改该图的 `nodes/edges`，重跑引擎后**同前缀覆盖该图**或加后缀另存；在 `交底书修订对话记录.md` 中记录改了哪幅图、改了什么、依据正文哪一节。不重画用户未提的图。
