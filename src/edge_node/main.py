# src/edge_node/main.py
import time
import uuid
import requests
from drivers.dongle import dongle
from drivers.printer import printer
from services.vision import vision_bot

# 假设这是服务器地址（注意：如果是Docker部署，且你在宿主机跑这个脚本，用localhost即可）
API_URL = "http://localhost:8000/api/v1/production/upload"

def production_loop():
    print("--- 🚀 Edge Node Started (Virtual Mode) ---")
    
    while True:
        try:
            # 1. 产生一个新的产品序列号 (模拟 PLC 信号触发)
            sn = f"SN-{uuid.uuid4().hex[:8].upper()}"
            print(f"--- New Cycle: {sn} ---")

            # 2. 加密 (调用虚拟狗)
            cipher = dongle.encrypt(sn)
            
            # 3. 喷码 (调用虚拟打印机)
            printer.print_code(cipher)

            # 4. 视觉核验 (调用虚拟眼)
            result = vision_bot.capture_and_verify(expected_content=cipher)

            if result["success"]:
                # 5. 解密核验 (闭环)
                decoded_sn = dongle.decrypt(result["content"])
                if decoded_sn == sn:
                    # 6. 上传数据
                    payload = {
                        "device_id": "EDGE-001", # 树莓派的ID
                        "sku": "DEMO-PRODUCT",
                        "batch_id": "BATCH-20260208",
                        "quantity": 1
                        # 可以在这里加上 sn 和 cipher 字段，如果后端支持的话
                    }
                    # 真正发送请求给后端
                    # resp = requests.post(API_URL, json=payload)
                    # print(f"☁️ Uploaded: {resp.status_code}")
                    print(f"☁️ [Simulated Upload] Data sent to Server: {sn}")
                else:
                    print("⚠️ Security Alert: Decryption mismatch!")
            
            print("----------------------------------\n")
            time.sleep(3) # 模拟流水线节拍

        except KeyboardInterrupt:
            print("Stop.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    production_loop()