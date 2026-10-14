# 发布到 GitHub

本目录已按可发布仓库整理完毕（技能、脱敏示例、README/NOTICE/LICENSE/.gitignore）。
**当前机器未安装 git**（`PATH` 与常见安装路径均无 `git.exe`），因此本仓库以"可直接 push 的目录"形式交付。

> **实际推送通道**（2026-10-14 起验证可用）：本机不装 git 也能更新本仓库——走 REST Git Data API
> （创建 blob / tree / commit，再更新 `refs/heads/main`），配套脚本在 DSH 的 `github-upload` 技能下
> （`push_via_api.py` 增量提交、`history_rewrite.py` 重写历史、`verify_published_repo.py` 复验）。
> 推送身份必须用 GitHub 匿名邮箱，原因见第 4 节最后一条。

## 1. 安装 git

- Windows：`winget install --id Git.Git -e --source winget`，或从 <https://git-scm.com/download/win> 下载安装；
- 安装后重开终端，确认：`git --version`。

## 2. 首次发布

在本目录（`yixiu-patent/`）执行：

```bash
git init -b main
git add -A
git commit -m "feat: 中国发明专利撰写全流程技能集（交底书 + 附图 + A4 导出 + 申请书）"
git remote add origin https://github.com/<你的用户名>/yixiu-patent.git
git push -u origin main
```

仓库需先在 GitHub 网页端创建（空仓库，**不要**勾选初始化 README，避免首推冲突）。
若使用 SSH：`git remote add origin git@github.com:<你的用户名>/yixiu-patent.git`。

## 3. 后续更新

```bash
git add -A
git commit -m "docs: 更新附图规范"      # 或 fix:/feat:
git push
```

## 4. 发布前检查清单

- [ ] **脱敏**：用本机路径关键词、内部选题名、真实统计数字各扫一遍（`grep -rn "<关键词>" .`），应无命中。**不要把关键词本身写进本文件**——公开仓库里的示例同样构成泄漏；
- [ ] **许可**：根 `LICENSE` 与两个技能目录下的 `LICENSE` 齐全，`NOTICE.md` 的来源表与实际文件一致；
- [ ] **无案件材料**：`outputs/`、`.patent-skill-research/`、任何 `.docx` 交底书与真实附图**不得**进入提交（`.gitignore` 已排除，仍建议 `git status` 复核）；
- [ ] **无凭证**：不含 token、cookie、企业名与联系人信息；
- [ ] **提交身份**：`git config user.email` 必须是 GitHub 匿名邮箱（`<id>+<login>@users.noreply.github.com`），公开仓库的首次提交会永久暴露该邮箱；
- [ ] **许可识别**：`LICENSE` 为标准全文（GitHub 才会显示 MIT 徽标）；附加说明放 `NOTICE.md`；
- [ ] **行尾一致**：Windows 上写入的文件统一 `newline="\n"`，避免提交后被 autocrlf 归一化而产生"假差异"。
- [ ] **可运行**：`examples/figures-spec-example.json` 能跑通附图引擎与复核脚本（见 README「快速开始」）；
- [ ] **README 路径**：本机绝对路径已替换为 `${SKILL_DIR}`、`<workspace>` 等占位符。

## 5. 备选：不使用 git

GitHub 网页端 **New repository → uploading an existing file** 可逐文件上传（每次最多 100 个文件），
但会丢失提交历史、且需手工处理目录层级，**仅在无法安装 git 时使用**。
另一条路：把本目录打包为 zip 上传到 Release，供他人下载后自行放入技能目录。

## 6. 如果之后让我（Agent）代推

本机 pwsh / curl / git 的凭证通道无外网，只有 **python/urllib** 有出口。
届时需要你提供：GitHub 用户名、仓库名、具备 `repo` 权限的 token（建议 fine-grained、限本仓库、用完即撤）。
推送将通过 GitHub REST Contents API 逐文件上传（无 git 历史），因此**仍建议优先在本机 git 推送**。
