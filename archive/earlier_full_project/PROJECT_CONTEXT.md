# Retail Growth and Profitability Comparison 项目背景

## 已确认的研究内容

中文题目为《互联网起家与门店起家零售商的销售增长和营业盈利能力比较：以 Amazon 北美分部与 Walmart 美国分部为例》。以 2019 为疫情前参照和销售指数基期，正式分析年度为 2019—2024，共六年。Amazon North America FY2019—FY2024，与 Walmart U.S. FY2020—FY2025 近似配对。实际日期不完全相同，应保留真实报告期间。

2019 为 Pre-pandemic baseline；2020—2021 为 Pandemic disruption；2022—2024 为 Subsequent adjustment。这是研究分组，不宣称疫情正式结束日期。一个疫情前年份只支持描述性比较，不作因果识别。

## 四个模块与当前进展

Module 01 Research Configuration 已完成，包含配置类、研究设置、JSON 保存及校验。

Module 02 Data and Database Management 已完成代码生成；用户最新总 Notebook 已包含全部十二格，第二模块基础库有 business_units 两行、financial_records 十二行；本项目已由第三模块增加三十六条指标。本归集版本复制最新 Notebook 与配置，并采用 SQLite backup 获取最新数据库快照。

Module 03 Metrics and Comparative Analysis 已生成并验证十二格代码、逐句 guide 和格式化 HTML。当前项目新增年度表十二行、指标长表三十六行（两项缺失）与阶段表六行；指标已存入 SQLite 并回读核对。阶段均值为有效年度非加权算术平均。本模块从 SQLite 查询基础记录，按配置加入分析年度与阶段，再计算销售同比、营业利润率和销售指数。2019 同比缺少前一年数据，保留缺失；本分部 2019 销售指数为 100；负营业利润需要保留。结果表已保存 study_id、config_signature、unit_id、analysis_year、metric_name 等字段。

Module 04 Reporting and Workflow 已完成，详见文末本次新增交付。已产出图表与报告，解释口径、年度配对及描述性研究限制。

## 代码与学习文件要求

用户希望使用 Jupyter Notebook，总 Notebook 位于项目根目录。代码和代码 comment 使用英文，解释用中文。每格以英文 comment 小标题开始。讲解必须具体解释代码语法、变量、参数、执行顺序和为什么这样写，不只概括业务流程。

guide 的代码与文字采用不同版式：英文代码为浅灰底、等宽字体、行号；中文解释用白底正文。module_02/module_02_code_explanation_guide.html 是排版阅读版；module_02/module_02_combined_notebook_detailed_guide.md 是逐句说明版，共二百一十条说明、十二格代码。保持可以直接复制的完整代码，不把行号和中文说明混入 Python 代码。

偏好普通字典、列表、for、if、普通函数和简单类。避免 dataclass、复杂类型标注、继承、ORM、装饰器等。类用于配置和有持续连接状态的数据库管理；纯数据转换使用普通函数。配置内容与通用框架分开，但不能仅改显示名称就继续使用旧公司的数字。

## 已修正的总 Notebook 路径

第一、第二模块共用同一个 kernel，第二模块 Cell 02 直接调用第一模块已定义的 load_study_config，不额外导入 study_config.py。先运行第一模块 Cell 01—08，再顺序运行第二模块。

根目录 study.json 的路径为 data/financial_data.csv、data/retail_comparison.sqlite 与 results。CONFIG_PATH 使用 Path.cwd() / "study.json"，因此启动 kernel 的工作目录应为本项目根目录。独立模块目录中的 Notebook 和 study_config.py 仍保留为参考。

## 数据与接口

原始两份 CSV 位于 data/raw/，由四份免费官方年报核对并人工转录。读取 CSV 不等于自动抓取财报；完整官方 HTML 未附带，链接与采用章节见 module_02/source_notes.md 和 data/raw/source_manifest.json。

raw_df 为十二行十四列，clean_df 为十二行十六列，新增 net_sales_usd_m 与 operating_income_usd_m。保存后从 SQLite 查询 financial_df，并逐字段比较以确认数据确实存入。

数据库业务单位表保存名称与口径，财务表联合主键为 unit_id 加 fiscal_year。金额统一为百万美元，当前只支持 USD 数量级转换，不支持汇率转换。Walmart 采用净销售额而非含其他收入的总收入；Amazon 北美分部含多种服务，不能描述为纯零售。

数据校验检查缺失、重复、身份、覆盖、金额、日期和 URL 基本格式。URL 校验不证明来源网页真实准确。报告起始日依年报年度日历推导，date_basis 已标注。

写入使用事务；相同记录不重复插入，变化记录更新，并使该分部旧派生指标失效。只建立指标结果表而未计算指标是 Module 02 的正常终态。

## 历史文件与原聊天

原聊天标题为“推荐零售业新旧公司对比”。本文件是项目上下文摘要，不是完整对话记录；原聊天仍保留在 Codex。侧边栏项目归属由应用设置决定，生成文件不会自动改变聊天所属项目。

模块目录、流程图、来源说明、原始下载包、修正说明及修改前备份都保留在本归集文件夹中。root 下最新总 Notebook 和 data/ 是当前学习入口；zip 包是之前的交付快照。

## Module 03 文件与重跑

完整总 Notebook 现在包含前三模块三十二格代码。module_03/guide.md 与 HTML 逐句解释所有非空代码行，共 149 条。metric_results 的 config_signature 实际是设置、所选源记录与 CALCULATION_VERSION 的组合签名。查询限定当前签名，重复运行原子替换本组；其他签名版本可保留。results/ 有 annual_metrics.csv、metric_records.csv、stage_summary.csv 与 analysis_manifest.json。

运行入口仍是项目根目录的总 Notebook，先运行前两模块定义。原桌面 Notebook 没有自动追加第三模块；可从 guide 复制，或直接使用更新后的项目总 Notebook。首年同比为 NULL，销售指数当前基期为 2019=100，公式百分比已经乘 100。展示舍入不覆盖计算值。


## Module 04 已完成（2026-10-11）

本次先检查用户 Desktop/JupyterProject 的实际 32 格前三模块 Notebook、真实 SQLite 与三个导出 CSV。保存输出无异常；隔离副本从头执行通过，独立 Decimal 公式核对通过，当前签名匹配。原文件未改。

完整项目总 Notebook 已增加 Module 04 十二格，共 44 格，在用户 .venv 的新 Jupyter kernel 运行通过。Module 04 名称为 Reporting and Workflow；简单 ReportBuilder 类保存 config 和目录，create_charts/write_report 是普通方法；读库、基期比较、格式化和报告正文使用普通函数。

report_metric_df 是当前签名 SQL 长表，report_df 是 12 x 22 的年度报告输入；expected_df 仅用于公式核对，所有展示指标值来自保存的 SQL。baseline_comparison_df 为 12 x 9，report_stage_df 为 6 x 12。读取连接 query_only，finally 关闭，报告过程中三张 SQL 表内容不变。

保存三个指标的 PNG/SVG 于 results/figures/；完整英文报告为 results/research_report.html，报告清单为 report_manifest.json。报告与 figures 一起分享。中文详细 guide 为 module_04/guide.md 和 module_04_code_explanation_guide.html，十二格、159 段解释，代码与文字分开排版。更新 study 配置和源数据后，按四模块顺序重跑；换研究时同步核对 Cell 03 的 REPORT_NOTES。

两份流程图已更新为四模块均实施，包含真实报告读库与保存步骤。README 和完整包以本次四模块状态为准；以前 ZIP 与独立模块的下一步说明是对应阶段的历史材料。模块总数仍是四个，不增加第五模块。
