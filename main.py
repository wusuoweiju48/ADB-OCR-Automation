import cv2
import numpy as np
from adbutils import adb
import time

# === 核心设置区域 ===
# 你的红色数值
lower = np.array([3, 97, 142])
upper = np.array([23, 177, 222])

# 【关键设置】面积阈值
# 如果还在乱点，就把这个数字改大（比如 2000）
# 如果该点的不点，就把这个数字改小（比如 200）
MIN_AREA = 800 

def connect_device():
    """尝试自动连接模拟器"""
    print("正在尝试连接模拟器...")
    # 常见模拟器端口：MuMu(7555), 雷电/蓝叠(5555), 夜神(62001), 逍遥(21503)
    known_ports = [7555, 5555, 62001, 21503]
    
    for port in known_ports:
        try:
            adb.connect(f"127.0.0.1:{port}")
        except:
            pass
            
    # 获取连接成功的设备
    devices = adb.device_list()
    if len(devices) > 0:
        return devices[0]
    else:
        return None

def main():
    print("=== 脚本启动 ===")
    
    # 1. 连接设备
    device = connect_device()
    if device:
        print(f"✅ 成功连接设备: {device.serial}")
    else:
        print("❌ 无法连接模拟器！")
        print("解决方法：请重启模拟器，确保开启了ROOT和ADB调试，然后重新运行脚本。")
        return

    print(f"🎯 开始运行！只点击面积大于 {MIN_AREA} 的红色区域...")
    print("(按 Ctrl+C 可以停止脚本)")
    
    # 2. 循环截图判断
    while True:
        try:
            # 截图
            png_data = device.shell("screencap -p", encoding=None)
            img = cv2.imdecode(np.frombuffer(png_data, np.uint8), cv2.IMREAD_COLOR)
            
            # 颜色识别
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, lower, upper)
            
            # 找轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # 找到屏幕上最大的一块红色
                max_c = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(max_c)

                # 【防止乱点】只有面积够大才点
                if area > MIN_AREA:
                    x, y, w, h = cv2.boundingRect(max_c)
                    cx, cy = x + w//2, y + h//2
                    print(f"👉 发现目标 (面积:{int(area)}) -> 点击: {cx}, {cy}")
                    
                    device.click(cx, cy)
                    
                    # 点击后稍微等一下，给游戏反应时间
                    time.sleep(0.5) 
                else:
                    # 面积太小，认为是杂色，忽略
                    print(f"👀 忽略小杂点 (面积:{int(area)})")
            else:
                print("...画面中没有红色...")
            
            # 每次循环间隔，防止电脑过热
            time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n🛑 用户手动停止")
            break
        except Exception as e:
            print(f"⚠️ 发生小错误 (通常不用管): {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
