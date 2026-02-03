import time
import random
import requests
import json
from datetime import datetime

# --- 配置区 ---
SERVER_URL = "http://localhost:8000/api/v1/data/upload"
DEVICE_ID = "PRESS-001"  # 模拟一台冲压机
LINE_ID = "LINE-A"

def generate_mock_data():
    """生成模拟的工业数据"""
    # 模拟偶尔出现的不良品 (重量偏差)
    base_weight = 500.0
    variation = random.uniform(-2.0, 2.0)
    
    # 构造我们要上传的 JSON
    data = {
        "line_id": LINE_ID,
        "device_id": DEVICE_ID,
        "operator_id": "OP-9527",
        "source_type": "SIMULATOR",
        "timestamp": int(time.time()), # 边缘端的时间戳
        "payload": {
            "sku": "Test-Metal-Part",
            "weight": round(base_weight + variation, 2),
            "temperature": random.randint(45, 80), # 模拟设备温度
            "status": "OK" if abs(variation) < 1.5 else "NG" # 简单的边缘判定逻辑
        }
    }
    return data

def run_client():
    print(f"🚀 设备 [{DEVICE_ID}] 启动，准备向 {SERVER_URL} 发送数据...")
    
    while True:
        try:
            # 1. 生成数据
            payload = generate_mock_data()
            
            # 2. 发送请求
            # timeout=2 很重要，防止网络卡死脚本
            response = requests.post(SERVER_URL, json=payload, timeout=2)
            
            # 3. 打印结果
            if response.status_code == 200:
                print(f"✅ [上传成功] {payload['payload']['weight']}g | 温度: {payload['payload']['temperature']}°C")
            else:
                print(f"⚠️ [服务器拒绝] {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ [连接失败] 服务器好像没开？(尝试重连中...)")
        except Exception as e:
            print(f"❌ [未知错误] {e}")
            
        # 4. 休息 3 秒再发下一次
        time.sleep(3)

if __name__ == "__main__":
    run_client()