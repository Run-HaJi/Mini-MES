# src/edge_node/drivers/dongle.py
import base64

class DongleDriver:
    def __init__(self):
        print("[Dongle] Initializing virtual security chip...")
        self.is_connected = True

    def encrypt(self, text: str) -> str:
        """模拟硬件加密: 其实就是转成 base64"""
        if not self.is_connected:
            raise Exception("Dongle not found!")
        # 模拟耗时
        return base64.b64encode(text.encode()).decode()

    def decrypt(self, cipher: str) -> str:
        """模拟硬件解密"""
        if not self.is_connected:
            raise Exception("Dongle not found!")
        return base64.b64decode(cipher.encode()).decode()

# 单例模式
dongle = DongleDriver()