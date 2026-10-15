# Module 02: Data and Database Management

本 guide 将中文说明、完整英文代码、每个函数和方法的详细讲解合在一起。配套 Notebook 有 **12 个 code cells**，每格第一行是英文 comment 小标题。定义函数的格通常没有输出，调用它们的格才会执行工作。

本模块沿用 2019 基期：Amazon North America 2019—2024，与 Walmart U.S. FY2020—FY2025 近似配对，共 12 条分部年度记录。2019 的疫情前参照和比较阶段仍属于 Module 01 配置；本模块保存报告财年和日期，不在基础财务表中写死分析年度或疫情阶段。

数据来自四份免费官方年报的分部表，由本次工作核对后人工转录为随包附带的两份原始 CSV。完整官方财报链接、采用版本、原始数值、日期推导依据和金额单位见 [source_notes.md](source_notes.md)。Notebook 读取这些本地 CSV，不假装自动抓取了分部数据。未附完整官方 HTML 快照；可在浏览器中从原始链接另行保存，不影响本模块运行。

## 使用前准备

建议解压完整包并保持 module_01、module_02、data 三个同级文件夹。打开 module_02/module_02_data_and_database_management.ipynb，将 kernel 工作目录设为 module_02，重启后按 Cell 01—12 顺序运行。Module 01 的 study_config.py 用于复用其配置类及读取函数；即使采用本 Notebook 的完整代码，仍需要这个配套文件和 study.json。

Cell 02 会依次检查当前工作目录的 module_01 子文件夹、上一级的 module_01 文件夹，以及当前目录本身，要求 study_config.py 和 study.json 同时存在。因此完整包既可以从项目根目录的总 Notebook 运行，也可以从 module_02 的独立 Notebook 运行。不要只复制 Notebook 而遗漏配套文件。若把 study.json 移到项目根目录，JSON 中的数据路径也应改成 data/...，才能继续指向项目内的数据。数据库和数据导出位置始终以 JSON 所在位置为基准；先核对 Cell 02 打印的路径。

只有 pandas 是本模块需要另行安装的第三方包。若当前 kernel 没有 pandas，可以单独增加一个安装格运行 `%pip install pandas`，安装后重启 kernel。其余使用 Python 标准库；SQLite 无需独立服务或付费账号。环境需求为 Python 3.10 或更高版本。

## 本模块的具体数据流

官方分部表 → 人工核对并转录到 data/raw/ 两份源 CSV → pandas 读取为 amazon_raw_df、walmart_raw_df → concat 成 raw_df → 普通函数生成 clean_df 并检查 → 导出组合快照与清洗核对 CSV → DatabaseManager 写入 SQLite → SQL 查询为 financial_df → 逐字段回读核对。

通用函数和类放在 Cell 03—05，研究配置和源文件映射集中在 Cell 02，执行流程在 Cell 06—12。Cell 06 的两家 DataFrame 名称是当前案例的展示别名；换内容时同步调整文件映射和这些别名，通用清洗、检查和 SQL 方法不需要判断公司名称。

后续指标采用 USD millions 的净销售额和营业利润数值列。Walmart 的净销售额不等同于包含会员及其他收入的总收入；Amazon 2022 营业亏损为合法负数。代码检查结构、内部一致性和覆盖，人工核对的来源说明负责解释实际业务口径。

SQL 建表与存取内容较长，是因为完整列出来源与字段；没有 ORM、继承、装饰器、dataclass、复杂类型标注或 lambda。后面的讲解按 SQL 语句和方法分段，不要求一次记住整个类。

## Cell 01: Import Libraries

目的：导入 pandas、SQLite 和所需标准库。这里只准备工具，尚未读入财务数据。

预期结果：通常没有输出。若提示 pandas 未安装，在当前 Notebook 的 kernel 环境安装 pandas，再重新运行本格。

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

### 构建思路：先准备工具，再处理内容

`math` 提供 `isfinite`，检查数值是不是有限数，拒绝无穷大和 NaN。`re` 提供正则表达式，用于检查金额字符串是不是允许的格式。`sqlite3` 是 Python 的 SQLite 接口，负责连接和执行 SQL。

`Path` 表示文件路径，让目录拼接和建立更直观；`urlparse` 拆分来源 URL。`pandas as pd` 给 pandas 起一个简短别名，后面所有 `pd.read_csv`、`pd.concat` 等调用都通过这个别名进行。`sys` 用于设置配套 Python 文件的搜索位置，不负责采集数据。

这一格没有研究年份、公司名称或财务数字。工具导入只执行一次，其余格复用这些工具。Notebook 显示某个导入为灰色通常只是尚未看到它的使用位置，不能据此判断代码运行失败。

## Cell 02: Load Study Configuration and Set Input Paths

目的：复用 Module 01 的配置读取函数，以 JSON 为研究内容入口。路径和原始文件映射集中在本格；通用清洗与数据库代码放在后面的定义格。

预期结果：显示 12 条计划记录、2019 基期及文件路径。数据库此时尚未连接。

```python
# Cell 02: Load Study Configuration and Set Input Paths

candidate_directories = [
    Path("module_01"),
    Path("../module_01"),
    Path("."),
]
MODULE01_DIRECTORY = None
for directory in candidate_directories:
    if (directory / "study_config.py").is_file() and (directory / "study.json").is_file():
        MODULE01_DIRECTORY = directory.resolve()
        break

if MODULE01_DIRECTORY is None:
    raise FileNotFoundError(
        f"Cannot find study_config.py and study.json together. "
        f"Current working directory: {Path.cwd()}. "
        "Extract the full package and keep module_01, module_02 and data together."
    )

CONFIG_PATH = MODULE01_DIRECTORY / "study.json"
sys.path.insert(0, str(MODULE01_DIRECTORY))
from study_config import load_study_config

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

### 构建思路：复用第一模块，把变化内容集中起来

**输入：** Module 01 的 `study.json` 和 `study_config.py` 文件。

**输出：** `config` 对象、三个主要数据路径，以及原始 CSV 文件映射 `RAW_FILES`。

`candidate_directories` 是普通列表，按顺序列出三个常见位置：当前工作目录里的 `module_01`、上一级里的 `module_01`，以及当前目录本身。`../` 表示上一级，`.` 表示当前目录。Notebook 的工作目录由 kernel 决定，不一定等于 Notebook 文件所在目录；`Path.cwd()` 可以查看实际位置。

`MODULE01_DIRECTORY = None` 表示还没有找到位置。`for directory in candidate_directories` 依次检查列表。`directory / "study_config.py"` 是 Path 拼接操作，不是数值除法；`.is_file()` 检查该路径是否为已有文件。`and` 要求 Python 配套文件和 JSON 配置同时存在。找到后，`.resolve()` 将位置整理成绝对路径，`break` 结束循环，避免继续选用其他目录。

`if MODULE01_DIRECTORY is None` 表示三个位置都没有找到这两个文件。此时 `raise FileNotFoundError(...)` 停止执行，提示实际工作目录和完整包解压方式。它不会创建一个空配置来掩盖问题，也不会在整台电脑上搜索。若文件在其他地方，可把它所在的准确目录加入候选列表。特别注意：第一模块的 `.ipynb` 文件不等于 `study_config.py`，执行 Notebook 不会自动生成同名 Python 文件。

`sys.path.insert(0, str(MODULE01_DIRECTORY))` 将目录放到 Python 的模块搜索列表最前面。`str` 把 Path 转为文本，`0` 表示第一个位置。随后 `from study_config import load_study_config` 从该目录下的配套文件导入普通函数。这里只改当前 Python 进程的搜索列表，不改变系统环境变量或文件。

为什么复用已有函数，而不是再定义一个 StudyConfig？两个模块必须使用同一套配置规则。`load_study_config` 会读取 JSON、创建对象并调用 Module 01 的检查；如果配置错误，会在处理数据前停止。这个调用不会自动读取财务 CSV。

`paths = config.resolve_paths(CONFIG_PATH)` 让 CSV、数据库及结果路径以 JSON 所在位置为基准。`DATA_FILE` 和 `DATABASE_FILE` 分别取出配置提供的导入快照和数据库路径。`DATA_FILE.parent` 是导入快照所在目录；在其下面安排 `raw` 和 `clean`，这样数据位置变化时不必修改通用函数。

`RAW_FILES` 是普通字典：键为稳定的 `unit_id`，值为来源 CSV 的路径。它是本次研究内容的一部分。更换对象后，JSON、对应 CSV、稳定标识和这份映射必须一致；不能仅修改显示名称却继续使用原公司的数字。

五行 `print` 是人工核对入口。新增的第一行显示 kernel 工作目录。`config.index_base_year` 只是显示保存的 2019 设置，并没有在这里计算销售指数。若打印路径不符合你的项目目录安排，先修改配置和本格，再开始读入数据。

## Cell 03: Define Cleaning Functions

目的：定义原始字段、单位换算规则，以及金额解析和标准化两个普通函数。保留原始金额文本，同时增加统一以 USD millions 表示的数值列。

预期结果：通常没有输出。只定义函数，Cell 07 才会调用。

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

### 构建思路：保留原始披露，再添加统一数值

这一格先定义字段和换算规则，再定义两个普通函数。函数不知道当前研究的是哪家公司；它们只要求输入具有相同的字段结构。

#### RAW_COLUMNS：明确每条记录应该包含什么

列表中的一项就是一个列名，顺序也明确下来。`unit_id` 表示分部身份；公司和分部名称供核对显示；`fiscal_year`、`period_start` 和 `period_end` 记录真实报告期间。

`net_sales_raw` 与 `operating_income_raw` 是报表金额文本，包括千位逗号和亏损括号。`reported_currency` 是币种，`reported_unit` 是金额数量级。来源 URL、章节和年度列、访问日期、日期依据使数值可以追溯。

本次 `period_start` 根据年报明确的年度日历推导，并用 `date_basis` 标明，不能把推导值伪装成原表单独披露的起始日期。每条记录仍保留真实结束日，不把两家公司强行改成相同日期。

#### UNIT_MULTIPLIERS：规定换算到 USD millions 的比例

这是普通字典。原始为整美元 `units` 时乘 0.000001，百万美元 `millions` 时乘 1，十亿美元 `billions` 时乘 1000。本次所有原表都是 USD millions，因此使用乘数 1。

这是数量级换算，不是汇率换算。本版不支持非 USD 数据，不会自动用汇率把其他币种变成美元。换算规则属于框架能力，不属于特定公司的分支。

#### RECORD_COLUMNS：说明财务表保存哪些字段

数据库财务表保存分部标识、报告财年、原始值、标准值和来源。公司及分部名称放在 `business_units` 表中，不在每年财务记录里重复保存；查询时通过 JOIN 取回。这是基础数据存储的分工。

列表最前面两项为 `unit_id` 和 `fiscal_year`，构成唯一键。后面的字段可以更新；Cell 05 会用这个固定顺序组织 SQL 参数。

### 函数 1：parse_amount(value)

**输入：** 一条原始金额文本，例如 `"170,773"` 或 `"(2,847)"`。

**输出：** 一个普通浮点数；无法解释的金额直接报错。函数不改变单位。

**调用时机：** `standardize_records` 逐行处理金额时调用，两项金额各调用一次。

`str(value).strip().replace(",", "")` 先变成文本、去除两端空白，再移除千位逗号。因此 `"170,773"` 变成 `"170773"`，原来的输入列仍由调用方保留。

`startswith("(")` 和 `endswith(")")` 判断括号是否成对包围金额。如果成立，用 `text[1:-1]` 取掉最外面两个字符，再在前面加负号；`"(2,847)"` 于是转为 `"-2847"`。

`re.fullmatch` 检查整个字符串，而不是其中一小段。规则允许可选负号、数字和可选小数部分：`-?` 表示负号可以没有；`\d+` 表示至少一个数字；后面的小数部分也可以没有。空白、破折号、文字和损坏的括号不会被当成零。

`is None` 表示匹配失败。`raise ValueError` 中的英文提示保留原输入，方便回到 CSV 找到问题。

`pd.to_numeric(..., errors="raise")` 把通过格式检查的文本变成数值，再用 `float` 统一输出类型。`math.isfinite` 再拒绝极端值导致的无穷大。最后 `return amount` 交回数值。

为什么不直接删掉所有非数字字符？这样会丢掉亏损负号，也可能把错误文字中的数字拼成一个看似合法的金额。本函数只处理明确支持的格式。

### 函数 2：standardize_records(raw_df)

**输入：** 包含 `RAW_COLUMNS` 的原始 DataFrame。

**输出：** 新的 `clean_df`，保留所有原始字段，另加 `net_sales_usd_m` 和 `operating_income_usd_m` 两列。

**调用时机：** Cell 07；它先于 `validate_records` 执行。

第一段用 `for column in RAW_COLUMNS` 检查所需列是否存在。缺失列就停止，而不是创建一列空值继续导入。

`raw_df[RAW_COLUMNS].copy()` 选择规定列并复制。原始 `raw_df` 不被修改，多余列也不会不经解释地进入数据库。随后对每列检查缺失值，转为文本并去除两端空白，再拒绝空字符串。`isna().any()` 表示这一列只要存在真正的缺失值就触发；`.eq("").any()` 检查清理后的空文本。

`pd.to_numeric` 解析财年。`between(1900, 2100).all()` 要求每个年份在范围内，`eq(years.round()).all()` 要求数值等于四舍五入后的自己，因此 2019.5 不会被直接截断成 2019。通过后再用 `.astype(int)` 转为整数。

日期列用 `pd.to_datetime` 按年-月-日解析，错误立即报错。`.dt.strftime("%Y-%m-%d")` 又将日期统一为 ISO 文本供 CSV 与 SQLite 保存；它不修改日期覆盖的真实期间。使用这个固定格式后，合法日期文本可按年月日顺序比较。

`sales_values = []` 和 `income_values = []` 准备两个空列表。`clean_df.to_dict("records")` 把每一行转为普通字典组成的列表，方便用你熟悉的循环取出字段。

每轮先确认美元和支持的数量级，再从换算字典取出 `multiplier`。`parse_amount(...) * multiplier` 将原始金额换成百万美元，并用 `.append` 按行存入列表。没有公司名称判断，没有把每个财年统一加 1。

将两份列表分别赋给两个新列后，`sort_values(["unit_id", "fiscal_year"])` 按分部和财年排序。`.reset_index(drop=True)` 让行索引重新从 0 开始，`drop=True` 避免把旧索引作为一列保存。最后返回整理好的 DataFrame。

为什么同时保留原始和标准金额？源文本用于审查，数值用于计算；只有标准化值会失去逗号、括号或原始单位线索，只有文本又无法直接计算。

## Cell 04: Define Record Validation

目的：定义检查函数，确保分部身份、日期、金额、来源格式以及研究所需年度覆盖一致。检查规则使用 config，不把两家公司的名称或年份写死。

预期结果：通常没有输出。遇到错误时停止导入，不填零，也不悄悄删掉问题行。

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

### 函数 3：validate_records(clean_df, config)

**输入：** 经过标准化的记录，以及第一模块的配置对象。

**输出：** 通过时没有专门返回值，即 Python 的 `None`；失败时抛出 `ValueError`。不修改输入数据。

**调用时机：** Cell 07 入库前，以及 Cell 11 数据库回读后。标准化检查“能否正确解释”，本函数检查“是否符合当前研究的要求”。

第一段确认配置也使用 USD，并用 `duplicated(["unit_id", "fiscal_year"]).any()` 检查同一分部财年是否出现两次。同一数字重复两行也不能悄悄去重，因为它可能来自不同来源版本，需要先明确采用哪一版。

`units_by_id` 是用稳定标识查分部配置的字典；`expected_keys` 是集合。遍历配置的时期和分部，把 `(unit_id, fiscal_year)` 这样的二元组加入集合。集合适合比较覆盖，不受输入行顺序影响。

例如 `("amazon_north_america", 2019)` 与 `("walmart_us", 2020)` 是不同键，虽然它们映射到同一个分析年度。函数没有写死 12，所需键完全由配置决定。

逐行检查时，先记录实际键，再检查标识是否已配置，随后核对公司和分部名称。名字也检查，是为了发现复制 CSV 后只改了部分信息的错误；名字不是数据库的匹配主键。

币种必须与配置一致，开始日必须早于结束日。标准化已保证 ISO 日期有效，所以字符串比较能表达日期顺序。这里不会证明人工填写的日期就是财报的日期，仍需来源核对和 `date_basis`。

对两个标准金额检查有限数值，再要求销售额大于零，因为后续利润率和销售指数需要合法分母。营业利润可以为零或负数，没有要求其大于零，因此 Amazon 2022 的亏损可以通过。

`urlparse` 只检查来源地址的协议和主机名；它不会联网证明来源内容正确。章节、日期依据和访问日期必须有内容，便于人工追溯。当前函数接收已标准化记录，标准化函数已检查这些原始字段完整。

最后比较 `actual_keys` 与 `expected_keys`。集合减法得到缺少或多出的键，用 `sorted` 整理提示顺序。即使总行数恰好 12，只要错用了一个财年也会失败。还核对对象方法计算的计划数量，避免与配置不一致。

为什么不把不合格行删除？一旦丢掉问题年份，比较期间就变了。这里把错误暴露出来，让你回到源文件检查，再重新运行。

## Cell 05: Define the Database Manager

目的：建立一个简单类管理数据库连接、建表、写入、查询、计数与关闭。金额处理仍由普通函数负责；类不包含特定公司的清洗分支。

预期结果：通常没有输出。此时只是定义类，尚未创建数据库对象。

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

### 构建思路：用一个对象管理有状态的数据库连接

普通清洗函数接收 DataFrame、返回 DataFrame，不需要长期保存状态。数据库则需要反复使用同一连接，因此用 `DatabaseManager` 类保存连接并提供清楚的方法接口。

### 方法 1：__init__(self, database_path)

**输入：** SQLite 文件路径。**输出：** 初始化好的对象，方法本身不返回数据库连接。

`self.database_path = Path(database_path)` 保存文件位置；`self.connection = None` 表示尚未连接。`None` 是 Python 的“没有值”，不是字符串 `"None"`。

创建 `database = DatabaseManager(DATABASE_FILE)` 时会自动执行这个方法，但此时不创建文件。把对象创建和连接分开，是为了让 Cell 09 清楚展示两个步骤。

### 方法 2：connect(self)

**输入：** 对象自身保存的路径。**输出：** 无专门返回值，但设置 `self.connection`。

只有连接为 `None` 时才建立新连接，避免同一对象重复打开而丢掉旧连接。`.parent.mkdir(parents=True, exist_ok=True)` 建立父目录，包括必要的上层目录；已存在目录不会报错。

`sqlite3.connect(str(self.database_path))` 打开已有文件，或在不存在时创建新的 SQLite 文件。`PRAGMA foreign_keys = ON` 为当前连接开启外键约束，使财务表中的分部标识必须存在于分部表中。

### 方法 3：create_tables(self)

**输入：** 已连接的对象。**输出：** 数据库中三张表可用。

`executescript` 一次执行多条建表 SQL。三引号让多行 SQL 保持实际换行；它是普通 Python 字符串，不是新语法框架。

`CREATE TABLE IF NOT EXISTS` 表示表不存在时建立，已存在时保留。它不删除已有记录，也不会自动迁移一个结构不兼容的旧表；本项目首版数据库采用这里定义的结构。

SQL 中 `TEXT` 保存文字，`INTEGER` 保存整数，`REAL` 保存数值。`NOT NULL` 要求字段不能为空。`PRIMARY KEY` 规定身份，`FOREIGN KEY` 规定记录之间的关系，`CHECK` 规定必须满足的条件。

**business_units 表：** 一行是一个分部，用 `unit_id` 作为主键，保存名称、股票代码、币种、口径和来源入口。它不保存每年销售额。

**financial_records 表：** 一行是一个分部财年，联合主键为 `(unit_id, fiscal_year)`。保存原始文本、原始单位、标准金额、实际日期和来源。销售额约束为正，营业利润没有正数约束，所以亏损可存入。日期顺序也在 SQL 中再检查一次。

**metric_results 表：** 现在只建立结构，不写计算结果。组合主键包含研究标识、配置签名、分部、分析年度和指标名，区分不同研究设置。`metric_value` 没有 `NOT NULL`，将来可用 SQL 的 NULL 表示缺失同比；不能把未计算值自动写成零。配置签名在第三模块生成，这里只预留文字字段。

为什么基础表不保存 `analysis_year` 或 `comparison_stage`？同一个报告财年可以用于不同研究，如何配对和分组属于配置，不应该永久绑在财务记录中。

### 方法 4：save_data(self, config, clean_df)

**输入：** 配置对象和已经检查通过的 DataFrame。**输出：** 包含 inserted、updated、unchanged 的普通计数字典，仅统计年度财务记录。

调用前由 Cell 07 完成财务检查。本方法负责存取，数据库约束再保护主键、外键、必填字段和销售额分母。

**第一段，准备固定 SQL 字段和占位符。** `", ".join(RECORD_COLUMNS)` 把框架规定的列名连接起来。`["?"] * len(RECORD_COLUMNS)` 生成与列数相等的问号列表，再用逗号连接。`?` 是 SQLite 参数占位符，真实数值通过第二个参数传入，不把公司名称或金额直接拼进 SQL。

`RECORD_COLUMNS[2:]` 跳过前两个主键字段。循环生成这些普通字段的 `column = ?` 更新表达式。字段名来自代码的固定列表，用户数据只进入参数；不要将外部输入用作表名或列名。

**第二段，开始事务并保存分部定义。** `with self.connection:` 管理这一批写入的提交与回滚。全部成功时提交，有异常时回滚已执行的写入。它不会自动关闭连接，Cell 12 才负责关闭。

`unit_values` 是一个元组，按 SQL 字段顺序准备值。`"\n".join(...)` 把多条口径说明或来源链接保存为换行文本，避免为这两个小列表增加额外表。

`SELECT ... WHERE unit_id = ?` 查询当前分部是否存在。`.fetchone()` 取一行，找不到就得到 `None`。`(unit["unit_id"],)` 是单元素元组，尾部逗号不可随意去掉。

不存在时执行 `INSERT`；存在且字段发生变化时执行 `UPDATE`。`unit_values + (unit_id,)` 拼接参数元组，使标识处于 SQL 最后一个问号的位置。已有相同内容时不重复写入。

口径或来源等分部定义改变时，删除该分部之前保存的指标，使它们需要重新计算。更换实际公司时应使用对应的新 `unit_id`，而不是把另一家公司的身份覆盖在原标识上。

**第三段，按分部财年保存每条财务记录。** `to_dict("records")` 将行变成字典。循环按 `RECORD_COLUMNS` 顺序取值，再转为元组。这个顺序必须与 SQL 中的列顺序一致。

`key` 是 `(unit_id, fiscal_year)`。查询相同键后，有三种情况：不存在就插入；存在但整组字段不同就更新；整组字段相同则记为 unchanged。即使你重复运行，也不会为同一键多插一行。

更新时 `values[2:] + key` 先提供非主键字段的新值，再提供 WHERE 所需的两个键。两个键不被更新，记录身份保持稳定。

新增或更新基础记录后执行 `DELETE FROM metric_results WHERE unit_id = ?`。这是有意使该分部所有旧指标失效：某年销售变化可能影响次年同比，基期变化还可能影响全部销售指数。首版采用保守的整分部失效规则；相同数据重复导入不会删除指标。

这项删除只作用于派生指标，不删除原始财务记录。访问日期或来源字段发生变化也算明确更新，会触发相同失效规则；这是本版选择，避免旧结果继续混用不同采用版本。

最后退出 `with`，事务提交，再返回计数。`+= 1` 是把当前计数增加一。为什么使用事务？否则前五行成功、第六行失败时，会留下不完整导入；事务可以把这一批写入一起撤回。

### 方法 5：read_selected_records(self, config)

**输入：** 配置对象。**输出：** 当前研究所需的 `financial_df`。

先创建空列表 `frames`，逐个分部，从配置中收集需要的报告财年。年份来自配置映射，不是查询函数根据公司名称猜出来的。

`IN (?, ?, ...)` 表示在若干年份中选择，问号数与年份数一致。`parameters = [unit_id] + years` 首先传分部标识，再传财年列表。外部数据不直接插入 SQL 文本。

`FROM financial_records AS f` 为表起简短别名；`JOIN business_units AS b ON f.unit_id = b.unit_id` 用稳定标识连接分部定义，把公司和分部名称取回来。`f.*` 取所有财务字段；`ORDER BY` 排序，`WHERE` 规定当前查询范围。

`pd.read_sql_query(..., params=parameters)` 执行查询，并把查询结果生成 DataFrame。这里 DataFrame 来源是已保存的数据库，不是上一步内存变量的复制。

把各分部查询结果组合、排序并重置索引后返回。数据库可以保存别的研究记录，本方法只选配置要求的分部财年；Cell 11 会检查是否全部找到了。

### 方法 6：get_table_counts(self)

**输入：** 已连接的对象。**输出：** 三张表的全表行数。

循环的表名来自框架固定列表。`SELECT COUNT(*)` 数这一张表的全部记录，`.fetchone()` 返回单元素元组，`row[0]` 取出数量。

这个方法统计全表，不等于当前研究所选记录数；当前研究的数量另看 `len(financial_df)`。首次新建本项目数据库，应为 2、12、0。

### 方法 7：close(self)

**输入：** 对象保存的连接。**输出：** 关闭连接，属性改回 `None`。

仅在连接存在时调用 `.close()`，因此已经关闭后再调用一次不会重复关闭。文件及已提交记录仍在磁盘上；`financial_df` 已读入内存，也不会因连接关闭而消失。

若随后还需写入或查询，应重新调用 `.connect()`。Notebook 分格运行时，这个显式步骤比隐式自动管理更容易看清。

## Cell 06: Load Source CSV Files into DataFrames

目的：读取随包附带的人工转录 CSV；分别保留两家分部的 DataFrame，再组合为 raw_df。数值来自官方财报核对后的转录，读取过程不需要网络请求。

预期结果：两个原始 DataFrame 各 6 行，raw_df 共 12 行；Amazon 2022 营业亏损仍显示为 (2,847)。

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

### 构建思路：数据从源 CSV 来，不在通用代码中填写数字

`source_frames = {}` 准备字典。循环读取 `RAW_FILES` 的每个键，用该键取得路径；`pd.read_csv` 读取文件后，字典保存这一份 DataFrame。每个分部都有自己的来源输入，方便单独检查。

`dtype=str` 要求原始字段先按文本读入，保留金额里的逗号和括号。`keep_default_na=False` 不让 pandas 把特定文本自动识别成 NaN，空文本随后由我们的函数明确拒绝。不能因为读入参数保留文本就认定数据已标准化。

读取后立即检查文件是否有 `unit_id` 列，以及这一列所有值是否等于文件映射的键。前面的 `or` 采用短路判断：列不存在时就报错，不再访问不存在的列。这个检查能发现两份文件路径写反的情况，保证两家原始 DataFrame 的展示别名和实际分部一致。

`amazon_raw_df` 与 `walmart_raw_df` 是字典中两份原始 DataFrame 的展示别名。代码拿到的是真实转录数据，不是这里临时编造的演示数值。这两个名字不会影响清洗公式，换案例时可以对应改名或直接使用字典。

`list(source_frames.values())` 取出各份 DataFrame 并组成列表。`pd.concat(..., ignore_index=True)` 按行组合，生成新的 `raw_df`，行索引不沿用两份输入重复的 0—5。

`raw_df[[...]]` 选择四个关键列，`.to_string(index=False)` 生成易于打印核对的文本；`index=False` 不显示行索引。打印只负责展示，不保存文件，也不写数据库。

为什么不直接从官网用 `read_csv`？官网提供的不是我们要求的整齐 CSV 分部表。这个小样本先人工核对并转录，避免自动抓取错分部或错列。来源获取步骤与 pandas 读文件步骤要区分。

## Cell 07: Standardize and Validate the Financial Records

目的：调用前面定义的普通函数，把 raw_df 转为 clean_df，并按配置检查。只有本格全部通过，才继续保存和入库。

预期结果：显示检查通过与 12 条标准记录；Amazon 2022 营业利润为 -2847.0。

```python
# Cell 07: Standardize and Validate the Financial Records

clean_df = standardize_records(raw_df)
validate_records(clean_df, config)

print("Financial record checks passed.")
print(clean_df[["unit_id", "fiscal_year", "period_start", "period_end", "net_sales_usd_m", "operating_income_usd_m"]].to_string(index=False))
```

### 构建思路：先解释值，再检查研究要求

`clean_df = standardize_records(raw_df)` 取得函数返回的新 DataFrame；`validate_records(clean_df, config)` 检查它，但不把返回值赋给 clean_df，因为检查函数没有返回新的数据。

这两行顺序不能交换：原始金额是文本，先标准化后才适合检查有限值、销售额分母和整数财年。函数定义放在 Cell 03、04，这里只调用，因此能够清楚区分“工具”与“执行”。

只有两行都没有异常，程序才执行成功提示与表格打印。出现错误时，应回到转录 CSV 或配置修正，不要为了通过检查把亏损填零或把某年删掉。

输出中保留不同的实际日期：Amazon 2019 为 2019-01-01 至 2019-12-31，Walmart FY2020 为 2019-02-01 至 2020-01-31。它们是近似配对，日期差异不会被清洗函数抹平。

## Cell 08: Save the Import Snapshot and Clean Audit File

目的：保留组合导入快照和清洗核对文件，原始两份 CSV 不覆盖。CSV 是核对材料，后续分析以数据库查询为入口。

预期结果：创建 financial_data.csv 和 clean/financial_records.csv。重新运行会更新这两个导出文件，不会覆盖 raw/ 中的源文件。

```python
# Cell 08: Save the Import Snapshot and Clean Audit File

DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
CLEAN_FILE.parent.mkdir(parents=True, exist_ok=True)
raw_df.to_csv(DATA_FILE, index=False)
clean_df.to_csv(CLEAN_FILE, index=False)

print(f"Import snapshot saved: {DATA_FILE}")
print(f"Clean audit file saved: {CLEAN_FILE}")
```

### 构建思路：保留可以人工打开的审查材料

两个 `.mkdir` 确保导出目录存在；`parents=True` 建立缺少的父目录，`exist_ok=True` 允许目录已经存在。它们不会创建数据库连接。

`raw_df.to_csv(DATA_FILE, index=False)` 保存原始组合快照。`clean_df.to_csv(CLEAN_FILE, index=False)` 保存清洗结果，包括原始文本、来源和两个标准数值列。`index=False` 不把 pandas 行索引作为额外 CSV 列。

目录不同，职责也不同：raw/ 的两份输入保留人工转录记录；financial_data.csv 是本次组合输入的快照；clean/financial_records.csv 用于审查标准化结果。导出文件在重复运行时更新，但不回写两份原始源 CSV。

CSV 不是 SQL 数据库，也不负责唯一键约束。它便于查看来源和清洗过程，SQLite 则负责后续按研究对象和财年查询。

## Cell 09: Connect to SQLite and Create Tables

目的：创建 DatabaseManager 对象，连接配置所指定的 SQLite 文件，再建立三张核心表。建表不等于财务记录已写入。

预期结果：SQLite 文件存在，business_units、financial_records 与 metric_results 表可用。

```python
# Cell 09: Connect to SQLite and Create Tables

database = DatabaseManager(DATABASE_FILE)
database.connect()
database.create_tables()
print("Database connected and tables are available.")
```

### 构建思路：把对象创建、连接、建表明确写出来

`DatabaseManager(DATABASE_FILE)` 创建一个对象，并把配置中的路径传给 `__init__`。左边的 `database` 是你之后使用的对象变量。

`database.connect()` 调用对象方法，连接数据库；`database.create_tables()` 再建立三张表。调用时不用自己传 `self`，Python 会把 `database` 作为当前对象提供给方法。

为什么不直接在类定义格建表？定义类只是描述工具，执行格才对本次研究的路径产生实际操作。这样别人拿走这个类，不会在导入代码时就创建你的研究数据库。

在这里已有数据库文件并不代表年度数据已经写入。Cell 10 才负责写，Cell 11 负责读回来核对。

## Cell 10: Write the Accepted Records in One Transaction

目的：将分部定义和通过检查的年度记录写入数据库。已存在的相同记录保持不变；明确更新的记录会替换该键的字段，并使该分部的旧指标失效。

预期结果：新数据库首次插入 12 行；在相同配置和相同数据下重复运行，通常显示 0 插入、0 更新、12 行不变。

```python
# Cell 10: Write the Accepted Records in One Transaction

write_counts = database.save_data(config, clean_df)
print(f"Inserted records: {write_counts['inserted']}")
print(f"Updated records: {write_counts['updated']}")
print(f"Unchanged records: {write_counts['unchanged']}")
```

### 构建思路：让数据库对象接收检查过的数据

`database.save_data(config, clean_df)` 同时需要分部定义和年度数据。前者来自 JSON，后者来自标准化输入，两种内容分别保存到对应表。

返回的 `write_counts` 是普通字典。通过 `write_counts['inserted']` 等访问计数，在 f-string 中放进输出文字。本格计数只说明本次年度记录的处理情况，不计算销售增长或营业利润率。

完整包附带已运行生成的数据库，所以你首次打开该包后用同一数据运行，可能立即显示 12 行 unchanged。这是预期行为，不能由此误以为数据没有导入。若在一个新的数据库文件上运行，才显示 12 行 inserted。

如果一批写入有问题，`with self.connection` 会回滚整批写入，不保留半份更新。只有通过检查和写入才能继续回读；数据库成功写入也不能替代人工来源核对。

## Cell 11: Read Back and Verify the Persisted Records

目的：定义回读核对函数，通过 SQL 读取当前配置所选记录为 financial_df，再逐字段与 clean_df 比较。证明数据库确实保存了这些记录，而不只是打印过 DataFrame。

预期结果：当前研究回读 12 行；全新数据库有 2 条分部定义、12 条财务记录、0 条指标结果。已有其他研究时全表计数可以更多。

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

### 函数 4：verify_database_copy(clean_df, financial_df)

**输入：** 内存中检查通过的 DataFrame，以及数据库查询生成的 DataFrame。

**输出：** 通过时为 `None`，不通过时抛出错误。不修改数据库。

**调用时机：** Cell 11，查询后先按当前配置检查覆盖，再逐字段与本次导入核对。

两个输入先采用相同键排序，再重置索引，因此核对不受 SQL 返回行顺序影响。先比较行数，数量不一样立即停止。

遍历 `left.columns`，每一列都要求存在于回读结果；用 `.tolist()` 把列转换为普通列表，再比较每一行的值。不只核对行数或金额合计，因为错换某年仍可能保持合计不变。

Python 中 2847 和 2847.0 的数值比较相等，所以 SQLite REAL 回读与清洗后的数值可以一致；日期、URL、原始文本和分部名称仍须逐项相同。金额这里只做数量级换算，当前数据没有复杂浮点计算误差。

`financial_df = database.read_selected_records(config)` 真正从磁盘数据库取得选中记录。再调用 `validate_records` 能发现缺失年份或错误身份；`verify_database_copy` 能发现字段写错或读错。

`table_counts` 是全表计数字典，循环逐个打印。新数据库指标表为 0，因为第三模块还没有运行；如果以后第三模块已有结果，再运行第二模块且输入未变，指标可以保留，所以不强制把该表清空到零。

为什么回读不能只打印 `clean_df`？打印的仍是写入前内存变量，不能证明 SQLite 保存了什么。这里的第二份 DataFrame 必须由 `read_sql_query` 产生。

## Cell 12: Close the Connection and Prepare the Next Module

目的：关闭数据库连接，说明交付给第三模块的入口与职责。financial_df 仍在内存中，但 SQLite 文件已独立保存，可在新 kernel 中重新查询。

预期结果：显示模块完成和数据库位置；第三模块将重新连接数据库，并按配置计算三个指标。

```python
# Cell 12: Close the Connection and Prepare the Next Module

database.close()
print("Database connection closed.")
print("Module 02 completed.")
print(f"Persistent database: {DATABASE_FILE}")
print("Next: query financial_records, join study periods and calculate metrics.")
print("No sales growth, operating margin or sales index has been calculated in Module 02.")
```

### 构建思路：明确完成存储，并留下下一步入口

`database.close()` 关闭连接；已提交的 SQLite 文件仍保留。后面的打印只是说明模块完成，不做额外计算或建表。

下一模块应重新连接 `DATABASE_FILE`，通过 `read_selected_records` 查询当前配置，再将 Module 01 的年度映射与阶段标签加到分析数据上。它不能仅从本格打印的文字获取财务数据。

基期 2019 的含义已经保存在配置，但本模块没有形成指数、同比或营业利润率。这样基础数据可以独立检查，也能被其他分析任务复用，不与特定报告结论绑在一起。

## 从研究需求到代码结构的完整构建思路

**第一步，确定一行代表什么。** 这里一行是一个分部的一个实际报告财年，不是公司合并数据，也不是指标结果。先建立稳定的 unit_id 与 fiscal_year，才能检查重复和覆盖。

**第二步，保留数据证据。** 输入 CSV 记录原始金额、单位、实际期间、官方链接和采用章节。数值从这些转录输入来，pandas 不会凭空产生财务数据。

**第三步，统一计算接口。** 所有来源转换成相同标准列，后续三个指标只需要数值列，不需要知道逗号如何清理或源报表使用百万还是十亿。

**第四步，把职责放在合适的位置。** 解析与检查是普通函数；SQLite 连接有持续状态，所以使用一个简单 DatabaseManager 类。研究对象、财年映射和疫情比较阶段是配置内容，不写成公司名称的 if 分支。

**第五步，先检查再存储。** 记录数、身份、日期、数值和来源格式通过之后才写数据库；来源真实性及业务口径仍依赖人工核对。SQL 主键和外键是第二层约束，不能代替研究者的判断。

**第六步，让重复运行有清楚行为。** 同一键同一内容不重复插入；来源或数值明确更新时覆盖该记录并使旧指标失效；整批写入使用事务。原始材料保留，导出核对文件更新。

**第七步，回读并交付下一模块。** 通过 SQL 生成 financial_df，逐字段与本次接受的数据核对，再关闭连接。数据库是真正可在另一个 kernel 中重新读取的持久化结果。

## 哪些内容会变，哪些框架通常不变

换研究对象时，修改 Module 01 JSON、原始 CSV、Cell 02 的文件映射和 Cell 06 展示别名。公司口径、年份、来源、货币和单位都要对应新内容，不能只换显示名称。

通常可复用 Cell 03 的清洗函数、Cell 04 的检查函数，以及 Cell 05 的数据库类。若新内容仍为 USD 的年度分部销售与营业利润，这些接口保持一致；若加入新币种、新报表结构或新基础指标，必须增加相应框架能力，不能用改名伪装成支持。

本次 COVID-19 分期仍保存在配置的 periods 中。数据存储无需判断某年是否疫情期；第三模块按配置组织比较，第四模块解释结果。这里只有一个疫情前年份，最终分析仍是描述性比较。

## 调用顺序

定义工具 → 读取并检查配置 → 定义清洗函数、检查函数和数据库类 → 读入两份 CSV → 标准化 → 检查配置覆盖 → 保存核对材料 → 创建数据库对象 → 连接与建表 → 事务写入 → SQL 回读 → 覆盖及字段核对 → 关闭连接。

类定义格与函数定义格需要先运行，调用格才能找到相应名称。更改源数据时重新读取，更改配置时重新创建 config，不能期待已经创建的对象或 DataFrame 自动更新。

## 完成后保存的文件

data/raw/amazon_segment_raw.csv 与 walmart_segment_raw.csv 是原始转录输入，source_manifest.json 是来源清单。data/financial_data.csv 是组合导入快照；data/clean/financial_records.csv 是含原始文本和标准数值的核对文件。data/retail_comparison.sqlite 是后续分析的数据入口。

数据库的 business_units 保存分部定义，financial_records 保存原始披露值、标准金额、财年、日期与来源，metric_results 为第三模块预留。本模块首次运行不会往 metric_results 写入虚构数值，也不会用零代替未计算指标。

如果你修改 CSV，应从 Cell 06 开始重新运行。已关闭连接时，在 Cell 10 前重新运行 Cell 09。导入过程中有错误，事务会回滚；可调用 database.close() 后修正源材料并重新运行。单纯修改 JSON 后，需要从 Cell 02 重新加载并核对配置。

核对依据与工具文档：[pandas.read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)、[pandas.read_sql_query](https://pandas.pydata.org/docs/reference/api/pandas.read_sql_query.html)、[Python sqlite3](https://docs.python.org/3.13/library/sqlite3.html)、[SQLite transactions](https://www.sqlite.org/lang_transaction.html)。
