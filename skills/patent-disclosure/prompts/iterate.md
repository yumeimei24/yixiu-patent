# 交底书问答迭代（iterate）

## 启用条件

用户要在**已有交底书**上：回答问题、补充章节、修正参数/事实、调整表述、合并新材料。

**不要求**用户说「迭代」；有交底书路径或上文刚交付草稿时默认本模式。

## 执行前（必做）

1. **`Read`** `prompts/iteration_context.md`
2. 按意图 **`Read`**：
   - 补充/扩展 → `prompts/merger.md`
   - 纠错/不符 → `prompts/correction_handler.md`
3. **`Read`** 当前交底书全文

## 分支概要

| 分支 | 模板 | 场景 |
|------|------|------|
| merger | `merger.md` | 新材料、补实施例、第五章书式强化 |
| correction | `correction_handler.md` | 错误、参数不一致、保护点调整 |
| 问答补充 | 本节后段 | 用户提问 → 解答 → 可写入稿内 |

## 问答补充

用户提问 → Agent 解答 → 若答案可写入交底书：

1. 说明将补充到哪一节
2. 写入后走 **merger** 落盘流程
3. 若涉及新现有技术，建议 **search**

## 落盘与留痕（必做）

- **命名**：`references/delivery-naming.md`（`{案件名}_{YYYYMMDDHHmmss}.md` + 同名 `.docx`）
- **不覆盖**旧稿（除非用户要求）
- **修订对话记录**：每轮交付后追加 `交底书修订对话记录.md`

```bash
python3 ${SKILL_DIR}/tools/iteration_dialog_log.py \
  --case-dir "{案件目录}" --kind merge|correct \
  --user "..." --summary "..." --artifacts "xxx.md,xxx.docx"
```

- 对话中输出 **「合并摘要（留档）」** 或 **「纠正摘要（留档）」**（见 merger/correction 模板）

## 循环

直到用户满意；满意后 **export** 或 **upgrade**。

## 禁止

- 迭代意图下默认回到 convert/draft 全流程
- 完成迭代却不更新修订对话记录
- 不编造用户 Q&A 中未确认的技术事实
