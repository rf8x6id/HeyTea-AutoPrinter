import cv2
import numpy as np
import pyautogui
import time
import sys
import os

pyautogui.FAILSAFE = True 
pyautogui.PAUSE = 0.005

def get_image_contours(image_path):
    if not os.path.exists(image_path):
        print(f"错误：找不到图片 -> {image_path}")
        return None, None, None

    img = cv2.imread(image_path)
    if img is None:
        return None, None, None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    h, w = img.shape[:2]
    
    valid_contours = [c for c in contours if cv2.arcLength(c, False) > 50]
    valid_contours.sort(key=lambda c: cv2.boundingRect(c)[1])
    
    return valid_contours, w, h

def calibrate_canvas():
    print("\n--- 校准步骤 ---")
    print("请定义 iPhone 镜像窗口中的【画布区域】。")
    
    input("1. 移到画布【左上角】 -> 按回车...")
    x1, y1 = pyautogui.position()
    
    input("2. 移到画布【右下角】 -> 按回车...")
    x2, y2 = pyautogui.position()
    
    width = x2 - x1
    height = y2 - y1
    print(f"区域已锁定。")
    return x1, y1, width, height

def draw_on_screen(contours, img_w, img_h, canvas_rect):
    canvas_x, canvas_y, canvas_w, canvas_h = canvas_rect
    scale = min(canvas_w / img_w, canvas_h / img_h)
    
    # 居中计算
    offset_x = canvas_x + (canvas_w - img_w * scale) / 2
    offset_y = canvas_y + (canvas_h - img_h * scale) / 2
    
    print("\n" + "="*30)
    print("   进入【人机协作】模式")
    print("   逻辑：移到起点 -> 你按住 -> 我画 -> 你松开")
    print("="*30)
    print("3秒后开始...")
    time.sleep(3)
    
    total = len(contours)
    
    for i, contour in enumerate(contours):
        start_point = contour[0][0]
        sx = int(start_point[0] * scale + offset_x)
        sy = int(start_point[1] * scale + offset_y)
        
        pyautogui.moveTo(sx, sy)
        
        print(f"[{i+1}/{total}] 到达起点 -> 请按住！ (2秒后走)")
        time.sleep(2.0) 
        
        for point in contour[1::3]: 
            px, py = point[0]
            screen_x = int(px * scale + offset_x)
            screen_y = int(py * scale + offset_y)
            
            pyautogui.moveTo(screen_x, screen_y, duration=0.01)
        
        print(f"   段落结束 -> 请松开")
        
        time.sleep(1.5) 

    print("\n所有线条绘制完成！")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, "image.jpg") 

    contours, w, h = get_image_contours(image_path)
    
    if contours:
        print(f"发现 {len(contours)} 个主要绘图区域。")
        canvas_area = calibrate_canvas()
        draw_on_screen(contours, w, h, canvas_area)