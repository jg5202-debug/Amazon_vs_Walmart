# Module 03 Metrics and Comparative Analysis

推荐打开项目根目录的完整总 Notebook，顺序运行 Module 01、Module 02、Module 03。本模块新增十二格，第一行均为英文 comment 标题。前两个模块无需改动。模块参考 Notebook 包含相同十二格与中文解释，需要同一 kernel 中已有前两模块定义，因此优先使用完整总 Notebook。

代码详解：module_03_code_explanation_guide.html，用浏览器打开；guide.md 为同样内容的 Markdown 版本。代码灰底等宽字体、中文说明白底，逐句标明对应行号，语法、参数、执行顺序和理由分开说明。

metrics_analysis.py 是通用规则、一个简单计算器类和普通函数的配套 Python 文件。总 Notebook 已包含这些定义，不需要额外导入它。唯一第三方依赖仍为 pandas。

Module 03 从 SQLite 查询十二条基础数据，再计算年度同比、营业利润率和配置基期销售指数。三十六条长结果保存在 metric_results，其中两条 2019 同比以 SQL NULL 保存。营业亏损对应负利润率保留。重复相同输入替换本研究本签名的结果，不产生重复行。其他签名版本可能仍在表中，全表数量可超过本次三十六。

results/annual_metrics.csv 为十二行二十二列；metric_records.csv 为三十六行九列的真实 SQL 回读；stage_summary.csv 为六行十二列的阶段均值及有效年份数。analysis_manifest.json 记录配置与数据签名、版本、时间、基期、单位约定和文件名。

当前基期为 2019。更换基期应在第一模块修改 index_base_year 并重新创建、保存配置，再完整重跑第三模块。当前研究首年依然无前一年同比。财务源文件改变时先重跑第二模块，再重跑第三模块，CSV 本身不自动更新数据库。

阶段均值是有效年度非加权算术平均，不是 CAGR、合并营业利润率或疫情因果效应。此模块不创建图表或最终报告，Module 04 会完成这些内容。来源与详细方法见 guide.md 末尾，验证记录见 verification.txt。

总 Notebook 与生成后的数据库放在完整包根目录对应位置。原桌面 Notebook 保留原样，可把新增十二格从本 guide 继续复制到原文件。
