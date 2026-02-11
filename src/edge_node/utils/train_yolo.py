import os
import yaml
from ultralytics import YOLO

# === 1. 路径配置 (自动锚定) ===
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 找到 dataset 目录 (src/edge_node/dataset)
DATASET_DIR = os.path.join(os.path.dirname(CURRENT_DIR), "dataset")
IMAGES_DIR = os.path.join(DATASET_DIR, "images")

# 确保输出目录存在
MODELS_DIR = os.path.join(os.path.dirname(CURRENT_DIR), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

def train():
    print(f"🚀 [Init] 准备训练，数据集路径: {DATASET_DIR}")

    # === 2. 动态生成 data.yaml ===
    # YOLO 需要一个 yaml 文件告诉它图片在哪，有多少类
    yaml_path = os.path.join(DATASET_DIR, "data.yaml")
    
    yaml_content = {
        'path': DATASET_DIR,    # 根目录
        'train': 'images',      # 训练集 (我们偷懒，训练集=验证集)
        'val': 'images',        # 验证集
        'nc': 2,                # 类别数量
        'names': ['flavor', 'date'] # 类别名称 (0, 1)
    }
    
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_content, f)
    print(f"✅ [Config] data.yaml 已生成")

    # === 3. 加载模型 ===
    # yolov8n.pt 是最轻量级的模型 (Nano版本)，只有 6MB，CPU 也能跑
    print("⏳ [Load] 加载 YOLOv8 Nano 模型...")
    model = YOLO('yolov8n.pt') 

    # === 4. 开始训练 (Training) ===
    print("\n🔥 [Train] 开始炼丹！(这可能需要 10-20 分钟，取决于你的电脑性能)")
    print("    请耐心等待，直到进度条走完...")
    
    # epochs=20: 训练 20 轮 (对于简单任务够了)
    # imgsz=640: 图片大小
    # device='cpu': 强制使用 CPU (防止你没装 CUDA 报错)
    results = model.train(
        data=yaml_path, 
        epochs=20, 
        imgsz=640, 
        device='cpu', # 如果你有 N卡，这里改成 '0' 会起飞
        project=os.path.join(CURRENT_DIR, 'runs'), # 临时训练日志放这里
        name='mini_mes_v1',
        exist_ok=True
    )
    
    print("\n✅ [Finish] 训练完成！")

    # === 5. 导出为 ONNX (Export) ===
    print("📦 [Export] 正在导出为 ONNX 格式...")
    # opset=12 是兼容性最好的版本
    success = model.export(format='onnx', opset=12)
    
    # === 6. 搬运结果 ===
    # 导出后的文件默认在 runs 目录深处，我们把它拷出来
    exported_path = str(success) # export 返回的是路径
    final_path = os.path.join(MODELS_DIR, "best.onnx")
    
    # 简单的文件移动/重命名逻辑
    import shutil
    shutil.move(exported_path, final_path)
    
    print("-" * 40)
    print(f"🎉 恭喜！模型已就绪！")
    print(f"💾 模型文件: {final_path}")
    print("-" * 40)

if __name__ == "__main__":
    train()