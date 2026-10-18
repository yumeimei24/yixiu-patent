# 技术交底书撰写（draft）

## 执行前

1. **`Read`** `references/regulatory-standards.md` 第二节（交底书约束）
2. **`Read`** `prompts/standards_lookup.md` 并 **WebSearch**「技术交底书 撰写规范」「国知局 专利申请文件 撰写要求」
3. **`Read`** `references/disclosure-structure.md`
4. **`Read`** `references/desensitization.md`（成稿须脱敏）
5. **`Read`** `references/delivery-naming.md`（落盘命名）
6. **`Read`** `references/disclosure-checklist.md`（完稿前内部自检）
7. **`Read`** `references/spec-quality-redlines.md`（十类判退缺陷：公式空悬、术语漂移、错字、AI 腔、无源数字等）
8. **`Read`** `references/anti-defensive-writing.md`（**防御性写作红线**：六种声音、模板壳改写表、必须保留清单、八问自查）——**撰写与改稿全程对照**，交稿前过八问
9. **`Read`** `references/output-layout-style.md` §4（语言质量红线）
10. 确认模板：
   - 用户提供模板 → 按其结构
   - 未提供且用户同意 → **Read** `assets/default-disclosure-template.md`
11. **文头**：正文以 `# 技术交底书` + 【发明名称】起首，**不写**「案件名称/技术联系人/专利类型」三行元信息（2026-10-18 用户约定；机构模板另有要求时从其模板）。

## 输入

- 《专利素材摘要》（来自 convert）或用户直接提供的材料
- 《查新与区别分析》（来自 search，若已执行）

## 撰写原则

- **须符合** `references/regulatory-standards.md` 第二节及联网检索得到的最新撰写要求
- 围绕 **技术问题 → 技术方案 → 技术效果** 组织，非论文翻译
- 三要素闭环贯穿第一至五章
- **反防御写作**（必做）：按 `references/anti-defensive-writing.md` 撰写——正文只保留最终成立的方案与它的技术事实，不写过程流水账、不写"可选地/在需要时/需要说明的是"式模板壳、不在效果段夹带方法间矛盾的证据；边界以"替代实施方式"承载；效果段一个主张 + 一个机理 + 一组对照数据
- **脱敏成稿**：按 `references/desensitization.md` 处理行业名、产品名、具体分类与敏感数值
- 1.1 每条现有技术含 **可核验 URL**
- 3.2 / 3.4 优先 **mermaid**（勿 ASCII 文字图）
- 含公式时设 **3.4.1 符号表**，3.5 与 3.4.1 **同形**
- 术语全文统一

## 落盘与双格式交付（必做）

**Read** `references/delivery-naming.md` 并严格执行：

1. 从 `**案件名称**：` 提取并规范化案件名
2. 文件名：`{案件名}_{YYYYMMDDHHmmss}.md` 与同名 `.docx`
3. 写入 `./outputs/{案件标识}/` 或用户指定目录
4. 调用 `scripts/render_disclosure_docx.py` 生成 Word

## 定稿前机械扫查（必做）

```bash
python ${SKILL_DIR}/tools/consistency_scan.py {案件名}_{时间戳}.md
```

- 0 个 `[ERROR]` 才可交付；`[WARN]` 逐条确认（术语变体、符号重定义、无源数字、**防御性表达**必须逐条处置）。
- 报告随稿留档（同目录 `{案件名}_{时间戳}.scan.txt`），**不写入交付正文**。
- 误报说明：从 `.docx` 提取的文本若原稿用 Word 公式对象（OMML），公式会整体丢失，"公式引导句空悬"可能是提取假阳性——但同样说明源稿不该依赖公式对象，应以 `$$…$$` 书写。

## 附图随稿生成（必做，2026-10-18 起）

**draft 定稿即出图**，不再等用户单独提出（用户约定：以后每回生成专利时都一起生成图）：

1. 交底书正文定稿后，按 `prompts/draw_figures.md` 从【相关附图】抽取图幅清单并生成规格 JSON；
2. 运行引擎（`paper2patent/scripts/generate_patent_drawings.py`）逐图校验至 `passes=true`，`verify_figures.py` 复核；
3. 把生成的 PNG 以 `![图N 图题](相对路径)` 插入【交底书附图】节，再渲染 DOCX（`md_to_docx_min.py` 已支持嵌图）；
4. 每图在实施方式中至少一次"如图N所示"引用（`references/implementation-writing.md` §3）；
5. 附图校验结论随交付信息报告；模型不能读图时，明确请用户人工目视复核。
6. 用户明确表示"先不要图"时才跳过，并在修订记录中注明。

## 交付交互（必做）

每次向用户**交付定稿**（已写明 `.md`/`.docx` 路径）时，在同一条回复中追加（**不入正文**）：

1. 若希望对**第五章「技术关键点和欲保护点」**做更贴近权利要求书习惯的强化，可用一句话说明侧重点
2. 承接方式：**Read** `iteration_context.md` → `merger.md`，另存新时间戳文件，并维护 `交底书修订对话记录.md`
3. **禁止捏造偏向**：对举选项须来自当前定稿已有论述，不得编造稿外场景或模块

## 交付后

- 向用户附 **固定免责声明**（见 SKILL.md）
- 简要说明待补充项（若有）
- 询问是否需要 **iterate** / **export** / **upgrade**

## 禁止

- 正文不含「自检清单」章节
- 正文末尾不含技能/仓库脚注
- 不写入固定免责声明到交底书正文（除非用户要求）
- 交付时省略时间戳或仅给 MD 不给 DOCX（除非 DOCX 工具失败并已说明）
