# 推荐：延续已有代码生成研究，补上从候选到可靠选择的环节

更新日期：2026-09-05。已纳入用户最新要求：尽快出成果；优先本机 GPU，必要时可租；新工作用独立 repo 记录。

**首选 Code Generation Reliability / Verifier Evaluation / Budgeted Inference。** 以已有博客的问题为起点，做一个有独立测试、有成本评估、能演示的小型代码选择工具。PINN 作为现成的第二篇技术文章，文档助手作为后续产品方向。

## 为什么这个方向最适合现在做

已经读取 [个人博客仓库的文章源码](https://github.com/WesleyJunweiSu/WesleyJunweiSu.github.io/blob/main/app/page.tsx)。文章标题为 **Agreement is not confidence.**，主题是代码生成可靠性，而非 PINN。

文章报告：Qwen3-4B、HumanEval+ Mini，30 个开发任务、34 个校准任务、100 个测试任务；执行分歧指标没有通过预先设置的门槛，token entropy 从开发集 AUROC 0.915 降到测试集 0.598；额外候选中出现了一个可救回的答案，但实际选择器没有带来最终正确率提升；选择性准确率的改善区间跨零。这些是博客的自述结果，本次未取得原始研究仓库重新运行。

你现在已有一个可以继续追问的研究问题：**为什么“生成了正确候选”没有变成“最终选出了正确答案”？** 把这个问题做深，能形成连续的研究故事，也能减少从零探索的时间。

对公开仓库的检查还确认：

- [pinn-ad-vs-fdm](https://github.com/WesleyJunweiSu/pinn-ad-vs-fdm) 已有配置、报告、指标 CSV、图和测试，README 明确标为 Brown APMA 2070 课程项目。可以提炼技术文章，不应把其原始性质改成导师课题。README 记录 162 + 324 + 81 = 567 个前三项实验配置，另有失败诊断实验；本次未重算 CSV。
- [handwriting-to-obsidian](https://github.com/WesleyJunweiSu/handwriting-to-obsidian) 已有 TypeScript 导入、转录、图像处理、图形重建与自动链接模块。因此确有产品基础，但立刻扩展到文档 QA 会增加解析、检索、数据标注和 UI 工作。
- [xai-dgnn-predictive-maintenance](https://github.com/WesleyJunweiSu/xai-dgnn-predictive-maintenance) 公开仓库存在。简历里 YOUR_GITHUB_USERNAME 占位链接可以修正到真实链接；是否足以复现论文结果仍需另外检查。

这次没有找到旧 codegen 研究仓库的公开入口；博客指向的仓库不在公开列表中，可能是私有或访问状态不同，不能直接断言不存在。

## 方向排序

以下为结合个人已有材料的判断，不是招聘市场统计或录取概率。

| 方向 | 现有基础 | 最能补强的申请 | 现在的安排 |
|---|---|---|---|
| 代码生成选择器与验证器可靠性 | 完整的博客研究问题、Qwen3-4B 实验记录描述 | SWE、AI/ML、research engineering；部分 empirical safety fellowship | 唯一主项目 |
| PINN 数值失败诊断与成本 | 已有公开代码、配置、图表和报告 | Scientific ML、研究实习、技术面试 | 提炼现有成果，尽快形成第二篇文章 |
| 证据溯源的文档助手 | Obsidian 插件、金融文档与检索经验 | SWE、Applied AI/ML | 主项目完成后再做 |
| 时间序列漂移、异常检测与校准 | GNN、C++ 传感器、工业数据经验 | DS、工业 ML、Motional 类岗位 | DS/工业方向成为主目标时替换主项目 |
| CoT 干预与监控 | BAIST 学习/复现背景 | AI safety fellowship | 单独研究分支，不与输出正确性混为一谈 |

通用产品 DS 岗位仍可能要求 SQL、因果推断和实验分析，代码生成项目不会自动覆盖这些要求。机制可解释性 fellowship 也不等同于代码评测；申请时应对齐具体导师课题。

## 主项目的具体题目

暂定研究标题：**When Should a Code Selector Abstain? Evaluating Imperfect Tests under a Fixed Compute Budget**。

项目名：`codegen-verifier-study`。

面试的一句话：我先发现模型多次生成同样答案并不能稳定说明正确性；接着构建一个执行评测系统，研究生成测试本身有错时，如何选择候选、避免错误接受，并量化计算成本与拒答的取舍。

首版做 Python 函数级任务。输入题目、公开样例和若干候选代码；输出被选代码、支持/反对它的测试证据、成本，或者“当前证据不足以选择”。先交付 CLI 和 HTML/JSON 报告即可，无需先做编辑器插件、通用 coding agent 或复杂前端。

这不是“首次用测试选代码”。近期已有直接近邻工作，详见 [related-work.md](related-work.md)。可研究的窄问题是：**在小模型、固定预算及存在错误测试的条件下，选择器什么时候会过度自信；过滤低质量测试和适当拒选是否能改善错误接受率，同时保留有用覆盖率？** 尚未证明其新颖性，也不预设能得到正结果。

从已知负结果走到可验证改进，或清楚证明某类改进无效，都能构成研究成果。不要为了让简历出现“提升”而换指标或重复调同一测试集。

## 和近期顶会研究怎样衔接

| 论文 | 正式状态与主题 | 项目要借鉴什么 |
|---|---|---|
| [S*: Test Time Scaling for Code Generation](https://aclanthology.org/2025.findings-emnlp.865/) | EMNLP 2025 Findings；候选覆盖、区分性输入和执行辅助选择 | 最直接的基线。选择器要能超越简单共识；简化复现须标明差异 |
| [HARDTESTGEN](https://iclr.cc/virtual/2026/poster/10006843) | ICLR 2026 主会 Poster；构造高质量代码测试/验证器 | 测试也可能出错，要评估错误接受和错误拒绝，首版无需复现 RL 训练 |
| [Dynamic-Static Synergistic Selection](https://ojs.aaai.org/index.php/AAAI/article/view/40481) | AAAI 2026 Technical Track；结合静态分析与动态执行应对有缺陷的生成测试 | 与“过滤测试后选候选”高度接近，是必须读的最近邻 |
| [CodeHacker](https://aclanthology.org/2026.acl-long.108/) | ACL 2026 主会；为竞赛程序生成揭示缺陷的测试 | 从重复随机输入，转向能区分候选的边界情况 |
| [AlgoVeri](https://arxiv.org/abs/2602.09464) | 列于 [ICML 2026 官方目录](https://icml.cc/Downloads/2026)；Dafny、Verus、Lean 的形式化验证基准 | 用来划清执行测试与证明正确的边界；不适合为了赶时间首版上手 |
| [DSCodeBench](https://ojs.aaai.org/index.php/AAAI/article/view/40540) | AAAI 2026 Technical Track；较真实的数据科学代码生成 | 第二阶段可扩到数据处理任务，为 DS/AI 工程申请增加关联 |

这组论文表明相关工作已经从单纯多采样推进到测试质量、候选选择和可验证性。本次是针对个人选题的代表论文检索，不是顶会所有研究方向的数量统计。

对你而言，最合理的研究层级是“严谨复现 + 一个有意义的小扩展 + 实际工具”。是否投稿 workshop、Findings 或主会，要在读完近邻全文、得到结果后决定，不能现在承诺。

## 第一轮实验怎样设计

完整定义见 [pilot-protocol.md](pilot-protocol.md)。

先固定同一批候选，对比：首个候选、执行共识、基于测试的选择、过滤低质量测试的选择、过滤后允许拒选。随机选择和随机拒选是必要对照。之后再做包含全部生成与验证成本的端到端比较。

隐藏测试和参考答案只能由最终评估器访问，不能进入选择器、测试生成器或路由策略。多个候选的一致输出不能直接当作预期正确输出；它们可能共享错误。

旧博客用过的 164 道题已经提供研究洞见，后续只能标为开发或历史复现，不能再称 untouched holdout。优先审计一个新的 MBPP+ 子集，并建立新的开发/校准/测试清单。若此前也用过 MBPP+，改用另一个未使用的数据分区。公开基准仍可能存在模型预训练污染，要在报告中说明。

先用 20 题检查管线与成本，再目标扩展到约 100–200 道独立任务。不同候选、种子和输入不能算作独立任务。模型比较时按任务配对，统计区间按任务聚类，若任务太少只报告探索性结论。

核心指标：最终返回正确答案占所有任务的比例；选择覆盖率；返回答案中的错误率；oracle candidate accuracy 与实际选择准确率之间的差距；错误测试导致的误拒/误接；总 token、执行次数、延迟和峰值显存。拒绝所有任务不会得到好结果。

## 怎样让人看到你确实做过工程

必须交付的不是一张排行榜，而是以下可检查的证据：

- 固定模型/数据版本、prompts、采样设置、任务清单及每题候选和选择结果。
- 能恢复中断、缓存重复计算、限制超时和资源的执行管线。
- 将生成代码放在隔离 Linux 容器或等效隔离环境执行；子进程超时或 WSL 本身都不等于安全沙箱。
- 用已知正确、错误、超时和异常输出校验评估器，确保不是 evaluator bug 带来改善。
- CLI/报告能展示一个完整例子：原选择如何失败，哪些测试有效/无效，最终是否选择正确、花费多少。
- 找少量真实 Python 任务试用，记录人工修正与失败；实际完成后再写使用人数和使用效果。

现阶段不能写 deployed in production。若只有本地实验，写 built and benchmarked；若有同学实际试用，写 pilot-tested，并说明规模。

## 本机优先与时间安排

已实测硬件识别：RTX 5070 Ti Laptop GPU，12,227 MiB 显存。旧博客使用 Qwen3-4B BF16，因此先保持该模型与非 thinking 模式的可比性。[官方模型卡](https://huggingface.co/Qwen/Qwen3-4B)确认模型为 4B 并支持模式切换。

4B 的 BF16 权重粗算约 8 GB，仍需为 KV cache、激活和运行时留空间。这只是容量估算，不能保证特定长度或批量可运行。先 batch=1、短上下文、限制生成长度并实测；必要时切量化，但量化结果须与旧 BF16 结果分开报告。首版不需要训练。

模型顺序加载，不同时驻留两个。只有当 20 题试跑表明本机耗时影响截止日期，或需要第二模型/长上下文复核时，才考虑租 24GB/48GB GPU。用户表达了可以租卡的偏好，但未确定费用上限，本次没有购买或启动付费实例。

| 阶段 | 工时估计与产出 | 达成条件 |
|---|---|---|
| 前 1–2 天 | 约 4–8 小时：找回旧 codegen 日志、核对 EvalPlus 标签、本机试跑 20 题 | 代码与依赖可用；否则先补环境，不保证两天有结果 |
| 第 3–7 天 | 累计约 15–25 小时：固定候选选择实验、错误测试分类、初步成本表 | 有足够正确/错误混合候选，指标口径稳定 |
| 第 8–14 天 | 累计约 30–45 小时：新测试集、小型 CLI、报告 v0.1 和 demo | 策略已冻结，独立评测完成；只写已验证的项目事实 |
| 第 15–21 天 | 约再 15–25 小时：第二模型、更多种子、真实任务或 DSCodeBench 小子集 | 前一阶段已有可解释结果，才扩大范围 |

上述日历依赖集中投入，并非按每周 12 小时能保证两周完成。研究结论不能承诺按时“显著提升”；最快先交付可靠评估系统和诚实的阶段报告。

第 7 天止损：如果候选里几乎没有正确答案，就先修生成覆盖率；若候选多数相同，先测多样性；若生成测试大多不合法，先做测试质量诊断。不要把不同瓶颈混在一个分数里。未改善也保留失败结果，形成后续题目的依据。

## 博客与简历的安排

现有文章：Agreement is not confidence，记录不确定性信号失效。

新文章建议标题：**Finding a Correct Program Is Easier Than Selecting One**。它讲执行测试、候选选择及拒选的研究结果。不要先写“我们成功改善”，等数据决定标题副句与结论。

工程文章可作为同项目附文：**Building a Reproducible Code Evaluation Harness on a 12GB GPU**。重点放缓存、沙箱、超时、任务清单、错误追踪与成本，不写成库安装教程。

PINN 文章从已有报告提炼：**A Smooth PINN Solution Can Still Be Wrong**。展示制造解、误差热图、独立残差审计和限制。Task 4 的宽步长同时改变截断误差与越界比例，因此要把“越界是唯一原因”的说法收紧；若想做因果解释，应追加固定步长的 safe/unsafe 对照。Task 3 中不同 stencil 的有效配点数不同，也应在公平性讨论中说明。

简历主线可以是：**可靠的 ML 系统与实证评估：从数值计算的错误诊断，到代码生成的验证与选择。**

完成后根据岗位选择两条事实即可。以下是模板，方括号必须填真实结果：

SWE：Built a reproducible Python code-evaluation CLI with isolated execution, timeout recovery, and per-task tracing; benchmarked [N] tasks at [measured latency/cost].

AI/ML：Compared [K] candidate-selection strategies under matched compute budgets; measured [supported change] in incorrect-acceptance rate at [coverage] on [held-out benchmark].

Research：Investigated correlated verifier failures in code generation, separating candidate coverage from deployed selection accuracy; released a technical report with [supported finding], paired analyses, and negative results.

独立完成就放 Independent Research / Projects。只有团队实际参与或认可时才归到 BAIST；这个新项目不能自动算成 BAIST 的科研成果。

## 七版简历中先统一的内容

已完整读取并检查页面：

- [motional.pdf](D:/chrome下载/motional.pdf)、[eluvio_ai_ml_intern.pdf](D:/chrome下载/eluvio_ai_ml_intern.pdf)：工业传感器、GNN、LLM 文档及视觉项目基础。
- [msra.pdf](D:/chrome下载/msra.pdf)：最详细的 PINN 实验和 CoT harness 描述。
- [google_sde_early.pdf](D:/chrome下载/google_sde_early.pdf)：Obsidian 软件项目与工程侧重点。
- [anthropic_fellow.pdf](D:/chrome下载/anthropic_fellow.pdf)、[openai_aisafety.pdf](D:/chrome下载/openai_aisafety.pdf)：BAIST、安全评测与研究定位。
- [字节llm.pdf](D:/chrome下载/字节llm.pdf)：post-training / PPO / DPO 表述。

毕业时间有 May/Dec 2027，学位名称有 Data Science/DECES，需以当前正式信息统一。BAIST 项目在 studying、replicating、reproduced 之间变化，需核对真实完成状态。DeepSeek 完整模型、蒸馏模型、API 调用和实际微调对象要写清具体版本。PPO 与 DPO 的工作分别说明。98.93%、67.47%、50,000+/day 等数字必须能解释数据划分、分母与个人贡献。

这些材料目前是简历自述，公开项目也只是部分证据，本次没有逐项认证所有工作经历或数值。

## 本次实际完成了什么

已对照七份简历、读取个人博客源码与三个相关项目的公开文件列表/部分报告、查询近期相关论文、识别本机 GPU，并建立本地研究规划目录及配置草案。

尚未运行新模型实验，尚未复现旧 codegen 结果，尚未创建 GitHub 远端仓库或发布文章。本地仓库用于开始记录新工作，远端发布状态以实际操作为准。
