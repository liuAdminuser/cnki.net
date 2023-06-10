import requests
import csv
import time
import ddddocr
import io
from PIL import Image
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

# 设置请求头
options = Options()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36')

# 启动浏览器并设置请求头
driver = webdriver.Edge(options=options)

try:
    # 打开目标网址
    url = 'https://www.cnki.net/'
    driver.get(url)

    # 等待页面加载完成
    time.sleep(3)

    # 查找搜索栏元素
    search_input = driver.find_element(By.CSS_SELECTOR, 'input.search-input')

    if search_input:
        print("找到了搜索栏")
        # 获取用户输入的搜索值
        keyword = input("请输入搜索关键字: ")
        # 输入搜索值并执行搜索
        search_input.clear()
        search_input.send_keys(keyword)
        search_input.send_keys(Keys.ENTER)

        # 等待搜索结果加载完成
        time.sleep(2)

        # 初始化计数器
        count = 0
        captcha_enabled = False

        # 获取标题行的文本
        thead = driver.find_element(By.CSS_SELECTOR, 'thead')
        tr_elements = thead.find_elements(By.TAG_NAME, 'tr')
        titles = [td.text for td in tr_elements[0].find_elements(By.TAG_NAME, 'td')]

        # 创建CSV文件并写入标题行
        with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(titles + ['链接'])

            while count < 10000:
                try:
                    # 查找<tbody>元素下的<tr>元素
                    tbody = driver.find_element(By.CSS_SELECTOR, 'table.result-table-list tbody')
                    tr_elements = tbody.find_elements(By.TAG_NAME, 'tr')
                    for tr in tr_elements:
                        td_elements = tr.find_elements(By.TAG_NAME, 'td')
                        link_element = td_elements[1].find_element(By.TAG_NAME, 'a')
                        link = link_element.get_attribute('href')
                        row_data = [td.text if td.text else '0' for td in td_elements]
                        writer.writerow(row_data + [link])
                        count += 1
                        if count >= 10000:
                            break

                    # 查找下一页的翻页链接并点击
                    next_page_link = driver.find_element(By.CSS_SELECTOR, 'a#PageNext')
                    driver.execute_script("arguments[0].click();", next_page_link)

                    # 等待页面加载完成
                    time.sleep(3)

                except NoSuchElementException:
                        # 处理验证码逻辑
                        captcha_element = driver.find_element(By.CSS_SELECTOR, 'img#changeVercode')
                        print("找到了验证码图片")
                        captcha_image_url = captcha_element.get_attribute('src')
                        # 下载验证码图片
                        print("正在下载验证码")
                        captcha_image_url = captcha_element.get_attribute('src')
                        response = requests.get(captcha_image_url)
                        with open('captcha_image.png', 'wb') as f:
                            f.write(response.content)

                        # 使用 ddddocr 识别验证码
                        print("正在解析验证码")
                        ocr = ddddocr.DdddOcr()
                        with open('captcha_image.png', 'rb') as f:
                            image_bytes = f.read()
                            res = ocr.classification(image_bytes)
                        captcha_text = res

                        # 输入验证码并提交
                        print("正在输入验证码")
                        captcha_input = driver.find_element(By.CSS_SELECTOR, 'input#vericode')
                        captcha_input.clear()
                        captcha_input.send_keys(captcha_text)

                        # 点击提交验证码按钮
                        print("正在提交验证码")
                        submit_button = driver.find_element(By.CSS_SELECTOR, 'a#checkCodeBtn')
                        ActionChains(driver).move_to_element(submit_button).click().perform()

                        # 等待页面加载完成
                        time.sleep(3)

                if not captcha_enabled:
                    continue

finally:
    # 关闭浏览器
    driver.quit()

