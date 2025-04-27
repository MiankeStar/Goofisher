from DrissionPage import ChromiumPage
from DrissionPage._configs.chromium_options import ChromiumOptions
from itertools import islice
from pathlib import Path
import json
import time
import os
import sys

# 初始化变量
args = sys.argv
output_path = str()
if len(args) >= 2:
    output_path = args[1]
nowtime = time.time()
config = dict()
products = dict()
#读取配置
with open("../gfc.json", "r", encoding="utf-8") as gfc:
    config = json.load(gfc)
included = config["included"]
notincluded = config["notincluded"]
all_check = config["all_check"]
is_upper = config["is_upper"]
results_show = config["results_show"]
keyword = config["keyword"]
pages = config["pages"]
min_price = config["min_price"]
max_price = config["max_price"]
content_range = config["content_range"]
# 创建 ChromiumPage 实例
browser_path = config.get("browser_path", None)
if browser_path and not os.path.exists(browser_path):
    print("请配置正确浏览器路径。")
    exit()
options = ChromiumOptions()
options.set_browser_path(browser_path)
driss = ChromiumPage(options)

try:
    #默认值
    keyword = "." if not keyword else keyword
    pages = 1 if not pages else pages
    included = included.replace("，", ",")
    notincluded = notincluded.replace("，", ",")
    included = None if not included else "".join([i.upper() for i in included]).split(",") if is_upper else included.split(",")
    notincluded = None if not notincluded else "".join([ni.upper() for ni in notincluded]).split(",") if is_upper else notincluded.split(",")
    is_upper = bool(is_upper)
    all_check = bool(all_check)
    content_range = 

    # 打开网页
    print("打开闲鱼官网。")
    driss.get("https://www.goofish.com/")

    print("输入关键词。")
    # 输入搜索关键词
    driss.ele("css:.search-input--WY2l9QD3").input(keyword)

    print("开始搜索。")
    # 点击搜索按钮
    driss.ele("css:.search-icon--bewLHteU").check()

    # 开始监听网络请求
    driss.listen.start("h5/mtop.taobao.idlemtopsearch.pc.search/1.0")

    for _ in range(pages):
        # 等待网络请求响应
        response = driss.listen.wait()
        try:
            # 获取响应体
            response_body = response.response.body
            result_list = response_body["data"]["resultList"]
            for item in result_list:
                item_data = item["data"]["item"]["main"]
                ex_content = item_data["exContent"]
                click_params = item_data["clickParam"]["args"]

                product_id = click_params["id"]
                category_id = click_params["cCatId"]
                product_url = f"https://www.goofish.com/item?spm=a21ybx.search.searchFeedList&id={product_id}&categoryId={category_id}"

                try:
                    detail_params = ex_content["detailParams"]
                    shop_name = detail_params.get("userNick", "未知店铺")
                except KeyError:
                    shop_name = "未知店铺"

                product_info = {
                    "标题": ex_content["title"],
                    "主图": ex_content["picUrl"],
                    "发货地": ex_content["area"],
                    "店铺名": shop_name,
                    "价格": click_params["price"],
                    "商品链接": product_url
                }
                stempt = product_info["标题"]
                tempt = stempt.upper() if is_upper else stempt
                price = float(product_info["价格"])
                icd = (True, ) if not included else (word in tempt for word in included)
                nicd = (False, ) if not notincluded else (word in tempt for word in notincluded)
                judgei = all(icd) if all_check else any(icd)
                judgeni = all(nicd) if all_check else any(nicd)
                tempt_range = len(tempt)
                if (judgei and not judgeni) and ((0 if not min_price else min_price) <= price <= (price if not max_price else max_price)) and (tempt_range <= len(content_range if not tempt_range)):
                    products[stempt] = (price, shop_name)
        except (KeyError, ValueError) as e:
            print(f"处理数据时出错: {e}")

        # 点击下一页按钮
        try:
            driss.ele("xpath://*[@id=\"content\"]/div[1]/div[4]/div/div[1]/button[2]").check()
        except Exception as e:
            print(f"点击下一页按钮时出错: {e}")

    # 计算均价
    print("开始整理结果。")
    items = products.items()
    final_prices = tuple(v[1][0] for v in items)
    final_shop = tuple(v[1][1] for v in items)
    num_products = len(products)
    results_show = num_products if results_show >= num_products else results_show
    if final_prices:
        average_price = round(sum(final_prices) / len(final_prices), 2)
        min_price = min(final_prices)
        min_shop = final_shop[final_prices.index(min_price)]
        max_price = max(final_prices)
        max_shop = final_shop[final_prices.index(max_price)]
        info = f"商品“{keyword}”结果：\n最低价——￥{min_price}（店铺名：{min_shop}）\n最高价——￥{max_price}（店铺名：{max_shop}）\n均价——￥{average_price}\n参考结果有{num_products}个，以下为前{results_show}个参考结果的标题："
        if output_path:
            target = list()
            target.append(info)
            for i, (k, v) in enumerate(islice(items, results_show)):
                target.append(f"第{i + 1}个结果：{k}（价格：￥{v[0]}，店铺名：{v[1]}）")
            with open(output_path, "w", encoding="utf-8") as w:
                w.write("\n".join(target))
            print(f"结果已保存至“{output_path}”文件。")
        else:
            print(info)
            for i, (k, v) in enumerate(islice(items, results_show)):
                print(f"第{i + 1}个结果：{k}（价格：￥{v[0]}，店铺名：{v[1]}）")
    else:
        print("未找到符合条件的商品。")
    print(f"爬取完毕，本次耗时{int((time.time() - nowtime) * 1000)}毫秒。")
except Exception as e:
    print(f"发生未知错误: {e}")
finally:
    driss.quit()