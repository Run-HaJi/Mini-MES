# src/edge_node/drivers/printer.py
import time

class PrinterDriver:
    def __init__(self, port="COM1"):
        print(f"[Printer] Connecting to virtual printer on {port}...")

    def print_code(self, content: str):
        """模拟喷码动作"""
        print(f"\n>>> 🖨️ [HARDWARE ACTION] PRINTER IS PRINTING: [{content}]")
        time.sleep(0.5) # 模拟喷码耗时
        print(">>> ✅ Print Complete.\n")

# 单例
printer = PrinterDriver()