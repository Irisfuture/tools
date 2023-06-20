#运行程序时，它会提示您将鼠标放到第一个坐标上，并按下回车键。然后等待您将鼠标放到第二个坐标上，并再次按下回车键。
#程序将使用这两个坐标来定义一个矩形框，该矩形框将成为要截取的屏幕区域。程序将使用ImageGrab.grab()方法截取该区域的屏幕截图，并使用Image.save()方法将其保存到指定的文件路径中。
import pyautogui
from PIL import Image
from PIL import ImageGrab
import time

def cut_word():
    text = '正在获取位置...'
    for char in text:
        print(char, end='', flush=True)  # 逐字打印字符
        time.sleep(0.2)  # 等待0.1秒钟以便用户可以看到每个字母
    print()  # 换行

input('请把鼠标放到第一个坐标，按下回车')
cut_word()
x, y = pyautogui.position()
time.sleep(0.5)  # 等待0.5秒钟
input('请把鼠标放到第二个坐标，按下回车')
cut_word()
n, m = pyautogui.position()
time.sleep(0.5)
box = (x, y, n, m)
img = ImageGrab.grab(box)
img.save("Er.png")  # 括号内路径
print('截图成功，已保存为“Er.png”')

