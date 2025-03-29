###
本脚本需浏览器要先基于Chromium内核，例如Edge
所需python库依赖：DrissionPage，tqdm（progress版需要，common版不需要）
然后先启动默认浏览器配置脚本，格式：python set_path.py "浏览器可执行文件路径"
记住是"浏览器可执行文件路径"，引号不能去除！！！
###
JSON配置文件说明
pages：爬取的页数，默认值1
keyword：关键词，即搜索词，默认值”.“
results_show：展示最大爬取结果条目数量，默认值全部显示
included：包含关键词
notincluded：不包含关键词
min_price：最小价格，默认0
max_price：最大价格，默认与商品同价
###
参数设置为null即使用默认值
