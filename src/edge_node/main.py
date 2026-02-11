import time
import os
import cv2
import sys
import logging

# === 关键：先让 Python 能找到同级模块 ===
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)

from services.yolo_service import YoloEngine
from services.ocr_service import DateReader

def main():
    print("🚀 Mini-MES Edge Node v0.9 (YOLO Architecture) Starting...")

    # === 关键修复：使用绝对路径锚定模型 ===
    # 无论你在哪里运行命令，这行代码都能精准定位到 src/edge_node/models/best.onnx
    model_path = os.path.join(CURRENT_DIR, "models", "yolo_v8_n.onnx")
    
    print(f"🔎 正在加载模型: {model_path}")

    # 初始化引擎，传入绝对路径
    yolo = YoloEngine(model_path=model_path)
    ocr = DateReader()

    # 准备测试图
    img_path = os.path.join(CURRENT_DIR, "assets", "target_sample.jpg")
    
    if not os.path.exists(img_path):
        print("⚠️ 没找到测试图，生成一张黑图用于测试流程")
        dummy = np.zeros((640, 640, 3), dtype=np.uint8)
        cv2.imwrite(img_path, dummy)

    while True:
        input("👉 按回车键模拟一次传感器触发 (Trigger)...")
        start_time = time.time()

        # === A. 拍照/读取 ===
        # 注意：这里未来要换成 camera.capture()
        if os.path.exists(img_path):
            frame = cv2.imread(img_path)
        else:
            print("❌ 图片又不见了！")
            continue
        
        # === B. YOLO 检测 (看图) ===
        detections = yolo.detect(img_path)
        
        flavor_result = "Unknown"
        date_result = "Unknown"

        # === C. 结果分拣 ===
        for item in detections:
            cls_id = item['class_id']
            box = item['box']
            conf = item['conf']

            # 策略 1: 口味 (直接分类)
            if cls_id == 0:
                flavor_result = item['class_name'] 
                print(f"   🍓 检测到口味: {flavor_result} (置信度: {conf:.2f})")

            # 策略 2: 日期 (定位 -> 抠图 -> 识别)
            elif cls_id == 1:
                print(f"   📅 发现日期区域，坐标: {box}")
                date_text = ocr.read_date(frame, box)
                if date_text:
                    date_result = date_text
                    print(f"      ✅ 日期读取结果: {date_result}")

        # === D. 数据上报 (Mock) ===
        payload = {
            "product": flavor_result,
            "batch_date": date_result,
            "timestamp": time.time()
        }
        
        cost = (time.time() - start_time) * 1000
        print(f"✨ 流程结束 | 耗时: {cost:.2f}ms | 数据: {payload}")
        print("-" * 40)

if __name__ == "__main__":
    import numpy as np 
    main()