# Retail Growth and Profitability Comparison

四个模块已完成。研究以 Amazon North America 与 Walmart U.S. 为例，正式分析 2019—2024 六年，以 2019 为疫情前参照及销售指数基期。采用免费官方分部年报数据，保留真实财年、日期、单位和来源；仅作描述性比较。

## 使用入口

打开根目录 retail_growth_and_profitability_comparison.ipynb，把 kernel 工作目录设为包含 study.json 的本文件夹。总 Notebook 包含全部四模块，共 44 个 code cells；第一行均为英文 comment 标题。顺序运行 Module 01→02→03→04，或从头 Run All。前三模块代码采用用户已成功运行的版本，第四模块新增十二格，均有独立中文详细解释。

你的原 Desktop/JupyterProject Notebook、配置、数据与结果在检查生成期间保留原样。可以把 Module 04 的十二格复制到原 Notebook 末尾；也可以解压完整项目包，在本文件夹使用四模块总 Notebook。不要只复制总 Notebook 而遗漏 data/raw/ 和 study.json。

依赖为 pandas 与 matplotlib。用户 .venv 已具备这两项，完整 Notebook 已在该环境的新 Jupyter kernel 中执行通过。全新 Jupyter 环境需要 pandas、matplotlib 和常规 Notebook kernel。

## Guides 与输出

module_01/guide.md：研究配置。module_02/module_02_code_explanation_guide.html：数据清洗与 SQLite，英文代码灰底、中文解释白底。module_03/module_03_code_explanation_guide.html：指标计算。module_04/module_04_code_explanation_guide.html：图表、报告与流程，十二格、159 段对照解释。每份 guide 保留完整可复制英文代码，说明变量、参数、执行顺序和构建理由。

results/research_report.html 是生成的完整英文报告。它包含三张图、年度指标、基期变化、阶段均值/有效年份数、方法、限制、报告期间和官方来源链接。HTML 依赖同级 figures/ 文件夹，分享时一起保留或发送完整 ZIP。三张图均另存 PNG 与 SVG。

results/annual_metrics.csv、metric_records.csv、stage_summary.csv、analysis_manifest.json 是第三模块输出；第四模块追加 research_report.html、report_manifest.json 与 figures/。报告清单包含输入签名、生成时间、配置快照和说明，读取当前 SQL 指标时核对数值版本。

## 数据与可复用范围

data/raw/ 保存经核对的转录原始 CSV；data/financial_data.csv 是组合导入快照；data/clean/financial_records.csv 是标准化审计表。data/retail_comparison.sqlite 包含 2 条分部资料、12 条财务记录、36 条本次指标，其中 2 条首年同比为 NULL。报告过程不更新数据库。

2019 同比缺失，2019 销售指数为 100，2022 Amazon 负利润率保留。销售累计变化是相对基期的百分比，利润率变化是百分点。阶段平均不等于 CAGR 或合并利润率，不能据此认定疫情因果效应。只有一个疫情前年份，财年配对近似，业务与地理范围也不同；金额为年报披露的名义 USD millions，未做通胀调整。

框架使用简单的 StudyConfig、DatabaseManager、MetricCalculator、ReportBuilder 与普通函数。更换研究需要替换配置、相应来源数据，并核对 Module 04 Cell 03 的研究说明。名称自动进入图和表，通用类不按公司名分支；全新指标则需增加计算和展示规则。不能只改名称后沿用旧公司的金额。

diagrams/ 的两份英文流程与数据管道图已标为四模块实施完成，展示具体 DataFrame、来源、工具和保存位置。project_plan.md、diagram_guide.md 与 PROJECT_CONTEXT.md 保存方法和工作背景。原来保留的 Module 01/02/03 ZIP 是历史交付快照；最新版本以本次四模块完整包为准。

## 检查与项目归属

module_04/modules_01_03_check.md 是对用户实际 Notebook 的检查，verification.txt 包含完整 44 格新 kernel 运行与错误输入验证。基础数值可追溯至 module_02/source_notes.md 中四份免费官方历史年报，完整官方 HTML 快照未附。

侧边栏项目归属由应用设置决定，生成文件不会自动移动聊天。若需要加入项目栏，在应用中添加本地项目并选择本文件夹。新聊天继续时读取 PROJECT_CONTEXT.md 与总 Notebook。

## PDF 导出

results/research_report.pdf 为当前 HTML 报告的 11 页 PDF 快照，保留三张图、四张结果/来源表和可点击的官方链接。宽表与图使用横向页面，来源审计表按分部分页。pdf_export_manifest.json 记录源 HTML 与 PDF 的 SHA256。Module 04 更新 HTML 后，PDF 需要重新导出；本次没有修改 Notebook 的计算代码。
