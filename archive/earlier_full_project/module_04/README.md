# Module 04 Reporting and Workflow

新增十二格，接着前三模块在同一个总 Notebook 中顺序执行。根目录的总 Notebook 已包括全部四模块，共四十四个 code cells。独立参考 Notebook 的十二格内容相同，需要同一 kernel 已有前三模块定义。

module_04_code_explanation_guide.html：英文代码浅灰底，中文解释白底，逐段对应行号、语法与理由；guide.md 为完整 Markdown 版。reporting.py 是配套通用函数、展示设置和 ReportBuilder 类，不需要额外导入即可使用总 Notebook。作为 Python 模块导入时，应从完整项目根目录使用 module_04.reporting。

新增依赖 matplotlib，保留 pandas。当前用户环境已安装并验证；全新环境可按根目录 requirements.txt 安装。报告读取当前签名的 SQL 指标，查询连接开启 query_only，finally 关闭。图和 HTML/JSON 写磁盘，不修改数据库。

results/figures/：三张指标图各有 PNG 与 SVG。results/research_report.html：英文报告，包含数据结论、图、年度表、基期变化、阶段均值/有效年数、方法限制、期间审计和官方链接。results/report_manifest.json：版本、时间、配置快照、说明和输出文件清单。

分享 HTML 时带上 figures 子目录，或发送完整交付 ZIP。替换研究对象时要替换配置和原始数据，核对 Cell 03 的本研究说明；支持指标范围内的通用函数与类不按公司名称编写判断。累计销售变化不等于同比或 CAGR，利润率差为百分点，不作疫情因果推断。

modules_01_03_check.md 为这次用户 Notebook 的检查结果，verification.txt 为第四模块及完整运行验证。用户 Desktop 原文件保持不变，outputs 中提供新增模块与完整四模块版本。
