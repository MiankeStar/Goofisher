# 基于Chromium内核的闲鱼爬虫脚本配置指南

## 方便

**若不想繁琐的使用python，则可以前往[Releases](https://github.com/MiankeStar/Goofisher/releases)界面下载图形化可执行文件**

## 环境准备

1. ​**浏览器要求**：
   - 必须使用基于Chromium内核的浏览器（如Microsoft Edge或Google Chrome）
   - 确保浏览器已安装并可用

2. ​**Python库依赖**：
   - 必须安装`DrissionPage`库：`pip install DrissionPage`
   - 如使用process版本，需进度条功能，安装`tqdm`库：`pip install tqdm`，common请忽略

## 初始配置

1. ​**设置浏览器路径**：
   - 编辑gfc.json，配置其browser_path属性，选择浏览器可执行文件路径！
   - ​**注意**：路径必须用英文双引号包裹，不能去除！

## gfc.json配置文件说明

| 参数名 | 说明 | 默认值 | 类型 | 例子 |
|--------|------|--------|------|------|
| `browser_path`| 浏览器可执行文件路径 | - | `string` | C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe |
| `pages` | 爬取的页数 | 1 | `int` | 10 |
| `keyword` | 搜索关键词 | "python" | `string` | "iqooz9turbo" |
| `results_show` | 最大显示结果数 | 终端版全部/图形化版1项 | `int` | 10 |
| `included` | 必须包含的关键词（逗号分隔） | "" | `string` | "8,256" |
| `notincluded` | 必须不包含的关键词（逗号分隔） | "" | `string` | "长续航版,turbo+" |
| `all_check` | 必须包含全部关键词 | 是 | `boolean` | true |
| `is_upper` | 是否区分大小写 | 是 | `boolean` | true |
| `min_price` | 最小价格 | 0 | `float` | 100 |
| `max_price` | 最大价格 | 与商品同价/python的float最大值 | `float` | 999 |
| `content_range` | 文本字数限制 | 与标题同字数/python的int最大值 | `int` | 999 |

**注意**：
- 除`browser_path`外其余参数设置为`null`将使用默认值
- 配置项说明清晰明确，便于理解和使用

## 技术说明

1. ​**进度条功能**：
   - `tqdm`提供直观的进度显示
   - 仅process版需要此依赖，common版不需要

2. **图形化界面**：
   - 图形化界面基于`PyQt6`开发，若需自己改进请记得安装PyQt6依赖库
