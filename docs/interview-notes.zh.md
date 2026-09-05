# 面试讲解与简历表述：当前能讲到哪里

2026-09-05，第一轮实验完成。方向是 **LLM 代码生成的测试可信度、候选选择与拒答**，连接 SWE 的工程实现、AI/ML 的推理实验、DS 的统计评估，以及 fellowship 需要的问题定义和可复现研究。

## 当前可使用的简历表述

**LLM Code Verification & Selection — Independent Research Project, ongoing**

- Built a resumable Qwen3-4B evaluation pipeline with isolated Linux execution, frozen task splits, and label-blind candidate selection; evaluated 80 code candidates across 20 MBPP+ development tasks.
- Audited 134 historical generations across evaluators, identifying seven label discrepancies; investigated generated-test reliability through a controlled parser ablation and a reproducible technical report.

不能改写成“提升准确率 7%”“实现可靠拒答”“顶会级新方法”或“已部署服务真实用户”。项目仍在研究阶段。

## 一分钟讲法

“我之前研究过代码生成的不确定性，发现多个答案一致并不代表正确。这次进一步问：如果模型自己出的测试也可能错，怎么选答案才有依据？我复用本机 4B 模型，固定候选池，把选择器与隐藏评分隔离，在 Linux 容器里执行。首轮 20 题，生成测试没有超过直接取首个答案；120 条测试里有 25 条拒绝参考实现。我追加不调用模型的格式消融，证明补全 assert 仍不能解决选错的问题。现在可以把候选多样性、测试预期答案错误和选择机制分别研究。”

## 现场演示

```bash
python scripts/selector_cli.py --task Mbpp/564 --method public_tests
python scripts/selector_cli.py --task Mbpp/564 --method filtered_abstain
```

第一条展示公开测试如何选择样本 3，并打印保存的代码；第二条展示固定拒答规则未返回答案。CLI 展示真实结果，不重新执行代码。

## 需要理解的追问

1. **为什么 80 个样本不是 80 个独立问题？** 同题的候选和测试相关，统计按题重采样，不能虚增样本量。
2. **为什么不用参考实现筛错测试？** 它属于评分端，部署时不可获得；否则隐藏答案泄漏给了选择器。
3. **为什么 0 次误答不算成功？** 当前全部拒绝，覆盖率为零，条件准确率没有定义，没有使用价值。
4. **旧结果为什么从 75 到 82？** 代码相同，是评测协议/环境变化。Linux 控制实验复现两个队列顺序导致的误超时、一个大整数日志转换错误和两个静态拦截；另两个历史超时未复现，不能声称全部解释。
5. **为什么不是完整 S* 复现？** 当前按测试通过数排序，没有复现其完整区分输入和推理流程。
6. **下一步为什么研究多样性？** 13/20 题的四个候选文本相同，候选池上限低；需要记录增加多样性的成本，再检验测试可信度，最后使用确认集。

## 把项目变成自己的能力

新增工程案例：旧评测器先等待子进程退出，再读取队列；子进程却在等待父进程读取约 34 MB 的输出日志。只交换读取/等待顺序，同一候选就能通过。这可以讲清进程间通信、日志设计和评测偏差，但它不是模型准确率提升。

先亲自跑两个演示，读懂 `selection.py`，用 Mbpp/564 和 Mbpp/607 解释公开证据与隐藏评分的区别，再参与下一轮假设和结果判断。面试竞争力来自能解释、复现和修改方法。后续博客应说明模型/自动化辅助与自己实际完成的研究判断。
