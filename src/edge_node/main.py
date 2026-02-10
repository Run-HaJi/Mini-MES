import time
import os
import requests
from services.vision import vision_bot

# 配置
SERVER_URL = "http://localhost:8000/api/v1/production/upload_batch" # 注意：后端可能需要写个批量接口
TEST_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "assets/test_batch.jpg") # 这是我们刚才生成的测试条码图像

def edge_loop():
    print("🚀 Edge Node v0.9 (Vision Only) Started...")
    print(f"📂 Watching Target: {TEST_IMAGE_PATH}")

    while True:
        try:
            # 1. 模拟触发 (比如光电传感器信号)
            # 在真实场景下，这里会等待 GPIO 信号
            print("\nWAITING FOR TRIGGER...")
            time.sleep(2) 
            
            # 2. 视觉识别 (调用刚才写的 VisionService)
            codes = vision_bot.detect_and_decode(TEST_IMAGE_PATH)

            if codes:
                # 3. 数据打包 (根据 Mentor 的要求，上传识别到的所有码)
                payload = {
                    "device_id": "EDGE-IPC-001",
                    "batch_time": time.time(),
                    "scanned_items": codes # 把列表传上去
                }

                # 4. 上传 (暂时打印出来，不真发，防止报错)
                print(f"☁️ [Simulated Upload] Uploading {len(codes)} items to Server...")
                # try:
                #     resp = requests.post(SERVER_URL, json=payload)
                #     print(f"   Server Response: {resp.status_code}")
                # except Exception as e:
                #     print(f"   Upload Failed: {e}")

            else:
                print("💤 No valid codes found in this cycle.")

            # 模拟流水线移动时间
            time.sleep(3)

        except KeyboardInterrupt:
            print("\n🛑 Stopping Edge Node.")
            break
        except Exception as e:
            print(f"❌ Critical Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    edge_loop()