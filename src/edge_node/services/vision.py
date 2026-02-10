import cv2
import time
import zxingcpp
import numpy as np

class VisionService:
    def __init__(self):
        print(f"[Vision] Initializing Vision Engine (Brute Force Mode)...")

    def detect_and_decode(self, image_path: str):
        print(f"--- 🔓 Brute Force Scan: {image_path} ---")
        
        img = cv2.imread(image_path)
        if img is None: return []

        # 1. 基础战术：切图 (只看右下角)
        h, w = img.shape[:2]
        roi = img[int(h*0.4):h, int(w*0.3):w]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # === ⚔️ 生成 12 种变种 (总有一款适合你) ===
        variants = []

        # 变种 1: 原味灰度
        variants.append(("Original Gray", gray))

        # 变种 2: 放大 2 倍 (线性插值，比较柔和)
        zoom2 = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_LINEAR)
        variants.append(("Zoom 2x", zoom2))

        # 变种 3: 放大 3 倍 + 锐化 (模拟微信)
        zoom3 = cv2.resize(gray, None, fx=3.0, fy=3.0, interpolation=cv2.INTER_CUBIC)
        kernel_sharp = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
        zoom3_sharp = cv2.filter2D(zoom3, -1, kernel_sharp)
        variants.append(("Zoom 3x + Sharp", zoom3_sharp))

        # 变种 4-6: 针对“墨水晕染”的杀手锏——【膨胀】(Dilate)
        # 你的条形码大概率是黑条太胖粘在一起了。
        # 膨胀白色区域 = 腐蚀黑色区域 = 让条形码变瘦！
        kernel_slim = np.ones((3,3), np.uint8)
        
        # 试着给原图“瘦身”
        dilated_1 = cv2.dilate(gray, kernel_slim, iterations=1)
        variants.append(("Slimming (Original)", dilated_1))
        
        # 试着给放大图“瘦身” (效果通常最好)
        dilated_zoom = cv2.dilate(zoom2, kernel_slim, iterations=1)
        variants.append(("Slimming (Zoom 2x)", dilated_zoom))

        # 变种 7-9: 疯狂调整对比度 (Gamma)
        # 有时候是因为太暗，有时候是因为太亮
        invGamma_light = 1.0 / 1.5
        table_light = np.array([((i / 255.0) ** invGamma_light) * 255 for i in np.arange(0, 256)]).astype("uint8")
        gamma_light = cv2.LUT(gray, table_light)
        variants.append(("Gamma Light (1.5)", gamma_light))

        invGamma_dark = 1.0 / 0.6
        table_dark = np.array([((i / 255.0) ** invGamma_dark) * 255 for i in np.arange(0, 256)]).astype("uint8")
        gamma_dark = cv2.LUT(gray, table_dark)
        variants.append(("Gamma Dark (0.6)", gamma_dark))

        # 变种 10-12: 暴力二值化 (Threshold)
        # 尝试不同的阈值，万一瞎猫碰到死耗子呢
        _, thresh_100 = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY) # 只有很黑的才算黑
        variants.append(("Thresh 100", thresh_100))
        
        _, thresh_180 = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY) # 稍微黑一点就算黑
        variants.append(("Thresh 180", thresh_180))

        # === 🚀 挨个试！ ===
        results = []
        found_it = False

        for name, variant_img in variants:
            # 这种暴力尝试很快，几十毫秒就跑完了
            try:
                codes = zxingcpp.read_barcodes(variant_img)
                if codes:
                    print(f"   🎉 SUCCESS! Strategy [{name}] worked!")
                    # 保存这张立功的图片，让我们死个明白
                    cv2.imwrite(image_path.replace(".jpg", f"_success_{name.replace(' ','_')}.jpg"), variant_img)
                    
                    for obj in codes:
                        print(f"      👉 Content: {obj.text}")
                        results.append({
                            "content": obj.text,
                            "type": str(obj.format),
                            "strategy": name,
                            "timestamp": time.time()
                        })
                    found_it = True
                    break # 找到了就收工！
            except:
                pass
        
        if not found_it:
            print("❌ All 12 strategies failed. The image is officially cursed.")

        return results

vision_bot = VisionService()