# 技术交底书撰写（draft）

## 执行前

1. **`Read`** `references/regulatory-standards.md` 第二节（交底书约束）
2. **`Read`** `prompts/standards_lookup.md` 并 **WebSearch**「技术交底书 撰写规范」「国知局 专利申请文件 撰写要求」
3. **`Read`** `references/disclosure-structure.md`
4. **`Read`** `references/desensitization.md`（成稿须脱敏）
5. **`Read`** `references/delivery-naming.md`（落盘命名）
6. **`Read`** `references/disclosure-checklist.md`（完稿前内部自检）
7. 确认模板：
   - 用户提供模板 → 按其结构
   - 未提供且用户同意 → **Read** `assets/default-disclosure-template.md`

## 输入

- 《专利素材摘要》（来自 convert）或用户直接提供的材料
- 《查新与区别分析》（来自 search，若已执行）

## 撰写原则

- **须符合** `references/regulatory-standards.md` 第二节及联网检索得到的最新撰写要求
- 围绕 **技术问题 → 技术方案 → 技术效果** 组织，非论文翻译
- 三要素闭环贯穿第一至五章
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
