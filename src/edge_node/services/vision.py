# src/edge_node/services/vision.py
import time
import random

class VisionService:
    def __init__(self):
        print("[Vision] Loading YOLO model (Mock)...")

    def capture_and_verify(self, expected_content: str) -> dict:
        """
        模拟：拍照 -> 识别 -> 校验
        在真实场景中，这里会调用 cv2.VideoCapture 和 onnxruntime
        """
        print(">>> 📷 [HARDWARE ACTION] Camera is capturing...")
        time.sleep(0.5) # 模拟处理时间
        
        # 90% 概率识别成功，10% 模拟脏污无法识别
        if random.random() > 0.1:
            print(f">>> 👁️ AI Detected: {expected_content}")
            return {"success": True, "content": expected_content}
        else:
            print(">>> ❌ AI Failed: Code unobtainable or blurred.")
            return {"success": False, "content": None}

vision_bot = VisionService()