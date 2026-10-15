# Module 02 Code Explanation Guide

本 guide 逐句解释 Module 02 的实际 Python 与 SQL 代码。每格先展示完整英文代码，再按代码块的行号解释语法、执行结果以及为什么这样写。连续几行组成一条语句时一起解释，空行只用于排版；所有非空代码行均有对应说明。行号是本格内部的位置，不是 Notebook 的执行编号。

本版用于 Module 01 和 Module 02 放在同一个总 Notebook 的结构。先运行第一模块 Cell 01—08，让 load_study_config 已定义、study.json 已保存；第二模块 Cell 02 直接复用该函数。JSON 位于项目根目录，数据路径为 data/financial_data.csv、data/retail_comparison.sqlite 和 results。这里只改讲解与版式，不改英文研究代码，也不改你桌面上的 Notebook。

## 怎样阅读

完整代码用于复制到 Notebook。下面的说明编号对应完整代码的行号，按“语法和执行含义”“为什么这样写”阅读。代码旁的中文解释不应复制到 Python cell。配套 HTML 阅读版将代码与解释用不同字体和背景分开，提供代码行号、复制按钮和行号定位；浏览器打开即可使用，不需要联网。


## Cell 01: Import Libraries

### 完整代码

```python
# Cell 01: Import Libraries

import math
import re
import sqlite3
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import sys
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 01: Import Libraries`

**语法和执行含义：** 井号 # 后面是注释，Python 不把它作为操作执行。Cell 编号表示本模块中的格子编号，不是 Notebook 的执行次数。

**为什么这样写：** 便于复制和定位每一格；保留英文标题，代码内不混入中文说明。

---

**第 3 行｜导入数学模块**

对应语句：`import math`

**语法和执行含义：** import math 将 math 这个模块名称放入当前 kernel。后面 math.isfinite(amount) 通过点号取得其中的函数。

**为什么这样写：** 检查金额是否为有限数值；本行只导入工具，还没有检查金额。

---

**第 4 行｜导入正则表达式模块**

对应语句：`import re`

**语法和执行含义：** import re 导入用于匹配文本格式的模块。后面 re.fullmatch 检查整个金额字符串是否符合规定格式。

**为什么这样写：** 转换前识别不合法的文字，避免误把错误内容当成金额。

---

**第 5 行｜导入 SQLite 接口**

对应语句：`import sqlite3`

**语法和执行含义：** sqlite3 是 Python 标准库模块。后面用 sqlite3.connect 建立连接，再通过连接执行 SQL。

**为什么这样写：** 操作本地 SQLite 文件；导入这一行不会创建或连接数据库。

---

**第 6 行｜只导入 Path 名称**

对应语句：`from pathlib import Path`

**语法和执行含义：** from pathlib import Path 从 pathlib 模块取出 Path，后面直接写 Path(...)，不用写 pathlib.Path(...)。

**为什么这样写：** 用专门的路径对象处理目录和文件，减少手工拼接路径字符串。

---

**第 7 行｜只导入网址解析函数**

对应语句：`from urllib.parse import urlparse`

**语法和执行含义：** 从 urllib.parse 导入 urlparse；它将网址拆成协议、网络地址、路径等部分。

**为什么这样写：** 后面检查来源 URL 的基本格式；这不是网页下载函数。

---

**第 9 行｜给 pandas 起别名**

对应语句：`import pandas as pd`

**语法和执行含义：** import pandas as pd 导入 pandas，并以 pd 作为本 Notebook 中的简称。

**为什么这样写：** 后面写 pd.read_csv、pd.concat 和 pd.to_numeric，减少重复书写。

---

**第 10 行｜当前没有使用的导入**

对应语句：`import sys`

**语法和执行含义：** sys 是 Python 运行环境模块。原独立 Notebook 版本使用 sys.path 寻找配套文件；当前总 Notebook 版本已经直接复用第一模块函数，因此没有使用它。

**为什么这样写：** 保留本行不影响执行；也可以删去本行，不必因为编辑器显示灰色就认为运行失败。

---

## Cell 02: Load Study Configuration and Set Input Paths

### 完整代码

```python
# Cell 02: Load Study Configuration and Set Input Paths

CONFIG_PATH = Path.cwd() / "study.json"

config = load_study_config(CONFIG_PATH)
paths = config.resolve_paths(CONFIG_PATH)
DATA_FILE = paths["data_file"]
DATABASE_FILE = paths["database_file"]
RAW_DIRECTORY = DATA_FILE.parent / "raw"
CLEAN_FILE = DATA_FILE.parent / "clean" / "financial_records.csv"

RAW_FILES = {
    "amazon_north_america": RAW_DIRECTORY / "amazon_segment_raw.csv",
    "walmart_us": RAW_DIRECTORY / "walmart_segment_raw.csv",
}

print(f"Working directory: {Path.cwd()}")
print(f"Configuration: {CONFIG_PATH}")
print(f"Planned records: {config.get_observation_count()}")
print(f"Index base year: {config.index_base_year}")
print(f"Database: {DATABASE_FILE}")
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 02: Load Study Configuration and Set Input Paths`

**语法和执行含义：** 井号 # 后面是注释，Python 不把它作为操作执行。Cell 编号表示本模块中的格子编号，不是 Notebook 的执行次数。

**为什么这样写：** 便于复制和定位每一格；保留英文标题，代码内不混入中文说明。

---

**第 3 行｜取得配置文件位置**

对应语句：`CONFIG_PATH = Path.cwd() / "study.json"`

**语法和执行含义：** 先执行 Path.cwd()，取得 kernel 的当前工作目录；Path 对象的 / 运算拼上 study.json；最后将结果赋给 CONFIG_PATH。

**为什么这样写：** 你的 JSON 放在项目根目录，因此以当前项目目录作为入口。这里没有打开文件，也不会自动推算 Notebook 的存放位置。

---

**第 5 行｜调用配置读取函数**

对应语句：`config = load_study_config(CONFIG_PATH)`

**语法和执行含义：** 右边先调用第一模块定义的 load_study_config(CONFIG_PATH)，读取 JSON、创建并检查 StudyConfig；左边 config 接收返回的对象。

**为什么这样写：** 复用同一套配置规则。先运行第一模块的定义与保存格，否则函数名称可能不存在或 JSON 尚未保存。

---

**第 6 行｜通过对象方法解析三个路径**

对应语句：`paths = config.resolve_paths(CONFIG_PATH)`

**语法和执行含义：** config.resolve_paths(CONFIG_PATH) 使用 JSON 所在目录作为基准，返回含 data_file、database_file、results_directory 的字典，保存到 paths。

**为什么这样写：** 数据路径依赖配置内容，不散落在清洗或 SQL 函数里。这一步也不创建文件。

---

**第 7 行｜取出组合快照路径**

对应语句：`DATA_FILE = paths["data_file"]`

**语法和执行含义：** paths["data_file"] 用字典键取得 Path 值，赋给 DATA_FILE。它对应之后导出的 financial_data.csv。

**为什么这样写：** DATA_FILE 是组合快照的保存位置；实际输入仍是 raw/ 中的两个源 CSV，不要把它误认成读取入口。

---

**第 8 行｜取出数据库路径**

对应语句：`DATABASE_FILE = paths["database_file"]`

**语法和执行含义：** 通过 database_file 键取得 SQLite 文件位置，赋给 DATABASE_FILE。

**为什么这样写：** 让数据库类使用配置指定的文件，换保存位置时不需要修改类的方法。

---

**第 9 行｜从数据目录得到 raw 目录**

对应语句：`RAW_DIRECTORY = DATA_FILE.parent / "raw"`

**语法和执行含义：** DATA_FILE.parent 取得 financial_data.csv 所在的 data 文件夹，再 / "raw" 得到原始输入目录。

**为什么这样写：** 原始输入与导出采用同一数据根目录，避免分别写两个可能不一致的位置。

---

**第 10 行｜确定清洗核对文件**

对应语句：`CLEAN_FILE = DATA_FILE.parent / "clean" / "financial_records.csv"`

**语法和执行含义：** 先取得 data 文件夹，再依次拼上 clean 文件夹与 financial_records.csv 文件名。

**为什么这样写：** 原始组合快照和清洗结果分开存，便于审查；这一行只准备路径。

---

**第 12—15 行｜建立标识到源文件的映射**

对应语句：`RAW_FILES = { ⏐ "amazon_north_america": RAW_DIRECTORY / "amazon_segment_raw.csv", ⏐ "walmart_us": RAW_DIRECTORY / "walmart_segment_raw.csv", ⏐ }`

**语法和执行含义：** 花括号创建字典。第 13 行的键是 Amazon 分部标识，值是其 CSV 路径；第 14 行对 Walmart 做同样安排；第 15 行结束字典。

**为什么这样写：** 后面循环按标识读取对应文件。换内容时调整配置、真实输入与这份映射，通用清洗函数不判断公司名称。

---

**第 17 行｜打印当前工作目录**

对应语句：`print(f"Working directory: {Path.cwd()}")`

**语法和执行含义：** f-string 把花括号中的 Path.cwd() 结果嵌入显示文字，再由 print 输出。

**为什么这样写：** 确认 kernel 的实际目录。相对路径从这里出发，不一定从 Notebook 文件所在位置出发。

---

**第 18 行｜打印实际配置位置**

对应语句：`print(f"Configuration: {CONFIG_PATH}")`

**语法和执行含义：** 将 CONFIG_PATH 的值嵌入输出文字。

**为什么这样写：** 确认读的是项目中的那份 JSON，避免误用另一处同名文件。

---

**第 19 行｜调用方法显示计划数量**

对应语句：`print(f"Planned records: {config.get_observation_count()}")`

**语法和执行含义：** config.get_observation_count() 根据分部数和时期数得到计划数量，本案例为 12；print 只是显示它。

**为什么这样写：** 这里尚未读入实际财务记录，计划数量与实际数量要在后面分别核对。

---

**第 20 行｜显示对象保存的基期**

对应语句：`print(f"Index base year: {config.index_base_year}")`

**语法和执行含义：** config.index_base_year 通过点号访问对象属性；这里读取配置里的 2019。

**为什么这样写：** 核对基期设置；这一行没有计算销售指数。

---

**第 21 行｜显示数据库目标位置**

对应语句：`print(f"Database: {DATABASE_FILE}")`

**语法和执行含义：** 将 DATABASE_FILE 嵌入显示文字。

**为什么这样写：** 确认数据库将在项目内部 data/ 中创建；看到路径不代表文件已创建。

---

## Cell 03: Define Cleaning Functions

### 完整代码

```python
# Cell 03: Define Cleaning Functions

RAW_COLUMNS = [
    "unit_id", "company_name", "segment_name", "fiscal_year",
    "period_start", "period_end", "net_sales_raw", "operating_income_raw",
    "reported_currency", "reported_unit", "source_url", "source_section",
    "accessed_date", "date_basis",
]

UNIT_MULTIPLIERS = {"units": 0.000001, "millions": 1.0, "billions": 1000.0}

RECORD_COLUMNS = [
    "unit_id", "fiscal_year", "period_start", "period_end",
    "net_sales_raw", "operating_income_raw", "reported_currency",
    "reported_unit", "source_url", "source_section", "accessed_date",
    "date_basis", "net_sales_usd_m", "operating_income_usd_m",
]


def parse_amount(value):
    """Convert a reported amount string without treating missing data as zero."""
    text = str(value).strip().replace(",", "")
    if text.startswith("(") and text.endswith(")"):
        text = "-" + text[1:-1]
    if re.fullmatch(r"-?\d+(\.\d+)?", text) is None:
        raise ValueError(f"Invalid reported amount: {value}")
    amount = float(pd.to_numeric(text, errors="raise"))
    if not math.isfinite(amount):
        raise ValueError(f"Reported amount must be finite: {value}")
    return amount


def standardize_records(raw_df):
    """Preserve source strings and add numeric amounts in USD millions."""
    for column in RAW_COLUMNS:
        if column not in raw_df.columns:
            raise ValueError(f"Missing raw column: {column}")

    clean_df = raw_df[RAW_COLUMNS].copy()
    for column in RAW_COLUMNS:
        if clean_df[column].isna().any():
            raise ValueError(f"Missing value in column: {column}")
        clean_df[column] = clean_df[column].astype(str).str.strip()
        if clean_df[column].eq("").any():
            raise ValueError(f"Blank value in column: {column}")

    years = pd.to_numeric(clean_df["fiscal_year"], errors="raise")
    if not years.between(1900, 2100).all() or not years.eq(years.round()).all():
        raise ValueError("Fiscal years must be integer years between 1900 and 2100.")
    clean_df["fiscal_year"] = years.astype(int)

    for column in ["period_start", "period_end", "accessed_date"]:
        dates = pd.to_datetime(clean_df[column], format="%Y-%m-%d", errors="raise")
        clean_df[column] = dates.dt.strftime("%Y-%m-%d")

    sales_values = []
    income_values = []
    for row in clean_df.to_dict("records"):
        if row["reported_currency"] != "USD":
            raise ValueError("This version supports USD records only; it does not convert currencies.")
        if row["reported_unit"] not in UNIT_MULTIPLIERS:
            raise ValueError(f"Unsupported reported unit: {row['reported_unit']}")
        multiplier = UNIT_MULTIPLIERS[row["reported_unit"]]
        sales_values.append(parse_amount(row["net_sales_raw"]) * multiplier)
        income_values.append(parse_amount(row["operating_income_raw"]) * multiplier)

    clean_df["net_sales_usd_m"] = sales_values
    clean_df["operating_income_usd_m"] = income_values
    return clean_df.sort_values(["unit_id", "fiscal_year"]).reset_index(drop=True)
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 03: Define Cleaning Functions`

**语法和执行含义：** 井号 # 后面是注释，Python 不把它作为操作执行。Cell 编号表示本模块中的格子编号，不是 Notebook 的执行次数。

**为什么这样写：** 便于复制和定位每一格；保留英文标题，代码内不混入中文说明。

---

**第 3—8 行｜规定原始表的十四列**

对应语句：`RAW_COLUMNS = [ ⏐ "unit_id", "company_name", "segment_name", "fiscal_year", ⏐ "period_start", "period_end", "net_sales_raw", "operating_income_raw", ⏐ "reported_currency", "reported_unit", "source_url", "source_section", ⏐ "accessed_date", "date_basis", ⏐ ]`

**语法和执行含义：** 方括号建立有顺序的列名列表。第 4 行是分部身份和财年；第 5 行是期间和原始金额；第 6 行是币种、单位、URL 与章节；第 7 行是访问日与日期依据；第 8 行结束列表。

**为什么这样写：** 定义清洗函数的输入接口。raw_df 必须具备这些字段，多余列不会自动进入本次标准输出。

---

**第 10 行｜规定单位换算乘数**

对应语句：`UNIT_MULTIPLIERS = {"units": 0.000001, "millions": 1.0, "billions": 1000.0}`

**语法和执行含义：** 字典以 units、millions、billions 查询乘数。整美元乘 0.000001、百万美元乘 1、十亿美元乘 1000，结果统一为百万美元。

**为什么这样写：** 统一金额数量级；这不是汇率换算，本版本只支持 USD。

---

**第 12—17 行｜规定数据库财务字段的顺序**

对应语句：`RECORD_COLUMNS = [ ⏐ "unit_id", "fiscal_year", "period_start", "period_end", ⏐ "net_sales_raw", "operating_income_raw", "reported_currency", ⏐ "reported_unit", "source_url", "source_section", "accessed_date", ⏐ "date_basis", "net_sales_usd_m", "operating_income_usd_m", ⏐ ]`

**语法和执行含义：** 此列表含十四个要存入 financial_records 的字段：前两个是联合主键，后十二个是期间、原始披露、来源和标准金额。名称字段改放 business_units，查询时再取回。

**为什么这样写：** 后面 SELECT、INSERT、UPDATE 以及参数元组都依赖这份固定顺序；它与 RAW_COLUMNS 的内容不同。

---

**第 20—21 行｜定义单个金额解析函数**

对应语句：`def parse_amount(value): ⏐ """Convert a reported amount string without treating missing data as zero."""`

**语法和执行含义：** def 定义普通函数 parse_amount，value 接收一次传入的金额；三引号是函数说明字符串。这里只保存函数定义，函数体在被调用时才执行。

**为什么这样写：** 将金额解析独立出来，两种金额列与其他同格式记录都可复用。返回值是一个普通浮点数。

---

**第 22 行｜连续处理原始字符串**

对应语句：`text = str(value).strip().replace(",", "")`

**语法和执行含义：** 从内向外依次执行 str(value)、strip()、replace(",", "")：先转成文本，去两端空白，再删除千位逗号，结果赋给 text。

**为什么这样写：** 例如 " (2,847) " 得到 "(2847)"。处理局部变量，不覆盖 DataFrame 的原始金额列。

---

**第 23 行｜检查成对亏损括号**

对应语句：`if text.startswith("(") and text.endswith(")"):`

**语法和执行含义：** startswith 判断开头是否为左括号，endswith 判断结尾是否为右括号，and 要求两个条件都为真。

**为什么这样写：** 只有左右括号同时存在，才按财报括号亏损规则处理。

---

**第 24 行｜把括号金额变成负数文本**

对应语句：`text = "-" + text[1:-1]`

**语法和执行含义：** text[1:-1] 取索引 1 到最后字符之前的内容，去掉最外层括号；前面拼上 "-"，再赋回 text。

**为什么这样写：** "(2847)" 变为 "-2847"。这里仍是字符串，下一步才转成数值。

---

**第 25 行｜检查整段金额格式**

对应语句：`if re.fullmatch(r"-?\d+(\.\d+)?", text) is None:`

**语法和执行含义：** re.fullmatch 要求整个 text 匹配。r 是原始字符串；-? 是可选负号；\d+ 是至少一个数字；\. 是字面小数点；(\.\d+)? 表示小数部分可有可无。失败返回 None，is None 检查失败。

**为什么这样写：** 允许本项目采用的普通整数或小数文本。货币符号、文字、科学记数法等不属于这个函数支持的格式。

---

**第 26 行｜拒绝无法解释的金额**

对应语句：`raise ValueError(f"Invalid reported amount: {value}")`

**语法和执行含义：** raise ValueError 主动抛出错误；f-string 将原 value 放进提示。没有捕获异常时，本次函数和当前 cell 停止。

**为什么这样写：** 暴露坏输入供你修正，避免把空白或文字当成零。

---

**第 27 行｜转换为普通浮点数**

对应语句：`amount = float(pd.to_numeric(text, errors="raise"))`

**语法和执行含义：** 先调用 pd.to_numeric(text, errors="raise") 将文本解释为数值，失败报错；再 float(...) 统一为普通浮点数，赋给 amount。

**为什么这样写：** "-2847" 得到 -2847.0，之后可做单位换算与指标计算。

---

**第 28—29 行｜拒绝非有限结果**

对应语句：`if not math.isfinite(amount): ⏐ raise ValueError(f"Reported amount must be finite: {value}")`

**语法和执行含义：** math.isfinite(amount) 对有限数返回 True；not 反转判断。若为 NaN 或无穷大，第 29 行抛出包含原输入的错误。

**为什么这样写：** 有限的负数是合法金额；无穷大等结果不能作为可靠财务数据。

---

**第 30 行｜将解析结果交给调用者**

对应语句：`return amount`

**语法和执行含义：** return amount 结束本次函数调用，并把 amount 的值交回调用位置。

**为什么这样写：** 后面 append(parse_amount(...) * multiplier) 才能取得这个金额；不写 return 会默认得到 None。

---

**第 33—34 行｜定义整张表标准化函数**

对应语句：`def standardize_records(raw_df): ⏐ """Preserve source strings and add numeric amounts in USD millions."""`

**语法和执行含义：** raw_df 是输入 DataFrame，说明字符串描述保留源文本并新增标准金额。def 结束后函数可调用，但本格尚未实际清洗。

**为什么这样写：** 将单值解析与整表处理分开。此函数返回新的 clean_df，调用时需要接收返回值。

---

**第 35—37 行｜先确认列齐全**

对应语句：`for column in RAW_COLUMNS: ⏐ if column not in raw_df.columns: ⏐ raise ValueError(f"Missing raw column: {column}")`

**语法和执行含义：** for 逐个取得 RAW_COLUMNS 的列名；not in raw_df.columns 检查是否缺列；有缺失则 raise，并将列名写入提示。

**为什么这样写：** 先确认字段可访问，再转换数据，避免在中途遇到不明确的 KeyError。

---

**第 39 行｜选择列并复制表**

对应语句：`clean_df = raw_df[RAW_COLUMNS].copy()`

**语法和执行含义：** raw_df[RAW_COLUMNS] 按列表选择并排列列；copy() 创建独立的 DataFrame，赋给 clean_df。

**为什么这样写：** 后面可以修改 clean_df，同时保留 raw_df 用于原始快照。

---

**第 40—42 行｜检查真正的缺失值**

对应语句：`for column in RAW_COLUMNS: ⏐ if clean_df[column].isna().any(): ⏐ raise ValueError(f"Missing value in column: {column}")`

**语法和执行含义：** for 逐列检查。isna() 为各行产生布尔值，any() 判断是否至少一行缺失；若为真，raise 提示对应列。

**为什么这样写：** 在转成字符串前拒绝缺失，避免 NaN 或 None 被转换成看似非空的文字。

---

**第 43 行｜统一文本并去空格**

对应语句：`clean_df[column] = clean_df[column].astype(str).str.strip()`

**语法和执行含义：** astype(str) 转换整列的值，.str.strip() 对每个字符串去两端空白，再将结果保存回同名列。

**为什么这样写：** 清理录入的外围空格，保证名称、币种和后面空文本检查一致。

---

**第 44—45 行｜检查空文本**

对应语句：`if clean_df[column].eq("").any(): ⏐ raise ValueError(f"Blank value in column: {column}")`

**语法和执行含义：** eq("") 逐行比较是否为空字符串，any() 要求只要有一个就触发 raise。

**为什么这样写：** 只有空格的输入经过 strip 会变为空字符串；它与真正缺失值需要分别检查。

---

**第 47 行｜将财年列解释为数字**

对应语句：`years = pd.to_numeric(clean_df["fiscal_year"], errors="raise")`

**语法和执行含义：** 这里 to_numeric 接收一整列，返回数值 Series；errors="raise" 让无法转换的年份报错，结果赋给 years。

**为什么这样写：** 整列数值便于检查范围和是否为整数，不直接截断不合法输入。

---

**第 48—49 行｜检查每个年份都合理且为整数**

对应语句：`if not years.between(1900, 2100).all() or not years.eq(years.round()).all(): ⏐ raise ValueError("Fiscal years must be integer years between 1900 and 2100.")`

**语法和执行含义：** between 检查范围，再 all() 要求每行满足；round 得到舍入值，eq 检查原值是否等于舍入值，再 all()。or 表示任意一项失败就 raise。

**为什么这样写：** 2019.5 不等于它的舍入值，因而先拒绝。all 是所有行，any 是至少一行，不能互换。

---

**第 50 行｜保存整数财年**

对应语句：`clean_df["fiscal_year"] = years.astype(int)`

**语法和执行含义：** years.astype(int) 将已检查的财年转成整数，再保存回 clean_df 的 fiscal_year 列。

**为什么这样写：** 后面联合键、年份比较和 SQLite INTEGER 字段使用整数；检查通过后转换才不会掩盖小数年份。

---

**第 52 行｜依次处理三列日期**

对应语句：`for column in ["period_start", "period_end", "accessed_date"]:`

**语法和执行含义：** for column 从三个列名中逐个取值，同样处理开始日、结束日和访问日。

**为什么这样写：** 共用一段日期转换代码，不重复写三个几乎相同的处理。

---

**第 53 行｜解释为有效日期**

对应语句：`dates = pd.to_datetime(clean_df[column], format="%Y-%m-%d", errors="raise")`

**语法和执行含义：** pd.to_datetime 接收该列，按年-月-日格式解析为日期 Series；%Y、%m、%d 分别表示年、月、日。错误输入会报错。

**为什么这样写：** 先确认日期可以解释，再统一保存格式，避免无效日期进入数据库。

---

**第 54 行｜将日期统一输出为文本**

对应语句：`clean_df[column] = dates.dt.strftime("%Y-%m-%d")`

**语法和执行含义：** dates.dt 是访问整列日期属性的入口；strftime 将每个日期格式化成 YYYY-MM-DD，结果覆盖原列。

**为什么这样写：** 有效且统一的这种格式可按日期先后比较，也便于 CSV 与 SQLite TEXT 保存。

---

**第 56—57 行｜准备两份金额结果列表**

对应语句：`sales_values = [] ⏐ income_values = []`

**语法和执行含义：** [] 创建空列表；sales_values 保存净销售额结果，income_values 保存营业利润结果。

**为什么这样写：** 逐行解析后 append 到对应列表，最后作为完整新列写回。

---

**第 58 行｜把表转成行字典并逐行处理**

对应语句：`for row in clean_df.to_dict("records"):`

**语法和执行含义：** to_dict("records") 返回字典组成的列表，每个字典是一行，for 每轮让 row 指向一行。

**为什么这样写：** 用 row["列名"] 访问不同字段，容易看清一条记录怎样被处理。

---

**第 59—60 行｜只接受 USD**

对应语句：`if row["reported_currency"] != "USD": ⏐ raise ValueError("This version supports USD records only; it does not convert currencies.")`

**语法和执行含义：** 比较 reported_currency 与 "USD"，不相等则 raise。

**为什么这样写：** 当前版本没有汇率转换；明确拒绝其他币种，避免把不同货币误当作美元。

---

**第 61—62 行｜先确认单位可查询**

对应语句：`if row["reported_unit"] not in UNIT_MULTIPLIERS: ⏐ raise ValueError(f"Unsupported reported unit: {row['reported_unit']}")`

**语法和执行含义：** not in UNIT_MULTIPLIERS 检查单位是否为该字典的一个键；未知单位会报错并显示原单位。

**为什么这样写：** 下一行要查乘数，先确认支持范围，不能凭猜测转换金额。

---

**第 63 行｜根据单位取得乘数**

对应语句：`multiplier = UNIT_MULTIPLIERS[row["reported_unit"]]`

**语法和执行含义：** 嵌套方括号先取 row 的 reported_unit，再以它为键查询 UNIT_MULTIPLIERS。结果保存到 multiplier。

**为什么这样写：** 把研究数据的单位文字连接到通用换算规则。

---

**第 64 行｜解析并换算销售额**

对应语句：`sales_values.append(parse_amount(row["net_sales_raw"]) * multiplier)`

**语法和执行含义：** 先 parse_amount 取得原始销售额的数值，乘 multiplier 得到百万美元，再 append 加到 sales_values 最后。

**为什么这样写：** 每轮添加一个结果，保持与 clean_df 行顺序相同。

---

**第 65 行｜解析并换算营业利润**

对应语句：`income_values.append(parse_amount(row["operating_income_raw"]) * multiplier)`

**语法和执行含义：** 对 operating_income_raw 执行同样处理，加到 income_values。

**为什么这样写：** 复用同一个解析函数，亏损的负号不会被删掉，两项金额的规则保持一致。

---

**第 67—68 行｜把结果列表写成两列**

对应语句：`clean_df["net_sales_usd_m"] = sales_values ⏐ clean_df["operating_income_usd_m"] = income_values`

**语法和执行含义：** 方括号指定列名，右边的列表按行赋值；列不存在时新增列。两列分别存百万美元销售额与营业利润。

**为什么这样写：** 原十四列仍在，加两列后成为十六列，同时保留证据文本与可计算数值。

---

**第 69 行｜排序并返回标准表**

对应语句：`return clean_df.sort_values(["unit_id", "fiscal_year"]).reset_index(drop=True)`

**语法和执行含义：** sort_values 先按分部、再按财年排序；reset_index(drop=True) 重新编号且不保留旧索引列；return 交回结果。

**为什么这样写：** 形成稳定顺序，方便显示与后面的逐字段回读比较。

---

## Cell 04: Define Record Validation

### 完整代码

```python
# Cell 04: Define Record Validation

def validate_records(clean_df, config):
    """Require exact configured coverage, correct identities and usable values."""
    if config.currency != "USD":
        raise ValueError("The configuration must use USD for this version.")
    if clean_df.duplicated(["unit_id", "fiscal_year"]).any():
        raise ValueError("Duplicate segment/fiscal-year records were found.")

    expected_keys = set()
    units_by_id = {}
    for unit in config.business_units:
        units_by_id[unit["unit_id"]] = unit
    for period in config.periods:
        for unit_id in units_by_id:
            expected_keys.add((unit_id, period["fiscal_years"][unit_id]))

    actual_keys = set()
    for row in clean_df.to_dict("records"):
        key = (row["unit_id"], row["fiscal_year"])
        actual_keys.add(key)
        if row["unit_id"] not in units_by_id:
            raise ValueError(f"Unexpected business unit: {row['unit_id']}")
        unit = units_by_id[row["unit_id"]]
        if row["company_name"] != unit["company_name"] or row["segment_name"] != unit["segment_name"]:
            raise ValueError(f"Company or segment name does not match configuration: {key}")
        if row["reported_currency"] != config.currency:
            raise ValueError(f"Currency does not match configuration: {key}")
        if row["period_start"] >= row["period_end"]:
            raise ValueError(f"Report start must be before report end: {key}")
        for column in ["net_sales_usd_m", "operating_income_usd_m"]:
            if not math.isfinite(float(row[column])):
                raise ValueError(f"Non-finite financial value in {column}: {key}")
        if row["net_sales_usd_m"] <= 0:
            raise ValueError(f"Net sales must be positive: {key}")
        source = urlparse(row["source_url"])
        if source.scheme not in ["http", "https"] or not source.netloc:
            raise ValueError(f"Invalid source URL: {key}")
        for column in ["source_section", "date_basis", "accessed_date"]:
            if not str(row[column]).strip():
                raise ValueError(f"Missing provenance in {column}: {key}")

    if actual_keys != expected_keys:
        missing = sorted(expected_keys - actual_keys)
        extra = sorted(actual_keys - expected_keys)
        raise ValueError(f"Coverage mismatch. Missing: {missing}; extra: {extra}")
    if len(clean_df) != config.get_observation_count():
        raise ValueError("Record count does not match the configured study.")
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 04: Define Record Validation`

**语法和执行含义：** 井号 # 后面是注释，Python 不把它作为操作执行。Cell 编号表示本模块中的格子编号，不是 Notebook 的执行次数。

**为什么这样写：** 便于复制和定位每一格；保留英文标题，代码内不混入中文说明。

---

**第 3—4 行｜定义只做检查的函数**

对应语句：`def validate_records(clean_df, config): ⏐ """Require exact configured coverage, correct identities and usable values."""`

**语法和执行含义：** 两个参数分别是实际标准数据 clean_df 与研究要求 config。函数通过时没有显式 return，默认返回 None；失败时抛出异常。

**为什么这样写：** 检查数据不必产生一张新表，因此调用时不把返回值赋给 clean_df。

---

**第 5—6 行｜检查研究配置币种**

对应语句：`if config.currency != "USD": ⏐ raise ValueError("The configuration must use USD for this version.")`

**语法和执行含义：** 访问 config.currency 属性并与 USD 比较，不同则 raise。

**为什么这样写：** 除了逐行币种检查，也确认本版研究整体满足 USD 接口。

---

**第 7—8 行｜按联合身份查重复**

对应语句：`if clean_df.duplicated(["unit_id", "fiscal_year"]).any(): ⏐ raise ValueError("Duplicate segment/fiscal-year records were found.")`

**语法和执行含义：** duplicated 指定 unit_id 和 fiscal_year 两列作为组合，返回重复标记；any 发现至少一个重复则 raise。

**为什么这样写：** 相同分部财年只能有一条，重复来源需要先核对，不能悄悄删除。

---

**第 10 行｜准备应该出现的身份集合**

对应语句：`expected_keys = set()`

**语法和执行含义：** set() 创建空集合 expected_keys，保存之后配置要求的元组。

**为什么这样写：** 集合用于比较覆盖，自动去重且不依赖输入行顺序。

---

**第 11 行｜准备分部查询字典**

对应语句：`units_by_id = {}`

**语法和执行含义：** {} 创建空字典 units_by_id；空字典与空集合的写法不同。

**为什么这样写：** 用稳定标识直接查对应分部配置。

---

**第 12—13 行｜按标识保存完整分部配置**

对应语句：`for unit in config.business_units: ⏐ units_by_id[unit["unit_id"]] = unit`

**语法和执行含义：** for 每次取得一个 unit 字典；unit["unit_id"] 是键，右侧 unit 是保存的完整配置值。

**为什么这样写：** 后面看到一条数据的标识就可取得正确名称和分部，无需反复搜索列表。

---

**第 14—16 行｜生成每期应有的分部财年组合**

对应语句：`for period in config.periods: ⏐ for unit_id in units_by_id: ⏐ expected_keys.add((unit_id, period["fiscal_years"][unit_id]))`

**语法和执行含义：** 外层遍历时期，内层遍历 units_by_id 的键；period["fiscal_years"][unit_id] 取得该分部在该期的报告财年；组成元组并 add 到集合。

**为什么这样写：** 分析年度 2019 对应 Amazon 2019、Walmart 2020。用映射生成十二个身份，没有写死公司特例。

---

**第 18 行｜准备实际身份集合**

对应语句：`actual_keys = set()`

**语法和执行含义：** 创建 actual_keys 空集合，等实际数据循环逐项加入。

**为什么这样写：** 最终与 expected_keys 比较，发现缺年、多年或错误配对。

---

**第 19 行｜逐条检查实际表**

对应语句：`for row in clean_df.to_dict("records"):`

**语法和执行含义：** to_dict("records") 将每行变成字典；for 每轮取得一行 row。

**为什么这样写：** 一条数据有多个字段检查，使用明确的列名访问。

---

**第 20 行｜组合当前记录身份**

对应语句：`key = (row["unit_id"], row["fiscal_year"])`

**语法和执行含义：** 以 row 的分部标识与财年创建二元素元组 key。

**为什么这样写：** 既用于覆盖检查，也放在错误提示中定位问题。

---

**第 21 行｜把身份加入实际名单**

对应语句：`actual_keys.add(key)`

**语法和执行含义：** actual_keys.add(key) 加入当前元组，重复元组在集合中仍只保留一份。

**为什么这样写：** 集合用于名单比较，重复检查已经在函数前面单独进行。

---

**第 22—23 行｜拒绝研究以外的分部**

对应语句：`if row["unit_id"] not in units_by_id: ⏐ raise ValueError(f"Unexpected business unit: {row['unit_id']}")`

**语法和执行含义：** not in 对字典查询键；当前标识不存在时抛出错误并显示该标识。

**为什么这样写：** 防止混入 AWS、其他地域或未配置公司，且保证下一行查字典安全。

---

**第 24 行｜取出正确分部配置**

对应语句：`unit = units_by_id[row["unit_id"]]`

**语法和执行含义：** 先取当前行 unit_id，再查询 units_by_id，把完整配置赋给局部变量 unit。

**为什么这样写：** 实际记录的名称与配置的名称接下来需要一一比较。

---

**第 25—26 行｜核对两个名称**

对应语句：`if row["company_name"] != unit["company_name"] or row["segment_name"] != unit["segment_name"]: ⏐ raise ValueError(f"Company or segment name does not match configuration: {key}")`

**语法和执行含义：** 两个 != 判断不一致，or 表示任意一项不一致就失败；raise 用 key 定位问题。字符串比较精确匹配大小写与拼写。

**为什么这样写：** 发现标识写对、公司或分部名字却录错的记录。

---

**第 27—28 行｜核对记录币种**

对应语句：`if row["reported_currency"] != config.currency: ⏐ raise ValueError(f"Currency does not match configuration: {key}")`

**语法和执行含义：** 比较 row 中的 reported_currency 与 config.currency，不同就报错。

**为什么这样写：** 实际记录与整个研究的货币口径必须一致，此处不做汇率换算。

---

**第 29—30 行｜核对日期先后**

对应语句：`if row["period_start"] >= row["period_end"]: ⏐ raise ValueError(f"Report start must be before report end: {key}")`

**语法和执行含义：** >= 表示晚于或等于。开始日期这样比较到结束日期时，要求条件为假，否则 raise。

**为什么这样写：** 报告开始必须严格早于结束；依赖标准化已将有效日期统一为 ISO 文本。

---

**第 31—33 行｜核对两个金额的有限性**

对应语句：`for column in ["net_sales_usd_m", "operating_income_usd_m"]: ⏐ if not math.isfinite(float(row[column])): ⏐ raise ValueError(f"Non-finite financial value in {column}: {key}")`

**语法和执行含义：** 小循环分别取两个金额列；float 转成普通数值，再 isfinite 检查，not 让非有限值触发 raise。

**为什么这样写：** 保护后续计算；正常负营业利润仍是有限数，可通过。

---

**第 34—35 行｜要求销售额为正**

对应语句：`if row["net_sales_usd_m"] <= 0: ⏐ raise ValueError(f"Net sales must be positive: {key}")`

**语法和执行含义：** <= 0 检查零或负销售额，并拒绝这种输入。

**为什么这样写：** 净销售额会作为指标分母或指数基准；营业利润没有这个正数限制。

---

**第 36 行｜拆分来源网址**

对应语句：`source = urlparse(row["source_url"])`

**语法和执行含义：** urlparse 返回解析结果对象，保存到 source，之后通过点号访问其中的组成部分。

**为什么这样写：** 检查基本结构，无需在小样本导入过程中联网抓取。

---

**第 37—38 行｜检查协议和地址部分**

对应语句：`if source.scheme not in ["http", "https"] or not source.netloc: ⏐ raise ValueError(f"Invalid source URL: {key}")`

**语法和执行含义：** scheme 要属于 http/https；not source.netloc 表示网络地址为空；任意条件失败则 raise。

**为什么这样写：** 发现明显无效的来源地址。它不证明网页可访问，也不核对网页中的金额。

---

**第 39—41 行｜拒绝空的追溯信息**

对应语句：`for column in ["source_section", "date_basis", "accessed_date"]: ⏐ if not str(row[column]).strip(): ⏐ raise ValueError(f"Missing provenance in {column}: {key}")`

**语法和执行含义：** 循环取章节、日期依据和访问日；str 转文本，strip 去空白，not 把空文本视为缺失，再 raise。

**为什么这样写：** 有数字也要可追溯。前面的标准化已拒绝真正缺失值，否则单靠 str(None) 这种检查不充分。

---

**第 43 行｜所有行结束后比较名单**

对应语句：`if actual_keys != expected_keys:`

**语法和执行含义：** 集合 != 检查是否有成员不同。这行缩进退回实际行循环外，等全部行检查完才判断。

**为什么这样写：** 若放在逐行循环里，第一行结束就会误报其他年份尚未出现。

---

**第 44 行｜取得缺少的身份**

对应语句：`missing = sorted(expected_keys - actual_keys)`

**语法和执行含义：** expected_keys - actual_keys 是集合差集，得到应有而未有的成员；sorted 输出有序列表。

**为什么这样写：** 报错时直接列出缺哪一个分部财年，便于定位。

---

**第 45 行｜取得多余的身份**

对应语句：`extra = sorted(actual_keys - expected_keys)`

**语法和执行含义：** 反方向差集 actual_keys - expected_keys 得到实际多出的成员，再排序。

**为什么这样写：** 即使行数正确，替换成一个错误年份也会被发现。

---

**第 46 行｜报告覆盖差异**

对应语句：`raise ValueError(f"Coverage mismatch. Missing: {missing}; extra: {extra}")`

**语法和执行含义：** f-string 分别插入 missing 与 extra；raise 停止本次检查。

**为什么这样写：** 不以删行或补零掩盖研究覆盖问题，先修正原始文件或配置。

---

**第 47—48 行｜比较行数与计划数**

对应语句：`if len(clean_df) != config.get_observation_count(): ⏐ raise ValueError("Record count does not match the configured study.")`

**语法和执行含义：** len(clean_df) 返回行数；对象方法返回分部数乘时期数；不相等则 raise。

**为什么这样写：** 集合会去重，名单相同仍可能多了重复行。此处再次核对总数量，当前计划为十二行。

---

## Cell 05: Define the Database Manager

### 完整代码

```python
# Cell 05: Define the Database Manager

class DatabaseManager:
    """Own the database connection without embedding company-specific rules."""

    def __init__(self, database_path):
        self.database_path = Path(database_path)
        self.connection = None

    def connect(self):
        if self.connection is None:
            self.database_path.parent.mkdir(parents=True, exist_ok=True)
            self.connection = sqlite3.connect(str(self.database_path))
            self.connection.execute("PRAGMA foreign_keys = ON")

    def create_tables(self):
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS business_units (
                unit_id TEXT PRIMARY KEY,
                company_name TEXT NOT NULL,
                ticker TEXT NOT NULL,
                segment_name TEXT NOT NULL,
                currency TEXT NOT NULL,
                scope_notes TEXT NOT NULL,
                source_urls TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS financial_records (
                unit_id TEXT NOT NULL,
                fiscal_year INTEGER NOT NULL,
                period_start TEXT NOT NULL,
                period_end TEXT NOT NULL,
                net_sales_raw TEXT NOT NULL,
                operating_income_raw TEXT NOT NULL,
                reported_currency TEXT NOT NULL CHECK (reported_currency = 'USD'),
                reported_unit TEXT NOT NULL,
                source_url TEXT NOT NULL,
                source_section TEXT NOT NULL,
                accessed_date TEXT NOT NULL,
                date_basis TEXT NOT NULL,
                net_sales_usd_m REAL NOT NULL CHECK (net_sales_usd_m > 0),
                operating_income_usd_m REAL NOT NULL,
                PRIMARY KEY (unit_id, fiscal_year),
                FOREIGN KEY (unit_id) REFERENCES business_units(unit_id),
                CHECK (period_start < period_end)
            );
            CREATE TABLE IF NOT EXISTS metric_results (
                study_id TEXT NOT NULL,
                config_signature TEXT NOT NULL,
                unit_id TEXT NOT NULL,
                analysis_year INTEGER NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                value_unit TEXT NOT NULL,
                calculation_time TEXT NOT NULL,
                missing_reason TEXT,
                PRIMARY KEY (study_id, config_signature, unit_id, analysis_year, metric_name),
                FOREIGN KEY (unit_id) REFERENCES business_units(unit_id)
            );
        """)

    def save_data(self, config, clean_df):
        counts = {"inserted": 0, "updated": 0, "unchanged": 0}
        columns_sql = ", ".join(RECORD_COLUMNS)
        placeholders = ", ".join(["?"] * len(RECORD_COLUMNS))
        update_parts = []
        for column in RECORD_COLUMNS[2:]:
            update_parts.append(column + " = ?")
        update_sql = ", ".join(update_parts)

        with self.connection:
            for unit in config.business_units:
                unit_values = (
                    unit["company_name"], unit["ticker"], unit["segment_name"],
                    unit["currency"], "\n".join(unit["scope_notes"]),
                    "\n".join(unit["source_urls"]),
                )
                existing_unit = self.connection.execute(
                    "SELECT company_name, ticker, segment_name, currency, scope_notes, source_urls "
                    "FROM business_units WHERE unit_id = ?", (unit["unit_id"],)
                ).fetchone()
                if existing_unit is None:
                    self.connection.execute(
                        "INSERT INTO business_units "
                        "(company_name, ticker, segment_name, currency, scope_notes, source_urls, unit_id) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?)", unit_values + (unit["unit_id"],)
                    )
                elif existing_unit != unit_values:
                    self.connection.execute(
                        "UPDATE business_units SET company_name = ?, ticker = ?, segment_name = ?, "
                        "currency = ?, scope_notes = ?, source_urls = ? WHERE unit_id = ?",
                        unit_values + (unit["unit_id"],)
                    )
                    self.connection.execute("DELETE FROM metric_results WHERE unit_id = ?", (unit["unit_id"],))

            for row in clean_df.to_dict("records"):
                values = []
                for column in RECORD_COLUMNS:
                    values.append(row[column])
                values = tuple(values)
                key = (row["unit_id"], row["fiscal_year"])
                existing = self.connection.execute(
                    f"SELECT {columns_sql} FROM financial_records WHERE unit_id = ? AND fiscal_year = ?", key
                ).fetchone()
                if existing is None:
                    self.connection.execute(
                        f"INSERT INTO financial_records ({columns_sql}) VALUES ({placeholders})", values
                    )
                    counts["inserted"] += 1
                    self.connection.execute("DELETE FROM metric_results WHERE unit_id = ?", (row["unit_id"],))
                elif existing != values:
                    self.connection.execute(
                        f"UPDATE financial_records SET {update_sql} WHERE unit_id = ? AND fiscal_year = ?",
                        values[2:] + key,
                    )
                    counts["updated"] += 1
                    self.connection.execute("DELETE FROM metric_results WHERE unit_id = ?", (row["unit_id"],))
                else:
                    counts["unchanged"] += 1
        return counts

    def read_selected_records(self, config):
        frames = []
        for unit in config.business_units:
            years = []
            for period in config.periods:
                years.append(period["fiscal_years"][unit["unit_id"]])
            placeholders = ", ".join(["?"] * len(years))
            parameters = [unit["unit_id"]] + years
            query = f"""
                SELECT f.*, b.company_name, b.segment_name
                FROM financial_records AS f
                JOIN business_units AS b ON f.unit_id = b.unit_id
                WHERE f.unit_id = ? AND f.fiscal_year IN ({placeholders})
                ORDER BY f.fiscal_year
            """
            frames.append(pd.read_sql_query(query, self.connection, params=parameters))
        financial_df = pd.concat(frames, ignore_index=True)
        return financial_df.sort_values(["unit_id", "fiscal_year"]).reset_index(drop=True)

    def get_table_counts(self):
        counts = {}
        for table in ["business_units", "financial_records", "metric_results"]:
            row = self.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
            counts[table] = row[0]
        return counts

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 05: Define the Database Manager`

**语法和执行含义：** 井号 # 后面是注释，Python 不把它作为操作执行。Cell 编号表示本模块中的格子编号，不是 Notebook 的执行次数。

**为什么这样写：** 便于复制和定位每一格；保留英文标题，代码内不混入中文说明。

---

**第 3—4 行｜定义数据库管理类**

对应语句：`class DatabaseManager: ⏐ """Own the database connection without embedding company-specific rules."""`

**语法和执行含义：** class 定义一种对象，类名为 DatabaseManager；三引号描述类职责。此时不创建实例、文件或连接。

**为什么这样写：** 多个方法共享 database_path 和 connection，把持续使用的状态集中到同一个对象。

---

**第 6 行｜定义初始化方法**

对应语句：`def __init__(self, database_path):`

**语法和执行含义：** __init__ 在创建实例时自动执行。self 是当前实例，由 Python 自动提供；database_path 是调用者传入的路径。

**为什么这样写：** 对象创建时就需要记住路径与初始状态，后面的数据库操作用普通方法主动调用。

---

**第 7 行｜把路径保存到对象**

对应语句：`self.database_path = Path(database_path)`

**语法和执行含义：** Path(database_path) 创建路径对象，赋给 self.database_path；左边是对象属性，右边 database_path 是本次方法参数。

**为什么这样写：** 参数只在方法调用中使用，保存成属性后 connect 等其他方法也能访问。

---

**第 8 行｜设置未连接状态**

对应语句：`self.connection = None`

**语法和执行含义：** None 表示没有连接对象，赋给 self.connection；它不是字符串 "None" 或数字零。

**为什么这样写：** 初始化与实际连接分开，创建实例不会马上创建数据库文件。

---

**第 10 行｜定义连接方法**

对应语句：`def connect(self):`

**语法和执行含义：** connect 接收 self，不需额外路径参数，因为路径已经在对象中。方法返回 None，但会改变对象状态。

**为什么这样写：** 用 database.connect() 在合适时机连接，而不是每次查询都新建连接。

---

**第 11 行｜避免同一对象重复连接**

对应语句：`if self.connection is None:`

**语法和执行含义：** is None 检查 connection 是否确实为 None，只有未连接时进入缩进块。

**为什么这样写：** 已有连接时保持原连接，避免重复打开并遗失原对象。

---

**第 12 行｜保证数据库父目录存在**

对应语句：`self.database_path.parent.mkdir(parents=True, exist_ok=True)`

**语法和执行含义：** parent 取得数据库所在目录；mkdir 创建目录，parents=True 补齐上层目录，exist_ok=True 允许目录已存在。

**为什么这样写：** SQLite 能创建文件，但不会替你建立不存在的文件夹，所以先准备目录。

---

**第 13 行｜连接文件并保存连接对象**

对应语句：`self.connection = sqlite3.connect(str(self.database_path))`

**语法和执行含义：** str 将 Path 转路径文字；sqlite3.connect 打开已有库或创建新库，返回连接对象，赋给 self.connection。

**为什么这样写：** 后面的 execute、executescript 与事务都通过这一个连接操作。

---

**第 14 行｜为当前连接启用外键检查**

对应语句：`self.connection.execute("PRAGMA foreign_keys = ON")`

**语法和执行含义：** execute 执行一条 SQL 设置语句。PRAGMA foreign_keys = ON 打开当前连接的外键约束。

**为什么这样写：** 年度财务的 unit_id 必须已有对应分部；后面先写分部表，再写财务表。

---

**第 16—17 行｜定义建表方法并执行多条 SQL**

对应语句：`def create_tables(self): ⏐ self.connection.executescript("""`

**语法和执行含义：** def 定义方法；executescript 接收三引号开始的多行字符串，执行其中由分号分开的建表 SQL。下面的缩进文字是 SQL 内容，不是 Python 变量赋值。

**为什么这样写：** 三张表一次建立，语句结构集中在这里；Cell 09 调用时才执行。

---

**第 18 行｜创建分部资料表**

对应语句：`CREATE TABLE IF NOT EXISTS business_units (`

**语法和执行含义：** CREATE TABLE IF NOT EXISTS 指定表名 business_units，左括号开始列和约束定义。已存在同名表时保留。

**为什么这样写：** 一行表示一个分部，保存相对稳定的身份和口径，不重复保存年度金额。此语句不升级已有旧表结构。

---

**第 19 行｜用标识区分分部**

对应语句：`unit_id TEXT PRIMARY KEY,`

**语法和执行含义：** unit_id 是 TEXT 字段，PRIMARY KEY 指定记录身份并限制非空标识重复；本项目的非空内容由配置校验保障。

**为什么这样写：** 用稳定标识关联记录，不以显示名称作为连接依据。

---

**第 20—25 行｜定义分部资料的六个字段**

对应语句：`company_name TEXT NOT NULL, ⏐ ticker TEXT NOT NULL, ⏐ segment_name TEXT NOT NULL, ⏐ currency TEXT NOT NULL, ⏐ scope_notes TEXT NOT NULL, ⏐ source_urls TEXT NOT NULL`

**语法和执行含义：** company_name 是公司名，ticker 是股票代码，segment_name 是分部名，currency 是币种，scope_notes 是口径说明文字，source_urls 是来源文字。各行 TEXT 表示文本，NOT NULL 拒绝 SQL NULL。

**为什么这样写：** 名称与说明存一次即可。NOT NULL 不单独拒绝空字符串，所以仍需要 Python 内容检查。两个说明列表之后用换行连接为 TEXT。

---

**第 26 行｜结束第一张表的 SQL**

对应语句：`);`

**语法和执行含义：** 右括号结束表定义，分号结束这条 CREATE TABLE。

**为什么这样写：** executescript 可以随后继续执行下一条建表语句。

---

**第 27 行｜创建年度财务表**

对应语句：`CREATE TABLE IF NOT EXISTS financial_records (`

**语法和执行含义：** 开始 financial_records 的定义，一行对应一个分部的实际报告财年。

**为什么这样写：** 基础数据保留 fiscal_year 和实际日期，分析年度和疫情阶段以后按研究配置加入。

---

**第 28—29 行｜定义财务身份字段**

对应语句：`unit_id TEXT NOT NULL, ⏐ fiscal_year INTEGER NOT NULL,`

**语法和执行含义：** unit_id 用 TEXT，fiscal_year 用 INTEGER，两者 NOT NULL；后面将一起作为联合主键。

**为什么这样写：** 同一个分部可有六年记录，单用 unit_id 不能区分年份。

---

**第 30—31 行｜保存报告期间**

对应语句：`period_start TEXT NOT NULL, ⏐ period_end TEXT NOT NULL,`

**语法和执行含义：** period_start 与 period_end 为文本字段；前面的标准化已统一成 YYYY-MM-DD。

**为什么这样写：** 保留真实期间，让两家近似配对时的日期差异可追溯。

---

**第 32—33 行｜保存原始金额文本**

对应语句：`net_sales_raw TEXT NOT NULL, ⏐ operating_income_raw TEXT NOT NULL,`

**语法和执行含义：** net_sales_raw 和 operating_income_raw 用 TEXT，保留千位逗号和亏损括号。

**为什么这样写：** 标准数值便于计算，原始字符串便于回查披露，两种表示都有用途。

---

**第 34 行｜要求披露币种为 USD**

对应语句：`reported_currency TEXT NOT NULL CHECK (reported_currency = 'USD'),`

**语法和执行含义：** TEXT 与 NOT NULL 指定文本及非 NULL；CHECK (reported_currency = 'USD') 再要求具体值为 USD。

**为什么这样写：** 数据库也拒绝其他币种，作为 Python 检查之外的额外约束。

---

**第 35 行｜保留原始数量级**

对应语句：`reported_unit TEXT NOT NULL,`

**语法和执行含义：** reported_unit 用 TEXT 保存 millions 等原始单位，不使用标准金额替代它。

**为什么这样写：** 知道原表单位才能复核换算是否正确。

---

**第 36—39 行｜保存每条数值的出处**

对应语句：`source_url TEXT NOT NULL, ⏐ source_section TEXT NOT NULL, ⏐ accessed_date TEXT NOT NULL, ⏐ date_basis TEXT NOT NULL,`

**语法和执行含义：** source_url 保存具体网址；source_section 保存章节与列；accessed_date 保存访问日；date_basis 保存报告日期采用依据，均为非 NULL 文本。

**为什么这样写：** 把来源附在各年度记录上，而不是仅保存一个无法定位金额的公司主页。

---

**第 40 行｜定义标准销售额及条件**

对应语句：`net_sales_usd_m REAL NOT NULL CHECK (net_sales_usd_m > 0),`

**语法和执行含义：** net_sales_usd_m 用 REAL 保存浮点数，NOT NULL 拒绝缺失，CHECK 要求大于零。

**为什么这样写：** 统一为百万美元，可供后续分母与指数计算；零或负销售额会在 SQL 写入时被拒绝。

---

**第 41 行｜定义标准营业利润**

对应语句：`operating_income_usd_m REAL NOT NULL,`

**语法和执行含义：** operating_income_usd_m 为 REAL NOT NULL，没有增加大于零的 CHECK。

**为什么这样写：** 营业利润可以亏损，合法负数应保存下来。

---

**第 42 行｜定义联合主键**

对应语句：`PRIMARY KEY (unit_id, fiscal_year),`

**语法和执行含义：** PRIMARY KEY (unit_id, fiscal_year) 让两个字段共同识别一行。

**为什么这样写：** 同一分部同一报告财年不能保存两条独立记录，更新时通过这两个条件定位。

---

**第 43 行｜关联已存在的分部**

对应语句：`FOREIGN KEY (unit_id) REFERENCES business_units(unit_id),`

**语法和执行含义：** FOREIGN KEY 指定本表 unit_id 引用 business_units 的 unit_id。

**为什么这样写：** 启用外键后，不允许财务记录引用不存在的分部，两个表的身份保持一致。

---

**第 44—45 行｜约束日期并结束财务表**

对应语句：`CHECK (period_start < period_end) ⏐ );`

**语法和执行含义：** CHECK 要求开始日早于结束日；下一行右括号和分号结束本表定义。这里按标准化后的合法 ISO 文本比较。

**为什么这样写：** 即使调用者跳过部分 Python 检查，写入时仍有日期顺序约束；它不能证明日期来自财报。

---

**第 46 行｜创建指标结果表**

对应语句：`CREATE TABLE IF NOT EXISTS metric_results (`

**语法和执行含义：** 开始 metric_results 的结构定义，现在不 INSERT 任何指标。

**为什么这样写：** 让 Module 03 有明确的保存接口，建表与计算是不同动作。

---

**第 47—51 行｜定义指标身份及名称**

对应语句：`study_id TEXT NOT NULL, ⏐ config_signature TEXT NOT NULL, ⏐ unit_id TEXT NOT NULL, ⏐ analysis_year INTEGER NOT NULL, ⏐ metric_name TEXT NOT NULL,`

**语法和执行含义：** study_id 为研究标识，config_signature 为配置版本标识，unit_id 为分部标识，analysis_year 为整数分析年度，metric_name 为指标名。这些字段均不能为 NULL。

**为什么这样写：** 同一基础数据可以供不同研究和配置使用，结果需要知道是哪一个研究版本算出来的。

---

**第 52 行｜允许缺失的指标值**

对应语句：`metric_value REAL,`

**语法和执行含义：** metric_value 声明为 REAL，但没有 NOT NULL，因而可以保存 SQL NULL。

**为什么这样写：** 例如没有前一年数据的同比不能当成零；缺失结果应有明确表示。

---

**第 53—55 行｜记录指标单位和计算信息**

对应语句：`value_unit TEXT NOT NULL, ⏐ calculation_time TEXT NOT NULL, ⏐ missing_reason TEXT,`

**语法和执行含义：** value_unit 是单位文字，calculation_time 是计算时刻，两者非 NULL；missing_reason 可为 NULL，缺失结果可注明原因。

**为什么这样写：** 区分百分比、指数等单位，并追溯计算时间与未能计算的原因。本模块只预留字段。

---

**第 56—57 行｜定义结果身份与关联**

对应语句：`PRIMARY KEY (study_id, config_signature, unit_id, analysis_year, metric_name), ⏐ FOREIGN KEY (unit_id) REFERENCES business_units(unit_id)`

**语法和执行含义：** 五个字段组成联合主键，区分研究、配置、分部、年度、指标；外键仍指向分部表。

**为什么这样写：** 相同身份的指标结果不重复存，结果与对应分部保持联系。

---

**第 58—59 行｜结束 SQL 字符串和调用**

对应语句：`); ⏐ """)`

**语法和执行含义：** 第 58 行结束指标表 SQL；第 59 行三个引号关闭多行字符串，右括号结束 executescript 调用。

**为什么这样写：** 上面的三张表结构形成一份完整脚本；括号和引号不能遗漏。

---

**第 61 行｜定义保存方法的输入**

对应语句：`def save_data(self, config, clean_df):`

**语法和执行含义：** save_data 使用当前连接、配置对象和已通过检查的 DataFrame；方法最后返回计数字典。

**为什么这样写：** 分部定义和年度记录来源不同，在同一批操作中分别保存。此方法不替你调用 validate_records。

---

**第 62 行｜初始化本次操作计数**

对应语句：`counts = {"inserted": 0, "updated": 0, "unchanged": 0}`

**语法和执行含义：** 创建字典，三个键对应新增、更新、不变，初始值均为零。

**为什么这样写：** 只统计本次年度财务记录操作，不是完整表的历史总量，也不计分部资料的变化。

---

**第 63 行｜连接 SQL 的列名**

对应语句：`columns_sql = ", ".join(RECORD_COLUMNS)`

**语法和执行含义：** ", ".join(RECORD_COLUMNS) 在各列名之间放逗号和空格，得到一个长字符串。

**为什么这样写：** SELECT 与 INSERT 使用同样的列顺序，便于与参数元组逐项对应。

---

**第 64 行｜创建相同数量的占位符**

对应语句：`placeholders = ", ".join(["?"] * len(RECORD_COLUMNS))`

**语法和执行含义：** ["?"] * len(RECORD_COLUMNS) 生成十四个问号组成的列表；join 将它连成 SQL 文本。

**为什么这样写：** INSERT 有十四列就需要十四个参数。真实金额、名称等通过参数传入，不直接拼进 SQL。

---

**第 65 行｜准备 UPDATE 的片段列表**

对应语句：`update_parts = []`

**语法和执行含义：** [] 创建空列表 update_parts，随后逐列加入赋值表达式。

**为什么这样写：** UPDATE 的 SET 部分需要列名与占位符，而不是 INSERT 的单纯列名列表。

---

**第 66—67 行｜只更新非主键字段**

对应语句：`for column in RECORD_COLUMNS[2:]: ⏐ update_parts.append(column + " = ?")`

**语法和执行含义：** RECORD_COLUMNS[2:] 跳过前两个身份字段；每轮把列名加上 " = ?" 并 append。

**为什么这样写：** 主键用于查找原记录，这个操作只更新其余十二个字段，避免改动身份。

---

**第 68 行｜组合 UPDATE 赋值部分**

对应语句：`update_sql = ", ".join(update_parts)`

**语法和执行含义：** 用逗号连接各个 column = ? 片段，保存到 update_sql。

**为什么这样写：** 例如 period_start = ?, period_end = ?，可嵌入后面的 SET 部分。

---

**第 70 行｜用事务管理这一批写入**

对应语句：`with self.connection:`

**语法和执行含义：** with 调用连接的上下文管理。在此代码的默认连接方式下，正常结束提交 DML，异常离开回滚尚未提交的本批修改。

**为什么这样写：** 避免导入半份数据。它不会自动关闭连接；已在前一步建好的表结构也不因此消失。

---

**第 71 行｜先逐个处理分部定义**

对应语句：`for unit in config.business_units:`

**语法和执行含义：** for 读取 config.business_units 中的各分部，下面的缩进块都在事务内。

**为什么这样写：** 外键要求年度数据写入前已有对应分部资料。

---

**第 72—76 行｜按固定顺序准备六个分部值**

对应语句：`unit_values = ( ⏐ unit["company_name"], unit["ticker"], unit["segment_name"], ⏐ unit["currency"], "\n".join(unit["scope_notes"]), ⏐ "\n".join(unit["source_urls"]), ⏐ )`

**语法和执行含义：** 圆括号与逗号组成元组。第 73 行取公司、股票代码、分部名；第 74 行取币种并将说明列表用换行连接；第 75 行连接 URL 列表；第 76 行结束元组。

**为什么这样写：** 顺序必须对应后面的 SELECT 和 UPDATE 六个字段。小型文字列表暂存为一段 TEXT，避免增加更多表。

---

**第 77—80 行｜查询现有分部并取得一行**

对应语句：`existing_unit = self.connection.execute( ⏐ "SELECT company_name, ticker, segment_name, currency, scope_notes, source_urls " ⏐ "FROM business_units WHERE unit_id = ?", (unit["unit_id"],) ⏐ ).fetchone()`

**语法和执行含义：** execute 接收 SQL 与参数。第 78、79 行相邻字符串自动连接为一条 SELECT；WHERE 的问号接收 (unit_id,) 单元素元组；fetchone 返回一行值元组，无行时返回 None。

**为什么这样写：** 先查再决定插入或更新。单元素元组靠末尾逗号识别，不能只留下括号。

---

**第 81—86 行｜不存在时插入分部**

对应语句：`if existing_unit is None: ⏐ self.connection.execute( ⏐ "INSERT INTO business_units " ⏐ "(company_name, ticker, segment_name, currency, scope_notes, source_urls, unit_id) " ⏐ "VALUES (?, ?, ?, ?, ?, ?, ?)", unit_values + (unit["unit_id"],) ⏐ )`

**语法和执行含义：** existing_unit is None 表示没找到；execute 的 INSERT 声明七个列，第 85 行七个问号接收六个 unit_values 加最后一个标识。元组 + 是连接，不是数值相加。

**为什么这样写：** 新分部保存一次，字段值顺序与 INSERT 列序一致。

---

**第 87—92 行｜已有但不同则更新分部**

对应语句：`elif existing_unit != unit_values: ⏐ self.connection.execute( ⏐ "UPDATE business_units SET company_name = ?, ticker = ?, segment_name = ?, " ⏐ "currency = ?, scope_notes = ?, source_urls = ? WHERE unit_id = ?", ⏐ unit_values + (unit["unit_id"],) ⏐ )`

**语法和执行含义：** elif 只在前面的 if 不成立时检查；两个六元素元组不同则 UPDATE。六个新值对应 SET，最后一个标识对应 WHERE。

**为什么这样写：** 保留分部身份并同步变化的名称或口径；完全相同的定义不重复写。

---

**第 93 行｜分部定义变更使旧指标失效**

对应语句：`self.connection.execute("DELETE FROM metric_results WHERE unit_id = ?", (unit["unit_id"],))`

**语法和执行含义：** DELETE 仅针对 metric_results 中这个 unit_id 的行，参数仍是单元素元组。

**为什么这样写：** 口径或来源定义发生改变时，已有派生结果应重新计算；基础财务行没有被删除。

---

**第 95 行｜逐行处理已接受的年度数据**

对应语句：`for row in clean_df.to_dict("records"):`

**语法和执行含义：** clean_df.to_dict("records") 生成行字典列表，for 每次处理一行。此循环仍在 with 的事务内，与分部循环是同一缩进层级。

**为什么这样写：** 把分部资料和全部年度记录作为一批保存，失败时可一并回滚。

---

**第 96—99 行｜按列序生成值元组**

对应语句：`values = [] ⏐ for column in RECORD_COLUMNS: ⏐ values.append(row[column]) ⏐ values = tuple(values)`

**语法和执行含义：** 先空列表，for 按 RECORD_COLUMNS 的顺序取 row[column] 并 append，最后 tuple(values) 转为元组并覆盖 values 变量。

**为什么这样写：** 固定十四个值的顺序；后面的数据库查询也按同一列序返回，才能准确比较。

---

**第 100 行｜取出年度联合身份**

对应语句：`key = (row["unit_id"], row["fiscal_year"])`

**语法和执行含义：** 将当前 unit_id 与 fiscal_year 组成 key 元组。

**为什么这样写：** 查找同一分部财年的旧记录，以及 UPDATE 的 WHERE 条件都使用它。

---

**第 101—103 行｜查询同一身份的旧财务记录**

对应语句：`existing = self.connection.execute( ⏐ f"SELECT {columns_sql} FROM financial_records WHERE unit_id = ? AND fiscal_year = ?", key ⏐ ).fetchone()`

**语法和执行含义：** f-string 放入固定列名，WHERE 有两个问号，key 提供两个值；fetchone 返回十四个旧字段组成的元组或 None。

**为什么这样写：** 取得完整字段，而不只看金额，才能识别来源或日期是否更新。

---

**第 104—107 行｜没有旧记录就插入**

对应语句：`if existing is None: ⏐ self.connection.execute( ⏐ f"INSERT INTO financial_records ({columns_sql}) VALUES ({placeholders})", values ⏐ )`

**语法和执行含义：** if 判断 None；INSERT 的列名与问号部分由之前固定规则生成，values 提供十四个值。

**为什么这样写：** 第一次导入写入新行；主键与外键在 SQL 中再约束身份。

---

**第 108 行｜新增计数加一**

对应语句：`counts["inserted"] += 1`

**语法和执行含义：** counts["inserted"] += 1 等于把当前值加一，再写回该键。

**为什么这样写：** 每成功新增一条财务记录计一次，返回统计方便检查本次运行。

---

**第 109 行｜新增数据后清除该分部旧指标**

对应语句：`self.connection.execute("DELETE FROM metric_results WHERE unit_id = ?", (row["unit_id"],))`

**语法和执行含义：** 删除指标表中对应 unit_id 的行。

**为什么这样写：** 新增基础数据可能改变覆盖或派生结果，采用简单的整分部重新计算规则。

---

**第 110—114 行｜字段变化时更新年度记录**

对应语句：`elif existing != values: ⏐ self.connection.execute( ⏐ f"UPDATE financial_records SET {update_sql} WHERE unit_id = ? AND fiscal_year = ?", ⏐ values[2:] + key, ⏐ )`

**语法和执行含义：** 旧记录存在且 existing 与 values 元组不同才进入 elif。SET 对应 values[2:] 的十二个新值，WHERE 对应加在最后的 key 两个值。

**为什么这样写：** 金额、日期和来源都参与比较。十四个参数顺序不能反过来；身份本身不更新。

---

**第 115—116 行｜记录更新并使旧指标失效**

对应语句：`counts["updated"] += 1 ⏐ self.connection.execute("DELETE FROM metric_results WHERE unit_id = ?", (row["unit_id"],))`

**语法和执行含义：** updated 加一，再删除该分部已保存的派生指标。

**为什么这样写：** 某年的销售额变化会影响同比或指数，因此不能沿用旧结果；来源或访问日变化也算更新。

---

**第 117—118 行｜完全相同则不写入**

对应语句：`else: ⏐ counts["unchanged"] += 1`

**语法和执行含义：** else 对应旧记录已存在且所有值相同；只将 unchanged 加一，不执行财务 UPDATE 和指标 DELETE。

**为什么这样写：** 重复运行保持稳定，不增加重复记录，也保留仍适用的指标。

---

**第 119 行｜提交后返回统计**

对应语句：`return counts`

**语法和执行含义：** return 的缩进已经离开 with 块。正常退出事务提交后，返回 counts 给调用者。

**为什么这样写：** 失败时异常会离开方法，不会正常返回本次成功统计。

---

**第 121 行｜定义按研究范围查询方法**

对应语句：`def read_selected_records(self, config):`

**语法和执行含义：** config 决定需要哪些分部财年；方法使用当前连接并返回 DataFrame。

**为什么这样写：** 数据库可保存更多内容，但当前分析只读取配置要求的记录。

---

**第 122 行｜准备各分部查询表的列表**

对应语句：`frames = []`

**语法和执行含义：** frames = [] 建立空列表，后面每家分部查询结果 append 一次。

**为什么这样写：** 最后合并查询结果，避免人为固定只有一家公司。

---

**第 123—126 行｜从配置收集每个分部的财年**

对应语句：`for unit in config.business_units: ⏐ years = [] ⏐ for period in config.periods: ⏐ years.append(period["fiscal_years"][unit["unit_id"]])`

**语法和执行含义：** 外层遍历分部；每家先清空 years；内层遍历时期，按 period 的 fiscal_years 映射查询该分部年份，再 append。

**为什么这样写：** Amazon 与 Walmart 的实际财年不同，用配置映射决定而不写公司特例。

---

**第 127 行｜为年份筛选创建问号**

对应语句：`placeholders = ", ".join(["?"] * len(years))`

**语法和执行含义：** 按 len(years) 生成同样数量的占位符，这里每家有六个。

**为什么这样写：** IN 子句需要与财年列表长度对应，年份数改变时不改通用 SQL。

---

**第 128 行｜准备七个查询参数**

对应语句：`parameters = [unit["unit_id"]] + years`

**语法和执行含义：** 列表 [unit_id] 与 years 连接，得到一个分部标识加六个财年。

**为什么这样写：** WHERE 的第一个问号取标识，IN 里的后六个问号按年取值。

---

**第 129—130 行｜开始查询并指定输出字段**

对应语句：`query = f""" ⏐ SELECT f.*, b.company_name, b.segment_name`

**语法和执行含义：** f-string 三引号创建多行 SQL；SELECT f.* 取财务表全部字段，再增加分部表的公司名和分部名。

**为什么这样写：** 基础表没有重复存这两个名称，查询仍需恢复完整的审查数据。

---

**第 131 行｜指定财务表及别名**

对应语句：`FROM financial_records AS f`

**语法和执行含义：** FROM 说明主表，AS f 给表取简短别名，后面 f.字段 指向这张表。

**为什么这样写：** 连接多表时避免同名字段来源不清楚。

---

**第 132 行｜通过稳定标识连接分部表**

对应语句：`JOIN business_units AS b ON f.unit_id = b.unit_id`

**语法和执行含义：** JOIN business_units AS b 引入第二张表，ON 要求 f.unit_id 等于 b.unit_id。

**为什么这样写：** 将每年财务数据配上正确分部名称，不能依据显示行号连接。

---

**第 133 行｜限定当前分部和财年**

对应语句：`WHERE f.unit_id = ? AND f.fiscal_year IN ({placeholders})`

**语法和执行含义：** WHERE 的两个条件通过 AND 同时满足；IN 选择列表中的任意财年，f-string 在其中插入固定问号字符串。

**为什么这样写：** 只查询配置要求的范围，真实值通过 parameters 提供。

---

**第 134—135 行｜按财年排序并结束字符串**

对应语句：`ORDER BY f.fiscal_year ⏐ """`

**语法和执行含义：** ORDER BY 指定查询返回顺序，下一行三引号结束 SQL 文本。

**为什么这样写：** 每家先按财年返回，后面合并时再做统一排序。

---

**第 136 行｜SQL 查询生成 DataFrame**

对应语句：`frames.append(pd.read_sql_query(query, self.connection, params=parameters))`

**语法和执行含义：** pd.read_sql_query 接收 SQL、连接及 params 参数，返回查询结果 DataFrame，立即 append 到 frames。

**为什么这样写：** 这是从已保存数据库读取，不是给 clean_df 另取变量名。

---

**第 137—138 行｜合并并返回查询结果**

对应语句：`financial_df = pd.concat(frames, ignore_index=True) ⏐ return financial_df.sort_values(["unit_id", "fiscal_year"]).reset_index(drop=True)`

**语法和执行含义：** pd.concat 把各分部的表按行合并，ignore_index=True 重编索引；再按身份排序、重设索引并 return。

**为什么这样写：** 给 Cell 11 一个完整且顺序稳定的 financial_df，供覆盖检查和逐字段比较。

---

**第 140—142 行｜准备统计三张表**

对应语句：`def get_table_counts(self): ⏐ counts = {} ⏐ for table in ["business_units", "financial_records", "metric_results"]:`

**语法和执行含义：** 定义 get_table_counts；创建计数字典，for 从固定三张表名中依次取 table。

**为什么这样写：** 统计完整表的行数，而非仅本研究选中的查询结果。

---

**第 143 行｜查询整表行数**

对应语句：`row = self.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()`

**语法和执行含义：** SELECT COUNT(*) 返回一行计数；表名来自固定代码列表，fetchone 取得例如 (12,) 的元组。

**为什么这样写：** 此处 COUNT 是 SQL 聚合，不是读取全部行后手工数。

---

**第 144—145 行｜取出数字并返回字典**

对应语句：`counts[table] = row[0] ⏐ return counts`

**语法和执行含义：** row[0] 取单元素元组的第一项，以 table 为字典键保存；循环结束后 return counts。

**为什么这样写：** 调用者可分别查看各表数量，当前案例新库通常为 2、12、0。

---

**第 147—148 行｜定义关闭方法并判断状态**

对应语句：`def close(self): ⏐ if self.connection is not None:`

**语法和执行含义：** close 接收当前对象；is not None 要求已有连接才执行下方关闭操作。

**为什么这样写：** 未连接或已关闭时不重复调用 SQLite close。

---

**第 149—150 行｜关闭连接并复原状态**

对应语句：`self.connection.close() ⏐ self.connection = None`

**语法和执行含义：** 先调用连接对象 close，再把属性设回 None。

**为什么这样写：** 释放连接资源，标明之后需要重新 connect；已提交文件和内存 DataFrame 不被删除。

---

## Cell 06: Load Source CSV Files into DataFrames

### 完整代码

```python
# Cell 06: Load Source CSV Files into DataFrames

source_frames = {}
for unit_id in RAW_FILES:
    raw_file = RAW_FILES[unit_id]
    frame = pd.read_csv(raw_file, dtype=str, keep_default_na=False)
    if "unit_id" not in frame.columns or not frame["unit_id"].eq(unit_id).all():
        raise ValueError(f"Source file does not match its configured unit: {raw_file}")
    source_frames[unit_id] = frame
    print(f"Loaded {unit_id}: {len(frame)} rows")

amazon_raw_df = source_frames["amazon_north_america"]
walmart_raw_df = source_frames["walmart_us"]
raw_df = pd.concat(list(source_frames.values()), ignore_index=True)

print(f"Combined raw records: {len(raw_df)}")
print(raw_df[["unit_id", "fiscal_year", "net_sales_raw", "operating_income_raw"]].to_string(index=False))
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 06: Load Source CSV Files into DataFrames`

**语法和执行含义：** 井号 # 后面是注释，Python 不把它作为操作执行。Cell 编号表示本模块中的格子编号，不是 Notebook 的执行次数。

**为什么这样写：** 便于复制和定位每一格；保留英文标题，代码内不混入中文说明。

---

**第 3 行｜准备保存各分部原始表**

对应语句：`source_frames = {}`

**语法和执行含义：** {} 创建字典 source_frames，键将是 unit_id，值将是该分部的 DataFrame。

**为什么这样写：** 各分部保留独立表，便于检查，再组合成一张输入表。

---

**第 4—5 行｜按映射逐份取文件位置**

对应语句：`for unit_id in RAW_FILES: ⏐ raw_file = RAW_FILES[unit_id]`

**语法和执行含义：** for 遍历 RAW_FILES 的字典键；通过同一个键查询其路径，赋给 raw_file。

**为什么这样写：** 研究文件选择来自 Cell 02，读取流程本身不用判断公司名称。

---

**第 6 行｜将 CSV 读入内存**

对应语句：`frame = pd.read_csv(raw_file, dtype=str, keep_default_na=False)`

**语法和执行含义：** pd.read_csv 返回 DataFrame。dtype=str 要求原始字段按文字读取，keep_default_na=False 不把默认文本标记自动解释成 NaN。

**为什么这样写：** 保留逗号和括号，稍后明确处理缺失与金额。这里读取本地 CSV，没有自动下载财报。

---

**第 7—8 行｜核对源文件归属**

对应语句：`if "unit_id" not in frame.columns or not frame["unit_id"].eq(unit_id).all(): ⏐ raise ValueError(f"Source file does not match its configured unit: {raw_file}")`

**语法和执行含义：** or 左侧检查有没有 unit_id 列；若列不存在就短路，不继续访问它。若存在，eq 逐行匹配标识、all 要求全匹配，not 让不匹配触发 raise。

**为什么这样写：** 发现两家文件路径填反或混入其他标识的情况，错误信息显示当前文件。

---

**第 9 行｜把表放入字典**

对应语句：`source_frames[unit_id] = frame`

**语法和执行含义：** source_frames[unit_id] = frame 以当前标识保存读取结果。

**为什么这样写：** 循环结束后可以按标识取得任何一份原始表。

---

**第 10 行｜显示本份读取数量**

对应语句：`print(f"Loaded {unit_id}: {len(frame)} rows")`

**语法和执行含义：** len(frame) 数 DataFrame 行数，f-string 显示分部和行数；本行仍在循环内，所以每份文件打印一次。

**为什么这样写：** 确认每家实际读到六行，打印本身不验证完整研究覆盖。

---

**第 12—13 行｜为两份原始表设置展示名称**

对应语句：`amazon_raw_df = source_frames["amazon_north_america"] ⏐ walmart_raw_df = source_frames["walmart_us"]`

**语法和执行含义：** 根据标识从字典取得 DataFrame，分别赋给 amazon_raw_df 与 walmart_raw_df。这是同一对象的另一个名称，不是 copy。

**为什么这样写：** 方便当前案例查看。需要独立修改副本时再显式 copy，不要误认为赋值自动复制数据。

---

**第 14 行｜按行组合为 raw_df**

对应语句：`raw_df = pd.concat(list(source_frames.values()), ignore_index=True)`

**语法和执行含义：** values() 取得字典中的表，list 将它们组成列表；concat 默认沿行组合，ignore_index=True 重新生成连续索引。

**为什么这样写：** 两个六行表组成十二行表，不沿用两个重复的 0—5 显示索引。

---

**第 16 行｜显示组合总行数**

对应语句：`print(f"Combined raw records: {len(raw_df)}")`

**语法和执行含义：** len(raw_df) 计算实际组合行数，再 print 输出。

**为什么这样写：** 数量应为十二，是否包含正确的十二个身份还要 Cell 07 检查。

---

**第 17 行｜只显示四个核对列**

对应语句：`print(raw_df[["unit_id", "fiscal_year", "net_sales_raw", "operating_income_raw"]].to_string(index=False))`

**语法和执行含义：** raw_df[[...]] 用列名列表选多列，所以出现双层方括号；to_string 生成显示文本，index=False 隐藏索引；print 输出。

**为什么这样写：** 查看身份与原始金额，不修改 raw_df、不保存 CSV、不写数据库。

---

## Cell 07: Standardize and Validate the Financial Records

### 完整代码

```python
# Cell 07: Standardize and Validate the Financial Records

clean_df = standardize_records(raw_df)
validate_records(clean_df, config)

print("Financial record checks passed.")
print(clean_df[["unit_id", "fiscal_year", "period_start", "period_end", "net_sales_usd_m", "operating_income_usd_m"]].to_string(index=False))
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 07: Standardize and Validate the Financial Records`

**语法和执行含义：** 井号 # 后面是注释，Python 不把它作为操作执行。Cell 编号表示本模块中的格子编号，不是 Notebook 的执行次数。

**为什么这样写：** 便于复制和定位每一格；保留英文标题，代码内不混入中文说明。

---

**第 3 行｜调用清洗并接收返回表**

对应语句：`clean_df = standardize_records(raw_df)`

**语法和执行含义：** 右侧 standardize_records(raw_df) 执行 Cell 03 的整表函数，左侧 clean_df 接收返回的 DataFrame。

**为什么这样写：** 输入仍为原始表，标准表另有变量；此时实际生成两列标准数值。

---

**第 4 行｜调用检查而不接收新表**

对应语句：`validate_records(clean_df, config)`

**语法和执行含义：** validate_records 接收标准表和配置，通过时返回 None，不赋值给 clean_df。

**为什么这样写：** 先标准化再检查。写 clean_df = validate_records(...) 会将表变量覆盖成 None。

---

**第 6 行｜只有检查通过才显示成功**

对应语句：`print("Financial record checks passed.")`

**语法和执行含义：** 前两句无异常才执行本行；单独运行这句 print 不能证明检查成功。

**为什么这样写：** 让输出与控制流程对应，失败时不要跳过检查继续写库。

---

**第 7 行｜显示标准数值核对视图**

对应语句：`print(clean_df[["unit_id", "fiscal_year", "period_start", "period_end", "net_sales_usd_m", "operating_income_usd_m"]].to_string(index=False))`

**语法和执行含义：** 选取标识、财年、期间、两个标准金额列，转显示文本并隐藏索引。

**为什么这样写：** 标准表共有十六列，这里仅显示六列；原始披露与来源字段仍在完整表中。

---

## Cell 08: Save the Import Snapshot and Clean Audit File

### 完整代码

```python
# Cell 08: Save the Import Snapshot and Clean Audit File

DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
CLEAN_FILE.parent.mkdir(parents=True, exist_ok=True)
raw_df.to_csv(DATA_FILE, index=False)
clean_df.to_csv(CLEAN_FILE, index=False)

print(f"Import snapshot saved: {DATA_FILE}")
print(f"Clean audit file saved: {CLEAN_FILE}")
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 08: Save the Import Snapshot and Clean Audit File`

**语法和执行含义：** 井号 # 后面是注释，Python 不把它作为操作执行。Cell 编号表示本模块中的格子编号，不是 Notebook 的执行次数。

**为什么这样写：** 便于复制和定位每一格；保留英文标题，代码内不混入中文说明。

---

**第 3 行｜准备快照保存目录**

对应语句：`DATA_FILE.parent.mkdir(parents=True, exist_ok=True)`

**语法和执行含义：** 从 DATA_FILE 取得 parent，mkdir 允许创建上级目录和复用已有目录。

**为什么这样写：** to_csv 写文件前，其所在目录必须存在。

---

**第 4 行｜准备清洗输出目录**

对应语句：`CLEAN_FILE.parent.mkdir(parents=True, exist_ok=True)`

**语法和执行含义：** 对 CLEAN_FILE 的 parent 做同样操作，即 data/clean/。

**为什么这样写：** 原始组合快照与清洗表分开位置，便于审查。

---

**第 5 行｜导出组合原始快照**

对应语句：`raw_df.to_csv(DATA_FILE, index=False)`

**语法和执行含义：** raw_df.to_csv 将原始组合表写到 DATA_FILE，index=False 不导出显示索引。默认模式会覆盖已有同名导出。

**为什么这样写：** 保留这次输入的组合版本，不覆盖 raw/ 中两份源文件。

---

**第 6 行｜导出标准化核对表**

对应语句：`clean_df.to_csv(CLEAN_FILE, index=False)`

**语法和执行含义：** 将 clean_df 写到 CLEAN_FILE，仍不保存索引；十六列包括原始和标准金额。

**为什么这样写：** 供人工复查清洗效果。两个 CSV 写入分别执行，不属于后面 SQLite 的事务。

---

**第 8—9 行｜显示两个导出位置**

对应语句：`print(f"Import snapshot saved: {DATA_FILE}") ⏐ print(f"Clean audit file saved: {CLEAN_FILE}")`

**语法和执行含义：** 两行 f-string 分别插入实际 Path 值并输出。

**为什么这样写：** 定位生成的核对材料；CSV 保存完成不代表数据库导入完成。

---

## Cell 09: Connect to SQLite and Create Tables

### 完整代码

```python
# Cell 09: Connect to SQLite and Create Tables

database = DatabaseManager(DATABASE_FILE)
database.connect()
database.create_tables()
print("Database connected and tables are available.")
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 09: Connect to SQLite and Create Tables`

**语法和执行含义：** 井号 # 后面是注释，Python 不把它作为操作执行。Cell 编号表示本模块中的格子编号，不是 Notebook 的执行次数。

**为什么这样写：** 便于复制和定位每一格；保留英文标题，代码内不混入中文说明。

---

**第 3 行｜创建数据库对象**

对应语句：`database = DatabaseManager(DATABASE_FILE)`

**语法和执行含义：** DatabaseManager 是类，圆括号调用会创建实例并执行 __init__；DATABASE_FILE 传给 database_path，结果赋给 database。

**为什么这样写：** 此刻仅有路径和 None 初始连接，尚未打开数据库。

---

**第 4 行｜主动调用连接方法**

对应语句：`database.connect()`

**语法和执行含义：** database.connect() 的 self 由 Python 自动提供为 database。执行后对象保存实际连接。

**为什么这样写：** 不需要写 database.connect(database)，也不需要每个方法重复传路径。

---

**第 5 行｜通过已有连接建表**

对应语句：`database.create_tables()`

**语法和执行含义：** 调用 create_tables 执行 Cell 05 定义的三条建表 SQL；已有同名表保留。

**为什么这样写：** 新库先建结构再写数据，建表成功不说明表里已有年度财务行。

---

**第 6 行｜显示准备完成**

对应语句：`print("Database connected and tables are available.")`

**语法和执行含义：** 只有前面连接与建表调用成功，才输出本行。

**为什么这样写：** 确认可继续执行 Cell 10，年度记录在下一格保存。

---

## Cell 10: Write the Accepted Records in One Transaction

### 完整代码

```python
# Cell 10: Write the Accepted Records in One Transaction

write_counts = database.save_data(config, clean_df)
print(f"Inserted records: {write_counts['inserted']}")
print(f"Updated records: {write_counts['updated']}")
print(f"Unchanged records: {write_counts['unchanged']}")
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 10: Write the Accepted Records in One Transaction`

**语法和执行含义：** 井号 # 后面是注释，Python 不把它作为操作执行。Cell 编号表示本模块中的格子编号，不是 Notebook 的执行次数。

**为什么这样写：** 便于复制和定位每一格；保留英文标题，代码内不混入中文说明。

---

**第 3 行｜保存本次接受的数据**

对应语句：`write_counts = database.save_data(config, clean_df)`

**语法和执行含义：** 调用对象 save_data，传入 config 与 clean_df，内部事务成功后返回计数字典，赋给 write_counts。

**为什么这样写：** 这个调用真正写入分部定义和年度财务；必须先有本次成功检查与可用连接。

---

**第 4 行｜显示新增数**

对应语句：`print(f"Inserted records: {write_counts['inserted']}")`

**语法和执行含义：** write_counts['inserted'] 通过键取整数，嵌入 f-string。内层单引号与外层双引号清楚区分字符串边界。

**为什么这样写：** 当前新库通常为十二，已有相同数据时可以为零。

---

**第 5 行｜显示更新数**

对应语句：`print(f"Updated records: {write_counts['updated']}")`

**语法和执行含义：** 读取 updated 计数并输出。

**为什么这样写：** 相同身份任一保存字段变化会计为更新，包括来源和访问日期，不只金额。

---

**第 6 行｜显示不变数**

对应语句：`print(f"Unchanged records: {write_counts['unchanged']}")`

**语法和执行含义：** 读取 unchanged 计数并输出。

**为什么这样写：** 同一数据重复运行通常显示十二行不变，说明避免了重复插入。三个计数不是全表历史行数。

---

## Cell 11: Read Back and Verify the Persisted Records

### 完整代码

```python
# Cell 11: Read Back and Verify the Persisted Records

def verify_database_copy(clean_df, financial_df):
    """Compare every imported field after reading the persisted records back."""
    left = clean_df.sort_values(["unit_id", "fiscal_year"]).reset_index(drop=True)
    right = financial_df.sort_values(["unit_id", "fiscal_year"]).reset_index(drop=True)
    if len(left) != len(right):
        raise ValueError("Database row count does not match the accepted records.")
    for column in left.columns:
        if column not in right.columns or left[column].tolist() != right[column].tolist():
            raise ValueError(f"Database values differ from accepted records: {column}")

financial_df = database.read_selected_records(config)
validate_records(financial_df, config)
verify_database_copy(clean_df, financial_df)

table_counts = database.get_table_counts()
print("Database read-back verification passed.")
print(f"Selected financial records: {len(financial_df)}")
for table in table_counts:
    print(f"{table}: {table_counts[table]} rows")
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 11: Read Back and Verify the Persisted Records`

**语法和执行含义：** 井号 # 后面是注释，Python 不把它作为操作执行。Cell 编号表示本模块中的格子编号，不是 Notebook 的执行次数。

**为什么这样写：** 便于复制和定位每一格；保留英文标题，代码内不混入中文说明。

---

**第 3—4 行｜定义逐字段核对函数**

对应语句：`def verify_database_copy(clean_df, financial_df): ⏐ """Compare every imported field after reading the persisted records back."""`

**语法和执行含义：** 两个输入分别是本次接受的 clean_df 和数据库查询的 financial_df；说明字符串仅描述用途。通过返回 None，失败 raise。

**为什么这样写：** 证明保存后的字段内容与接受数据一致，不能只核对行数或金额合计。

---

**第 5 行｜整理左侧比较表**

对应语句：`left = clean_df.sort_values(["unit_id", "fiscal_year"]).reset_index(drop=True)`

**语法和执行含义：** 对 clean_df 按分部、财年排序，再 reset_index(drop=True)，赋给 left。

**为什么这样写：** 两边同一身份必须对应同一行位置，避免因排序不同误报差异。

---

**第 6 行｜同样整理右侧比较表**

对应语句：`right = financial_df.sort_values(["unit_id", "fiscal_year"]).reset_index(drop=True)`

**语法和执行含义：** 对 financial_df 采用完全相同的排序和索引规则，赋给 right。

**为什么这样写：** 这些调用返回新的表，没有用 inplace 修改传入数据。

---

**第 7—8 行｜先比较行数**

对应语句：`if len(left) != len(right): ⏐ raise ValueError("Database row count does not match the accepted records.")`

**语法和执行含义：** len 取两表行数，不相等则 raise。

**为什么这样写：** 数量不同已经证明保存或查询不完整，无需继续逐列比较。

---

**第 9 行｜逐列核对所有接受字段**

对应语句：`for column in left.columns:`

**语法和执行含义：** 遍历 left.columns 的列名，将当前列名赋给 column。

**为什么这样写：** 以本次导入的全部字段为核对范围，包括来源、日期和原始文本。

---

**第 10—11 行｜检查列存在且逐值相等**

对应语句：`if column not in right.columns or left[column].tolist() != right[column].tolist(): ⏐ raise ValueError(f"Database values differ from accepted records: {column}")`

**语法和执行含义：** or 左边检查右表是否有该列；缺列时短路不再访问它。列存在则 tolist 转成普通列表，!= 检查对应位置值差异，失败 raise 显示列名。

**为什么这样写：** 允许右表有额外字段，但左表所有字段必须保留。数值 7033 与 7033.0 可比较相等，这不是 dtype 的严格一致检查。

---

**第 13 行｜从数据库真正查询**

对应语句：`financial_df = database.read_selected_records(config)`

**语法和执行含义：** 调用 read_selected_records，内部 SQL 按配置筛选并 JOIN 分部名称，pandas 将结果变为新 DataFrame，赋给 financial_df。

**为什么这样写：** 这份数据来自已提交数据库，不是内存 clean_df 的别名。

---

**第 14 行｜检查查询覆盖及字段规则**

对应语句：`validate_records(financial_df, config)`

**语法和执行含义：** 对 financial_df 再调用 validate_records。

**为什么这样写：** 确保选中的实际数据仍符合当前配置，发现查询漏年或身份错误。

---

**第 15 行｜比较保存前后的全部字段**

对应语句：`verify_database_copy(clean_df, financial_df)`

**语法和执行含义：** 调用刚定义的 verify_database_copy，以 clean_df 和 financial_df 为左右输入，不接收返回值。

**为什么这样写：** 覆盖正确仍可能值写错，此检查证明本次保存内容逐项一致。

---

**第 17 行｜查询全表计数**

对应语句：`table_counts = database.get_table_counts()`

**语法和执行含义：** get_table_counts 返回三张表名到行数的字典，赋给 table_counts。

**为什么这样写：** 它数完整表，当前研究选中行数另看 len(financial_df)；未来存其他研究时全表可更大。

---

**第 18 行｜显示回读核对通过**

对应语句：`print("Database read-back verification passed.")`

**语法和执行含义：** 只有查询与两项检查成功后，才执行这个 print。

**为什么这样写：** 结合真实查询而不是重复打印 clean_df，确认数据库保存结果。

---

**第 19 行｜显示当前选中行数**

对应语句：`print(f"Selected financial records: {len(financial_df)}")`

**语法和执行含义：** len(financial_df) 取配置所选查询行数。

**为什么这样写：** 当前应为十二，与三张全表数量不是同一个统计。

---

**第 20—21 行｜依次显示三表数量**

对应语句：`for table in table_counts: ⏐ print(f"{table}: {table_counts[table]} rows")`

**语法和执行含义：** 遍历 table_counts 的键，再用同一个键查询数量；第 21 行缩进在循环里，因此打印三次。

**为什么这样写：** 新库导入后常见为分部表二、财务表十二、指标表零。指标尚未计算，空指标表正常。

---

## Cell 12: Close the Connection and Prepare the Next Module

### 完整代码

```python
# Cell 12: Close the Connection and Prepare the Next Module

database.close()
print("Database connection closed.")
print("Module 02 completed.")
print(f"Persistent database: {DATABASE_FILE}")
print("Next: query financial_records, join study periods and calculate metrics.")
print("No sales growth, operating margin or sales index has been calculated in Module 02.")
```

### 逐句解释

**第 1 行｜英文 cell 注释标题**

对应语句：`# Cell 12: Close the Connection and Prepare the Next Module`

**语法和执行含义：** 井号 # 后面是注释，Python 不把它作为操作执行。Cell 编号表示本模块中的格子编号，不是 Notebook 的执行次数。

**为什么这样写：** 便于复制和定位每一格；保留英文标题，代码内不混入中文说明。

---

**第 3 行｜关闭对象保存的连接**

对应语句：`database.close()`

**语法和执行含义：** 调用 DatabaseManager.close，内部关闭实际连接并将属性复原为 None。

**为什么这样写：** 释放连接资源，已提交文件保留，financial_df 仍是可用的内存表。

---

**第 4—5 行｜显示关闭与模块完成**

对应语句：`print("Database connection closed.") ⏐ print("Module 02 completed.")`

**语法和执行含义：** 两句 print 输出状态文字，不执行额外保存或计算。

**为什么这样写：** 这些提示依赖前面的流程真正成功，不能靠单独运行 print 来证明完成。

---

**第 6 行｜显示持久化文件位置**

对应语句：`print(f"Persistent database: {DATABASE_FILE}")`

**语法和执行含义：** f-string 将 DATABASE_FILE 嵌入提示，指出磁盘文件在哪里。

**为什么这样写：** kernel 重启后可以用这个路径重新连接，不依赖现有内存变量。

---

**第 7 行｜说明下一模块读取步骤**

对应语句：`print("Next: query financial_records, join study periods and calculate metrics.")`

**语法和执行含义：** 输出下一步是查询基础财务表、加入研究时期并计算指标的英文提示。

**为什么这样写：** 这里只交接流程，实际 SQL 与指标计算由下一模块运行。

---

**第 8 行｜说明当前尚未计算指标**

对应语句：`print("No sales growth, operating margin or sales index has been calculated in Module 02.")`

**语法和执行含义：** 输出本模块没有计算销售增长、营业利润率和销售指数的英文提示。

**为什么这样写：** 明确数据库有基础数据和结果表结构，不代表三项指标已有值。

---

## 执行顺序和学习提醒

Cell 01—02 准备工具、配置和路径；Cell 03—05 定义函数和类；Cell 06—12 实际读取、清洗、保存、查询与关闭。函数定义成功但没有输出很正常，函数体要等后面调用才执行。

输入来自项目 data/raw/ 的两份原始 CSV。raw_df 是十二行十四列；clean_df 新增两个标准金额列，为十二行十六列；financial_df 是数据库查询恢复的十二行十六列。净销售额和营业利润统一为百万美元。来源金额、单位和出处保留，具体官方来源见 [source_notes.md](source_notes.md)。

学习时先理解赋值、字典查询、对象属性、函数调用，再看集合和循环，最后理解 SQL 参数及事务。不要跳过失败的 cell 继续保存，因为 kernel 中可能还保留旧变量。重启 kernel 后重新运行第一模块和第二模块定义格。
