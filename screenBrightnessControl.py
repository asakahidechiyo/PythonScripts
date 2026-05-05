import screen_brightness_control as sbc

curBrightness = sbc.get_brightness()
print(f"当前亮度：{curBrightness}%")

op = input("请输入目标亮度：")
sbc.set_brightness(int(op))
