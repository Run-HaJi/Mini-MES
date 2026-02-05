import time
import random
import requests
import json
import sys
from datetime import datetime

# 🔒 引入加密库
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
import base64

# ================= 配置区 =================
# 目标服务器地址
SERVER_URL = "http://localhost:8000/api/v1/data/upload"

# 🔑 最高机密 (必须与后端完全一致)
# AES-256 需要 32 字节密钥
SECRET_KEY = b"MiniMES_2026_Ver0.4_Secure_Key!!" 
# 固定 IV (实际生产应随机生成，这里为了简化先固定)
IV = b"MiniMES_IV_2026!"

# 模拟设备信息
DEVICE_ID = "PRESS-001"
LINE_ID = "LINE-A"

def encrypt_payload(data_dict):
    """
    加密函数：把字典 -> JSON字符串 -> 加密 -> Base64字符串
    """
    try:
        # 1. 字典转 JSON 字符串
        json_str = json.dumps(data_dict)
        
        # 2. 创建加密器 (CBC模式)
        cipher = AES.new(SECRET_KEY, AES.MODE_CBC, IV)
        
        # 3. 填充 (Padding) 并加密
        # AES 加密的数据长度必须是 16 的倍数，所以要 pad
        ciphertext = cipher.encrypt(pad(json_str.encode('utf-8'), AES.block_size))
        
        # 4. 转 Base64 (方便网络传输)
        return base64.b64encode(ciphertext).decode('utf-8')
    except Exception as e:
        print(f"❌ 加密失败: {e}")
        return None

def generate_mock_data():
    """生成模拟生产数据"""
    return {
        "sku": "Test-Metal-Part",
        "weight": round(random.uniform(498.0, 502.0), 2),
        "temperature": random.randint(45, 80),
        "pressure": round(random.uniform(10.0, 12.0), 1),
        "vibration": round(random.uniform(0.1, 0.5), 3)
    }

def run_client():
    print(f"🚀 边缘采集端启动 (加密模式)...")
    print(f"📡 目标服务器: {SERVER_URL}")
    print(f"🔒 使用密钥: {SECRET_KEY.decode()}")
    print("-" * 50)

    try:
        while True:
            # 1. 生成原始数据
            raw_data = generate_mock_data()
            
            # 2. 🔒 加密 Payload
            encrypted_payload = encrypt_payload(raw_data)
            
            if not encrypted_payload:
                continue

            # 3. 构造请求体
            # 注意：现在的 payload 字段不再是字典，而是一串乱码字符串
            post_data = {
                "line_id": LINE_ID,
                "device_id": DEVICE_ID,
                "operator_id": "OP-9527",
                "source_type": "MOCK_CLIENT_V0.4",
                "timestamp": datetime.now().isoformat(),
                "payload": encrypted_payload  # <--- 这里是密文！
            }

            # 4. 发送
            print(f"\n[生成] 原始数据: {raw_data}")
            print(f"[加密] 发送密文: {encrypted_payload[:20]}...... (已隐去后半段)")
            
            try:
                resp = requests.post(SERVER_URL, json=post_data, timeout=2)
                if resp.status_code == 200:
                    print(f"✅ 上传成功: ID={resp.json().get('data', {}).get('record_id')}")
                else:
                    # 预期内：因为后端还没写解密逻辑，现在肯定会报错 422 或 500
                    print(f"⚠️ 服务器响应异常 (正常现象，等待后端升级): {resp.status_code} - {resp.text}")
            except Exception as e:
                print(f"❌ 网络错误: {e}")

            # 模拟生产节拍 (2秒一次)
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n🛑 采集端已停止")

if __name__ == "__main__":
    run_client()