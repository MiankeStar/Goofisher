# 基于Chromium内核的爬虫脚本配置指南

## 环境准备

1. ​**浏览器要求**：
   - 必须使用基于Chromium内核的浏览器（如Microsoft Edge或Google Chrome）
   - 确保浏览器已安装并可用

2. ​**Python库依赖**：
   - 必须安装`DrissionPage`库：`pip install DrissionPage`
   - 如使用progress版本，需进度条功能，安装`tqdm`库：`pip install tqdm`，common请忽略

## 初始配置

1. ​**设置浏览器路径**：
   - 运行配置脚本：`python set_path.py "浏览器可执行文件路径"`
   - ​**注意**：路径必须用英文双引号包裹，不能去除！

## JSON配置文件说明

| 参数名 | 说明 | 默认值 |
|--------|------|--------|
| `pages` | 爬取的页数 | 1 |
| `keyword` | 搜索关键词 | "." |
| `results_show` | 最大显示结果数 | 全部显示 |
| `included` | 必须包含的关键词 | - |
| `notincluded` | 必须不包含的关键词 | - |
| `min_price` | 最小价格 | 0 |
| `max_price` | 最大价格 | 与商品同价 |

**注意**：
- 任何参数设置为`null`将使用默认值
- 配置项说明清晰明确，便于理解和使用

## 技术说明

1. ​**进度条功能**：
   - `tqdm`提供直观的进度显示
   - 仅progress版需要此依赖，common版不需要
