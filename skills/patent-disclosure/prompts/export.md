# A4 排版与导出（export）

## 目标

交付 **Markdown + A4 Word（.docx）**；环境允许时可建议用户自行转 PDF。

## 步骤

### 1. 确认源稿与命名

使用最新 `{案件名}_{时间戳}.md` 或用户指定路径。命名规则见 **`references/delivery-naming.md`**。

### 2. 图示（若有 mermaid）

若 3.2 / 3.4 含 mermaid 围栏且需嵌入 Word：

- 优先用 Node `mmdc` / puppeteer 转 PNG 后嵌入（见 `tools/README.md`）
- 工具不可用时：保留 mermaid 源码于 MD，DOCX 中注明「定稿前需渲染附图」，或对话中提供 mermaid 预览

### 3. 生成 DOCX

```bash
pip install -r ${SKILL_DIR}/requirements.txt
python3 ${SKILL_DIR}/scripts/render_disclosure_docx.py \
  --input {path}.md \
  --output {path}.docx \
  --base-dir {md所在目录}
```

`md_to_docx.py` 默认按 A4 常用边距与标题样式排版。

### 4. 交付清单

告知用户：

- `.md` 与 `.docx` 完整路径
- 文件名规则（案件名 + 时间戳）
- 附图/公式渲染限制（若有）
- **固定免责声明**（原样附在对话，不写入正文）

### 5. 失败降级

- DOCX 失败：仍交付 MD，给出 stderr 与手动命令
- 依赖缺失：提示 `pip install -r requirements.txt`

## 完整申请书

用户要五大部分正式文本时，转 **`prompts/upgrade.md`**（可另出申请书专用 DOCX）。
