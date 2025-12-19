import time
import pyautogui
from random import uniform
from selenium学习.opencv import CalculateDistance
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class DoubanSpider:
    def __init__(self):
        """初始化驱动"""
        self.service = Service(executable_path=r'D:\tools\python\chromedriver.exe')
        self.opt = Options()
        self.opt.add_argument("--disable-blink-features=AutomationControlled")
        self.opt.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.opt.add_experimental_option('useAutomationExtension', False)

        # 1. 先创建浏览器实例
        self.browser = webdriver.Chrome(options=self.opt, service=self.service)

        # 2. 紧接着在这里加载 stealth.js (必须在 get() 之前)
        # 注意：这行代码现在在 __init__ 函数内部，self 才有效
        try:
            with open(r'D:\tools\pythonDriver\stealth.min.js', 'r', encoding='utf-8') as f:
                js = f.read()
                self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js})
            print('防检测脚本加载成功')
        except FileNotFoundError:
            print("未找到 stealth.min.js 文件")

    def simulated_input(self,pic_addr,button):
        """模拟鼠标点击登录"""
        try:
            print(f"正在查找图片: {pic_addr}")
            try:
                loc = pyautogui.locateCenterOnScreen(pic_addr, confidence=0.8)
            except pyautogui.ImageNotFoundException:
                print("未找到图片，请检查图片路径或屏幕上是否存在该图片。")
                return False

            if loc:
                # print(f"正在处理坐标: {loc}")
                pyautogui.moveTo(loc)
                if button == 'left':
                    pyautogui.click()  # 使用click()而不是leftClick()
                return True
            else:
                print("未找到图片坐标")
                return False
        except Exception as e:
            print(f"模拟鼠标点击出错: {e}")
            return False


    def handle_distance(self,distance):
        """将直线距离转化为缓慢的轨迹"""
        import random
        slow_distance = []
        while sum(slow_distance) <= distance :
            slow_distance.append(random.randint(-2,15))

        if sum(slow_distance) != distance:
            slow_distance.append(distance - sum(slow_distance))
        return slow_distance


    def drag_slide(self,tracks,slide_addr):
        """拖动滑块"""
        try:
            loc = pyautogui.locateOnScreen(slide_addr)
            p1 = pyautogui.center(loc)
            print(f"找到滑块位置: {p1}")
            #移动到滑块位置
            current_pos = pyautogui.position()
            pyautogui.moveTo(p1[0], p1[1], duration=uniform(0.3, 0.8))
            #按下鼠标
            pyautogui.mouseDown()
            time.sleep(uniform(0.1, 0.3))
            #按照轨迹线移动
            for track in tracks:
                pyautogui.move(track,uniform(-2,2),duration=0.15)
            #释放鼠标
            pyautogui.mouseUp()
        except Exception as e:
            print(f"拖动滑块时出错: {e}")

    def login(self, url, username, password):
        try:
            self.browser.get(url)
            self.browser.implicitly_wait(10)
            self.browser.maximize_window()
            #定位用户iframe框架
            positioning_iframe = self.browser.find_element('xpath','//*[@id="anony-reg-new"]/div/div[1]/iframe')
            self.browser.switch_to.frame(positioning_iframe)
            #定位用户登录框
            time.sleep(3)
            denglu_input = self.browser.find_element('xpath','/html/body/div[1]/div[1]/ul[1]/li[2]')
            denglu_input.click()
            #定位账户
            time.sleep(uniform(2,5))
            zhanghu_input = self.browser.find_element('xpath','//*[@id="username"]')
            zhanghu_input.send_keys(username)
            #定位密码
            time.sleep(uniform(1, 5))
            mima_input = self.browser.find_element('xpath','//*[@id="password"]')
            mima_input.send_keys(password)

            #切回主文档
            self.browser.switch_to.default_content()
        except Exception as e:
            print(f"登录过程中出错: {e}")
        finally:
            self.browser.switch_to.default_content()


    def verification_code(self,img_path):
        """处理验证码"""
        try:
            #定位验证码iframe框架
            wait = WebDriverWait(self.browser, 10)

            img_out_iframe = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="anony-reg-new"]/div/div[1]/iframe')))
            self.browser.switch_to.frame(img_out_iframe)

            img_inner_iframe = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="tcaptcha_iframe_dy"]')))
            self.browser.switch_to.frame(img_inner_iframe)

            #定位滑块背景图片
            background_element = self.browser.find_element(By.ID,'slideBg')
            background_location = background_element.location
            print (f'背景图图片:{background_location}')
            background_img = background_element.screenshot_as_png
            filename = int(time.time())

            with open(f'{img_path}/back-{filename}.png', 'wb') as f:
                f.write(background_img)
                print (f'已下载背景图片到{img_path}位置')

            #获取滑块图片
            slide_element_1 = self.browser.find_element(By.XPATH,'//*[@id="tcOperation"]/div[8]')
            slide_element_2 = self.browser.find_element(By.XPATH,'//*[@id="tcOperation"]/div[9]')
            s1 = slide_element_1.size
            s2 = slide_element_2.size
            if s1['width'] > s2['width'] and s1['height'] < s2['height'] :
                slide_element = slide_element_2
            else:
                slide_element = slide_element_1
            slide_location = slide_element.location
            print (f'滑块缺口图片：{slide_location}')
            slide_img = slide_element.screenshot_as_png

            with open(f'{img_path}/slide-{filename}.png','wb') as f:
                f.write(slide_img)
                print(f'已下载滑块缺口图片到{img_path}位置')

            #背景图片和滑块图片地址
            bg_addr = f'{img_path}/back-{filename}.png'
            sd_addr = f'{img_path}/slide-{filename}.png'

            #计算滑块和背景图片的地址
            offset_x = slide_location['x'] - background_location['x']
            offset_y = slide_location['y'] - background_location['y']
            print(f'偏移量 - X: {offset_x}, Y: {offset_y}')

            #调用CalculateDistance类
            slide_offset = CalculateDistance(bg_addr,sd_addr,offset_x,offset_y,1)
            slide_distance = slide_offset.run()
            print(f'计算出的滑动距离: {slide_distance}')

            # #计算滑块轨迹
            # tracks = self.handle_distance (slide_distance)
            # print(f'生成的轨迹: {tracks}')
            #
            # #拖动滑块
            # slide_img_addr = r'D:\tools\pythonxianmu\picture\douban-slide.png'
            # self.drag_slide(tracks, slide_img_addr)

        except Exception as e:
            print ('处理验证码时出错:%e'%e)
        finally:
            self.browser.switch_to.default_content()


if __name__ == '__main__':
    spider = None
    try:
        spider = DoubanSpider()
        url = 'https://www.douban.com/'
        username = '1921244224'
        password = '12429097823'
        pic_addr = r'D:\tools\pythonxianmu\picture\douban-login.png'
        slide_addr = r'D:\tools\pythonxianmu\picture\douban-slide.png'
        img_path = r'D:\tools\pythonxianmu\picture\sildes'
        spider.login(url,username,password)
        time.sleep(3)
        spider.simulated_input(pic_addr,button='left')
        time.sleep(5)
        spider.verification_code(img_path)

    except Exception as e:
        print('程序运行错误: %s' % e)
    finally:
        if spider:
            # time.sleep(10)
            # spider.browser.quit()
            input('手动关闭浏览器')