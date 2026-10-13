# 查新与现有技术对比（search）

## 必做时机

在交底书 **1.1 现有技术** 定稿前执行；创意审核后若用户关心重复风险也应执行。

## 检索渠道（优先国知局，再降级）

### A. 中国专利公布公告（优先）

1. **站点**：http://epub.cnipa.gov.cn/（仅 `epub.cnipa.gov.cn`）
2. **工具**：`python3 ${SKILL_DIR}/tools/cnipa_epub_search.py {词块}`
3. **检索词（生成命令前必做）**

   - 从本案方案归纳 **2～8 个相关语义块**（术语、名词短语、名动组合）
   - **禁止**整句长中文作唯一参数
   - **每次 Bash 只传一个词块**；2～8 块对应 2～8 次独立调用
   - Agent 自行按 `pub_number` 合并 `EPUB_HITS_JSON`

   示例：

   ```bash
   python3 ${SKILL_DIR}/tools/cnipa_epub_search.py 知识库
   python3 ${SKILL_DIR}/tools/cnipa_epub_search.py 检索增强
   python3 ${SKILL_DIR}/tools/cnipa_epub_search.py 大语言模型
   ```

4. **依赖**（可选）：

   ```bash
   pip install -r ${SKILL_DIR}/tools/requirements-cnipa.txt
   python -m playwright install chromium
   ```

5. **解析**：stdout 唯一一行 `EPUB_HITS_JSON:` + JSON 数组；按 `pub_number` 去重合并

6. **`abstract` 必用**：对每条非空 `abstract`，须先理解再概括写入查新笔记与 1.1；禁止仅凭标题臆造；禁止大段粘贴官方摘要

7. **降级**：命令失败、超时、无 Playwright、空数组 → 进入 B

### B. WebSearch / Google Patents（降级）

- Google Patents：`https://patents.google.com/patent/CN…/en`
- Google Scholar：中文学术补充
- 每条记录须 **可核验 URL**，禁止编造

## 分析要求

对高度相关现有技术逐项记录：

- 专利号 / 文献标识
- 技术方案要点（与国知局 abstract 一致）
- 应用场景
- 局限性
- 公开源 URL

## 与本案对比

输出 **《查新与区别分析》**：

- 最接近现有技术 1–3 件
- 本案区别特征
- 重复/新颖性 **初步** 风险（高/中/低 + 理由）
- 建议写入交底书 1.1 / 1.2 / 第四章的要点

## 写入交底书

查新结论须写入 **第一章 1.1**（分类 + URL + 消化后概括）及 **区别论述**（第四、五章回扣）。
