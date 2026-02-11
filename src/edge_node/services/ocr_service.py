import cv2
import numpy as np
import logging
import time

# 尝试导入真实 OCR 库
try:
    from rapidocr_onnxruntime import RapidOCR
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

logger = logging.getLogger("ocr")

class DateReader:
    def __init__(self):
        """
        初始化真实 OCR 引擎
        """
        if HAS_OCR:
            # 实例化 OCR 引擎
            # det_use=False: 因为 YOLO 已经帮我们找到位置了，我们只需要识别(Rec)，不需要再检测(Det)
            # 这样速度会快一倍
            self.ocr_engine = RapidOCR(det_use=False) 
            logger.info("✅ RapidOCR 引擎已加载 (纯识别模式)")
        else:
            logger.error("❌ 未安装 rapidocr_onnxruntime，请执行 pip install rapidocr_onnxruntime")
            self.ocr_engine = None

    def read_date(self, image, bbox):
        if image is None or self.ocr_engine is None: return None
        
        x, y, w, h = bbox
        img_h, img_w = image.shape[:2]
        
        # 1. 抠图
        pad = 5
        x1 = max(0, x - pad)
        y1 = max(0, y - pad)
        x2 = min(img_w, x + w + pad)
        y2 = min(img_h, y + h + pad)
        
        roi = image[y1:y2, x1:x2]
        if roi.size == 0: return None

        # 2. 转灰度
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # 3. 推理
        start_t = time.time()
        result, _ = self.ocr_engine(gray) 
        cost = (time.time() - start_t) * 1000
        
        # 4. === 针对 RapidOCR 列表格式的最终修复 ===
        if result:
            # 调试日志保留，万一还有问题能看
            # print(f"🐛 [DEBUG] OCR原始返回: {result}")

            detected_texts = []
            
            # 遍历所有识别到的片段
            for item in result:
                # item 结构通常是: [坐标, 文本, 置信度]
                if len(item) >= 2:
                    text = item[1] # 取文本
                    # 只要是字符串，就收录进来
                    if isinstance(text, str):
                        detected_texts.append(text)
            
            # 把所有片段拼成一句话，例如 "生产" + "日期:2025" + "99" + "/08"
            full_text = "".join(detected_texts)
            
            if full_text:
                # 过滤掉非字符的杂质，只保留关键信息
                print(f"   👁️ [OCR实测] 拼合结果: '{full_text}' (耗时: {cost:.2f}ms)")
                return full_text

        return None