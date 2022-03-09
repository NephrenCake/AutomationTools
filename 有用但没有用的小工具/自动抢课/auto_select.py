# -- coding: utf-8 --
import time
from selenium.webdriver import Edge

user = ""  # 学号
pw = ""  # 密码

url = f"https://jwgl.njtech.edu.cn/xsxk/zzxkyzb_cxZzxkYzbIndex.html?gnmkdm=N253512&layout=default&su={user}"  # 这里给你的选课页面url

driver = Edge("D:\ProgrammingKits\Python36/MicrosoftWebDriver.exe")  # 百度搜MicrosoftWebDriver下载对应的驱动，版本号看你edge的设置-关于Microsoft Edge
driver.get(url)

driver.find_element_by_xpath('//*[@id="yhm"]').send_keys(user)
driver.find_element_by_xpath('//*[@id="mm"]').send_keys(pw)
driver.find_element_by_xpath('//*[@id="dl"]').click()

time.sleep(2)
driver.find_element_by_xpath('//*[@id="searchBox"]/div/div[1]/div/div/div/div/input').send_keys("尔雅 智慧树")
# 通过 xpath 选择你想要的标签
driver.find_element_by_xpath('//*[@id="searchBox"]/div/div[3]/div[13]/div/div/ul/li[1]/a').click()  # 有余量
driver.find_element_by_xpath('//*[@id="searchBox"]/div/div[3]/div[7]/div/div[1]/ul/li[6]/a').click()  # 自然

count, get = 0, 0
while True:
    count += 1
    try:
        driver.find_element_by_xpath('//*[@id="searchBox"]/div/div[1]/div/div/div/div/span/button[1]').click()  # 查询
        time.sleep(0.5)  # 等待查询结果
        if driver.find_element_by_xpath('/html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/tbody/tr/td[24]/button').text == '选课':
            driver.find_element_by_xpath('/html/body/div[1]/div/div/div[5]/div/div[2]/div[1]/div[2]/table/tbody/tr/td[24]/button').click()
            print("选课成功")
            get += 1
    except Exception as e:
        print(get, count, e)
    time.sleep(0.5)  # 调节时间间隔
