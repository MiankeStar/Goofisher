import json
import os
import threading
import time
from itertools import islice
from typing import Dict, Tuple

from DrissionPage._configs.chromium_options import ChromiumOptions
from DrissionPage._pages.chromium_page import ChromiumPage
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QApplication, QWidget, QLineEdit, QHBoxLayout,
                             QVBoxLayout, QPushButton, QTextEdit, QCheckBox,
                             QProgressBar, QLabel, QFileDialog)
import sys


class WorkerSignals(QObject):
    update_log = pyqtSignal(str)
    update_progress = pyqtSignal(int)
    set_button_status = pyqtSignal(bool)
    set_progress_range = pyqtSignal(int, int)


class GoofisherGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.worker_signals = WorkerSignals()
        self.setup_connections()

    @staticmethod
    def resources_path(relative_path):
        if hasattr(sys, "_MEIPASS"):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def init_ui(self):
        self.setWindowTitle("Goofisher")
        self.setWindowIcon(QIcon(self.resources_path("icon.ico")))
        self.resize(app.primaryScreen().availableGeometry().center().x(),
                    app.primaryScreen().availableGeometry().center().y() * 2)
        self.move(app.primaryScreen().availableGeometry().center().x() - self.width() // 2,
                  app.primaryScreen().availableGeometry().center().y() - self.height() // 2)
        self.create_widgets()
        self.create_layouts()
        self.set_stylesheets()

    def create_widgets(self):
        self.pages = QLineEdit()
        self.keyword = QLineEdit()
        self.results_show = QLineEdit()
        self.included = QLineEdit()
        self.notincluded = QLineEdit()
        self.min_price = QLineEdit()
        self.max_price = QLineEdit()
        self.is_upper = QCheckBox("区分大小写")
        self.all_check = QCheckBox("包含所有关键字")
        self.logger = QTextEdit()
        self.progress = QProgressBar()
        self.start_btn = QPushButton("开始爬取")
        self.clear_btn = QPushButton("清空日志")
        self.load_btn = QPushButton("读取配置")
        self.browser_path = QLineEdit()
        self.browser_path.setPlaceholderText("浏览器可执行文件路径（必填）")

        # 初始化状态
        self.is_upper.setChecked(True)
        self.all_check.setChecked(True)
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.progress.setFormat("当前进度：%v/%m")

        # 设置占位文本
        components = {
            self.pages: "请输入要爬取的页数",
            self.keyword: "请输入搜索关键字",
            self.results_show: "请输入显示结果数",
            self.included: "包含关键词（逗号分隔）",
            self.notincluded: "排除关键词（逗号分隔）",
            self.min_price: "最低价格（单位：元）",
            self.max_price: "最高价格（单位：元）",
            self.logger: "操作日志..."
        }
        for widget, text in components.items():
            widget.setPlaceholderText(text)

    def create_layouts(self):
        main_layout = QVBoxLayout()
        header_btns = QHBoxLayout()
        checkboxes_btns = QHBoxLayout()

        header_btns.addWidget(self.start_btn)
        header_btns.addWidget(self.clear_btn)
        header_btns.addWidget(self.load_btn)

        main_layout.addLayout(header_btns)
        main_layout.addWidget(QLabel("匹配设置"))
        checkboxes_btns.addWidget(self.is_upper)
        checkboxes_btns.addWidget(self.all_check)
        main_layout.addLayout(checkboxes_btns)

        main_layout.addWidget(QLabel("基本参数"))
        main_layout.addWidget(self.pages)
        main_layout.addWidget(self.keyword)
        main_layout.addWidget(self.results_show)

        main_layout.addWidget(QLabel("浏览器路径"))
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.browser_path)
        main_layout.addLayout(path_layout)

        main_layout.addWidget(QLabel("过滤条件"))
        main_layout.addWidget(self.included)
        main_layout.addWidget(self.notincluded)
        main_layout.addWidget(self.min_price)
        main_layout.addWidget(self.max_price)

        main_layout.addWidget(QLabel("进度状态"))
        main_layout.addWidget(self.progress)
        main_layout.addWidget(self.logger)

        self.setLayout(main_layout)

    def set_stylesheets(self):
        # 按钮样式
        btn_style = """
        QPushButton {
            background-color: #2196F3;
            border: none;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 14px;
            margin: 3px;
            min-width: 80px;
        }
        QPushButton:disabled {background-color: #BBDEFB;}
        QPushButton:hover {background-color: #1976D2;}
        """
        self.start_btn.setStyleSheet(btn_style.replace("2196F3", "4CAF50"))
        self.clear_btn.setStyleSheet(btn_style.replace("2196F3", "F44336"))
        self.load_btn.setStyleSheet(btn_style)

        # 复选框美化
        checkboxes_style = """
        QCheckBox {
            font-size: 14px;
            color: #616161;
            padding: 8px 0;
            margin-left: 5px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 2px solid #BDBDBD;
        }
        QCheckBox::indicator:checked {
            background-color: #4CAF50;
            border: 2px solid #388E3C;
        }
        """
        self.is_upper.setStyleSheet(checkboxes_style)
        self.all_check.setStyleSheet(checkboxes_style)

        # 输入框通用样式
        self.setStyleSheet("""
        QLineEdit, QTextEdit {
            border: 2px solid #E0E0E0;
            border-radius: 6px;
            padding: 8px;
            font-size: 14px;
            margin: 5px 0;
            background: #FAFAFA;
        }
        QProgressBar {
            border: 2px solid #E0E0E0;
            border-radius: 6px;
            text-align: center;
            height: 25px;
            background: #F5F5F5;
        }
        QLabel {
            color: #616161;
            font-weight: 500;
            margin-top: 10px;
        }
        """)

    def setup_connections(self):
        self.clear_btn.clicked.connect(self.logger.clear)
        self.start_btn.clicked.connect(self.start_crawler)
        self.load_btn.clicked.connect(self.load_config)
        self.worker_signals.update_log.connect(self.logger.append)
        self.worker_signals.update_progress.connect(self.update_progress)
        self.worker_signals.set_button_status.connect(self.set_button_status)
        self.worker_signals.set_progress_range.connect(self.progress.setRange)

    def load_config(self):
        try:
            path, _ = QFileDialog.getOpenFileName(self, "选择配置文件", "", "JSON Files (*.json)")
            if path:
                with open(path, "r", encoding="utf-8") as f:
                    config = json.load(f)

                # 映射字段到组件
                field_map = {
                    "browser_path": self.browser_path,
                    "pages": self.pages,
                    "keyword": self.keyword,
                    "results_show": self.results_show,
                    "included": self.included,
                    "notincluded": self.notincluded,
                    "min_price": self.min_price,
                    "max_price": self.max_price,
                    "is_upper": self.is_upper,
                    "all_check": self.all_check
                }

                for key, widget in field_map.items():
                    value = config.get(key, "")
                    if isinstance(widget, QLineEdit):
                        widget.setText(str(value))
                    elif isinstance(widget, QCheckBox):
                        widget.setChecked(bool(value))

                self.logger.append(f"成功加载配置文件：{path}")

        except Exception as e:
            self.logger.append(f"配置加载失败：{str(e)}")

    def start_crawler(self):
        # 添加路径校验
        if not self.browser_path.text().strip():
            self.logger.append("错误：必须配置浏览器路径")
            return

        config = {
            "browser_path": self.browser_path.text().strip(),
            "pages": self.pages.text(),
            "keyword": self.keyword.text(),
            "results_show": self.results_show.text(),
            "included": self.included,
            "notincluded": self.notincluded,
            "is_upper": self.is_upper.isChecked(),
            "min_price": self.min_price.text(),
            "max_price": self.max_price.text(),
            "all_check": self.all_check.isChecked()
        }
        thread = threading.Thread(
            target=catch,
            args=(config, self.worker_signals)
        )
        thread.daemon = True
        thread.start()

    def update_progress(self, value):
        self.progress.setValue(value)

    def set_button_status(self, enabled):
        self.start_btn.setEnabled(enabled)
        self.start_btn.setText("开始爬取" if enabled else "正在运行...")

def validate_input(value, default, type_=int):
    try:
        return type_(value) if value.strip() else default
    except ValueError:
        return default


def catch(config, signals):
    signals.set_button_status.emit(False)
    signals.update_log.emit("启动爬虫任务...")

    options = ChromiumOptions()
    options.set_browser_path(config["browser_path"])

    try:
        driss = ChromiumPage(options)
        products: Dict[str, Tuple[float, str]] = {}
        nowtime = time.time()

        # 参数处理
        pages = validate_input(config["pages"], 1)
        keyword = config["keyword"] or "python"
        results_show = validate_input(config["results_show"], 1)
        min_price = validate_input(config["min_price"], 0.0, float)
        max_price = validate_input(config["max_price"], float("inf"), float)

        # 关键词处理
        included = [w.strip() for w in config["included"].text().replace("，", ",").split(",") if w.strip()]
        notincluded = [w.strip() for w in config["notincluded"].text().replace("，", ",").split(",") if w.strip()]
        case_func = str.upper if bool(config["is_upper"]) else lambda x: x
        included = list(map(case_func, included))
        notincluded = list(map(case_func, notincluded))
        all_check = bool(config['all_check'])

        signals.set_progress_range.emit(0, pages)

        # 开始爬取
        signals.update_log.emit("访问闲鱼官网...")
        driss.get("https://www.goofish.com/")

        # 搜索操作
        search_input = driss.ele("css:.search-input--WY2l9QD3", timeout=10)
        search_input.input(keyword)
        driss.ele("css:.search-icon--bewLHteU").click()

        driss.listen.start("h5/mtop.taobao.idlemtopsearch.pc.search/1.0")

        for current_page in range(1, pages + 1):
            signals.update_progress.emit(current_page)
            response = driss.listen.wait()

            try:
                result_list = response.response.body["data"]["resultList"]
                process_items(result_list, products, included, notincluded,
                            min_price, max_price, case_func, signals, all_check)
            except Exception as e:
                signals.update_log.emit(f"页面处理错误: {str(e)}")

            # 翻页操作
            if current_page < pages:
                try:
                    driss.ele("xpath://*[@id=\"content\"]/div[1]/div[4]/div/div[1]/button[2]").check()
                except Exception as e:
                    signals.update_log.emit(f"翻页失败: {str(e)}")
                    break

        display_results(products, keyword, results_show, signals, nowtime)

    except Exception as e:
        signals.update_log.emit(f"爬虫异常: {str(e)}")
    finally:
        if "driss" in locals():
            driss.quit()
        signals.set_button_status.emit(True)


def process_items(result_list, products, included, notincluded,
                min_price, max_price, case_func, signals, all_check):
    for item in result_list:
        try:
            item_data = item["data"]["item"]["main"]
            ex_content = item_data["exContent"]
            click_params = item_data["clickParam"]["args"]

            title = ex_content["title"]
            price = float(click_params["price"])
            processed_title = case_func(title)

            icd = (True, ) if not included else (word in processed_title for word in included)
            nicd = (False, ) if not notincluded else (word in processed_title for word in notincluded)
            icd = all(icd) if all_check else any(icd)
            nicd = all(nicd) if all_check else any(nicd)
            # 关键词过滤
            if not icd:
                continue
            if nicd:
                continue

            # 价格过滤
            if not (min_price <= price <= max_price):
                continue

            # 店铺信息
            shop_name = ex_content.get("detailParams", {}).get("userNick", "未知店铺")
            products[title] = (price, shop_name)

        except Exception as e:
            signals.update_log.emit(f"商品处理错误: {str(e)}")


def display_results(products, keyword, results_show, signals, start_time):
    if not products:
        signals.update_log.emit("未找到符合条件的结果")
        return

    products_values = products.values()
    prices = [price for price, shop in products_values]
    shops = [shop for price, shop in products_values]
    res_min_price = min(prices)
    res_max_price = max(prices)
    res_min_shop = shops[prices.index(res_min_price)]
    res_max_shop = shops[prices.index(res_max_price)]
    avg_price = sum(prices) / len(prices)
    time_cost = int((time.time() - start_time) * 1000)

    result_text = [
        f"【{keyword}】市场分析结果：",
        f"▪ 最低价格：[{res_min_shop}] - ￥{res_min_price:.2f}",
        f"▪ 最高价格：[{res_max_shop}] - ￥{res_max_price:.2f}",
        f"▪ 平均价格：¥{avg_price:.2f}",
        f"▪ 有效商品数：{len(products)}",
        f"▪ 耗时：{time_cost}ms",
        f"\n前{min(results_show, len(products))}个结果："
    ]

    for idx, (title, (price, shop)) in enumerate(islice(products.items(), results_show), 1):
        result_text.append(f"{idx}. [{shop}] {title} - ¥{price:.2f}")

    signals.update_log.emit("\n".join(result_text))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GoofisherGUI()
    window.show()
    sys.exit(app.exec())
