# 从 Mac 和 iPhone 接续本机研究项目

本项目的模型权重、GPU、生成环境与部分私有数据位于 Windows。需要使用这台显卡时，把 Windows 设为 ChatGPT/Codex Remote 的**主机**，Mac 和 iPhone 作为控制端。远程任务读取和运行的是主机上的项目、工具与权限。仅在 Mac 克隆 GitHub 仓库可以查看代码和已提交记录，不会自动获得 Windows 的模型和显卡。

## 一次性配对

1. 在 Windows ChatGPT 桌面应用中，进入 **Settings → Connections → Control this Mac or PC → Set up / Add**，打开对这台电脑的远程连接，完成账号验证。更新应用，并保持 Windows 联网、登录同一 ChatGPT 账号及工作空间、运行应用且不休眠。远程设置会显示供手机配对的二维码。
2. 用 iPhone 扫描 Windows 显示的二维码，在 ChatGPT 手机应用中完成相同账号/工作空间的配对。之后从手机的 **Remote** 选择 Windows 主机，打开现有研究任务或发起新任务。若没有 Remote，先更新手机 App；功能可用性受发布进度及工作空间设置影响。
3. 在 Mac 的 ChatGPT/Codex 桌面应用中，若有 **Settings → Connections → Control other devices**，把这台 Windows 主机加入可控制设备。Mac 的可用性同样受发布进度影响。选 Windows 作为任务执行位置，才能使用它的 GPU 和本地模型。
4. 在 Windows 桌面应用的 Projects 中，把 `C:\Users\Asuka\Documents\ChatGPT\Project Builder\codegen-verifier-study` 单独设为一个**本地项目的主文件夹**。目前保存的项目是上级 `Project Builder`；只有研究仓库成为主文件夹时，新任务才会自动发现仓库根目录的 `AGENTS.md`。Remote 项目目前只支持一个文件夹。已有任务已重命名并置顶为 **Codegen Verifier Study · 研究与实验**，可直接继续。

配对和账号验证需在你的设备上完成。`AGENTS.md` 是 Codex 的项目指引，用于跨会话读入研究规范；它本身不提供网络远控，也不是常驻后台服务。新任务先读 `PROGRESS.md` 和最新的 run journal，检查运行进程与 GitHub Actions，再决定下一步。之前的 180 题确认集已经完成评分，不能作为新策略的未见验证集。

官方文档：[Remote connections](https://learn.chatgpt.com/docs/remote-connections)、[Codex Remote](https://learn.chatgpt.com/docs/remote)、[AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)。
