# 译文中文规范（translation_zh / translation_si_zh）

## 核心区分

| 类型 | 处理方式 |
|------|----------|
| **专业术语 / 领域名词** | 中文 + 括号英文 **可保留**（后文重复亦可） |
| **普通英文词** | 在中文句中**应译出**；具体依**全文语境**判断 |
| **专名、缩写、化学式、URL** | 保留 |
| **章节 / 小节标题** | **中文译名（English Title）**，便于对照 PDF |

**不要**追求「零英文括号」。**要防止**的是：正文句中普通词汇漏译、未理解全文就逐句硬译。

## 章节标题格式

各级 Section / Subsection 标题：**先中文译文，括号附原文英文**。

```
## 1 引言（Introduction）
### 2.3 定量结果（Quantitative Results）
#### Supplementary Note S1（Supplementary Note S1）
```

图注、表注标题同理。标题括号英文是**对照注释**，审校时勿删。

## 翻译流程（两遍，必做）

### 第一遍：生成
- 完整、逐段、忠实翻译（见 `translation.mdc`）
- 术语可写 **中文（English）**

### 第二遍：通读审校
1. 结合原文 `content.md`（+ SI）**理解全文**后再读译文
2. 从头到尾通读 `translation_zh.md`（+ `translation_si_zh.md`）
3. 检查：漏译普通词、误译、不通顺、术语不一致
4. 修正后再次快速通读

**审校以全文理解为准**，不机械套用词表。

## 常见漏译参考（非穷举、非禁词表）

以下仅供审校时联想，**不是**「见到必改」：

challenging、entire、arbitrary、off-the-shelf、understudied、dramatically、largely、non-trivial、trivial、performance、training、inference、sampling …

## 辅助检查（可选）

`python scripts/check_translation_chinese.py notes/<slug>/translation_*.md`

输出**疑似**问题行；有 flagged 项须人工结合全文判断是否修改，**不必盲从**。

## 示例

❌ `扩展 arbitrary 模型 dramatically 更快`（普通词漏译）  
✅ `扩展任意模型大幅更快`

✅ `**基序（motif）**`（专业术语，可保留括号）

✅ `## 2 方法（Methods）`（章节标题，括号附原文便于对照）

详见 `docs/CHINESE_STYLE.md`。

