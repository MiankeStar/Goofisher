from DrissionPage import ChromiumPage
from itertools import islice
from pathlib import Path
import json
import time

# 创建 ChromiumPage 实例
driss = ChromiumPage()
try:
    # 初始化变量
    nowtime = time.time()
    config = dict()
    products = dict()
    #读取配置
    with open('../gfc.json', 'r', encoding='utf-8') as gfc:
        config = json.load(gfc)
    included = config['included']
    notincluded = config['notincluded']
    results_show = config['results_show']
    keyword = config['keyword']
    pages = config['pages']
    min_price = config['min_price']
    max_price = config['max_price']

    #默认值
    keyword = '.' if not keyword else keyword
    pages = 1 if not pages else pages

    # 打开网页
    print('打开闲鱼官网。')
    driss.get('https://www.goofish.com/')

    print('输入关键词。')
    # 输入搜索关键词
    driss.ele('css:.search-input--WY2l9QD3').input(keyword)

    print('开始搜索。')
    # 点击搜索按钮
    driss.ele('css:.search-icon--bewLHteU').check()

    # 开始监听网络请求
    driss.listen.start('h5/mtop.taobao.idlemtopsearch.pc.search/1.0')

    for _ in range(pages):
        # 等待网络请求响应
        response = driss.listen.wait()
        try:
            # 获取响应体
            response_body = response.response.body
            result_list = response_body['data']['resultList']
            for item in result_list:
                item_data = item['data']['item']['main']
                ex_content = item_data['exContent']
                click_params = item_data['clickParam']['args']

                product_id = click_params['id']
                category_id = click_params['cCatId']
                product_url = f'https://www.goofish.com/item?spm=a21ybx.search.searchFeedList&id={product_id}&categoryId={category_id}'

                try:
                    detail_params = ex_content['detailParams']
                    shop_name = detail_params.get('userNick', '未知店铺')
                except KeyError:
                    shop_name = '未知店铺'

                product_info = {
                    '标题': ex_content['title'],
                    '主图': ex_content['picUrl'],
                    '发货地': ex_content['area'],
                    '店铺名': shop_name,
                    '价格': click_params['price'],
                    '商品链接': product_url
                }
                
                tempt = product_info['标题']
                price = float(product_info['价格'])
                if (not included or any(word in tempt for word in included)) and (not notincluded or not any(word in tempt for word in notincluded)) and ((price >= (0 if not min_price else min_price)) and (price <= (price if not max_price else max_price))):
                    products[tempt] = (price, shop_name)

        except (KeyError, ValueError) as e:
            print(f"处理数据时出错: {e}")

        # 点击下一页按钮
        try:
            driss.ele('xpath://*[@id="content"]/div[1]/div[4]/div/div[1]/button[2]').check()
        except Exception as e:
            print(f"点击下一页按钮时出错: {e}")

    # 计算均价
    print('开始整理结果。')
    items = products.items()
    final_prices = {v[0] for k, v in items}
    num_products = len(products)
    results_show = num_products if not results_show else results_show
    if final_prices:
        average_price = round(sum(final_prices) / len(final_prices), 2)
        print(f"商品“{keyword}”市场均价为{average_price}，参考结果有{num_products}个，以下为前{results_show}个参考结果的标题：")
        for i, (k, v) in enumerate(islice(items, results_show)):
            print(f'第{i + 1}个结果：{k}（价格：{v[0]}，店铺名：{v[1]}）')
    else:
        print("未找到符合条件的商品。")
    print(f'爬取完毕，本次耗时{int((time.time() - nowtime) * 1000)}毫秒。')
except Exception as e:
    print(f"发生未知错误: {e}")
