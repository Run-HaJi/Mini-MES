import cv2
import numpy as np
import os
import random

# === 路径配置修正 ===
# 1. 获取当前脚本所在目录 (.../src/edge_node/utils)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. 获取 edge_node 目录 (.../src/edge_node)
EDGE_NODE_DIR = os.path.dirname(CURRENT_DIR)

# 3. 定义资源路径 (输入)
ASSETS_DIR = os.path.join(EDGE_NODE_DIR, "assets")

# 4. === 关键修改：输出路径改为 edge_node/dataset ===
OUTPUT_DIR = os.path.join(EDGE_NODE_DIR, "dataset") 

print(f"📍 脚本位置: {CURRENT_DIR}")
print(f"🔎 寻找素材: {ASSETS_DIR}")
print(f"💾 输出目录: {OUTPUT_DIR}")  # 确认一下是不是这里

# === 下面的逻辑保持不变 ===
IMG_COUNT = 50         
IMG_SIZE = 640         

CLASSES = ["flavor", "date"] 
SEEDS = {
    "flavor": os.path.join(ASSETS_DIR, "seed_flavor.png"),
    "date":   os.path.join(ASSETS_DIR, "seed_date.png")
}

def create_dirs():
    os.makedirs(os.path.join(OUTPUT_DIR, "images"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "labels"), exist_ok=True)

def random_augment(img):
    h, w = img.shape[:2]
    
    # 随机缩放
    scale = random.uniform(0.5, 1.5)
    new_w, new_h = int(w * scale), int(h * scale)
    img = cv2.resize(img, (new_w, new_h))
    
    # 随机旋转
    center = (new_w // 2, new_h // 2)
    angle = random.uniform(-15, 15)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    img = cv2.warpAffine(img, M, (new_w, new_h), borderValue=(200,200,200))
    
    # 随机亮度
    value = random.randint(-50, 50)
    img = img.astype(np.int16) + value
    img = np.clip(img, 0, 255).astype(np.uint8)
    
    return img

def create_background():
    bg = np.zeros((IMG_SIZE, IMG_SIZE, 3), dtype=np.uint8)
    # 模拟纸箱颜色
    bg[:] = (random.randint(140, 180), random.randint(170, 210), random.randint(200, 240))
    # 加噪点
    noise = np.random.randint(0, 30, (IMG_SIZE, IMG_SIZE, 3), dtype=np.uint8)
    bg = cv2.add(bg, noise)
    return bg

def generate():
    # 检查种子文件
    for name, path in SEEDS.items():
        if not os.path.exists(path):
            print(f"❌ 错误：找不到种子文件: {path}")
            return

    create_dirs()
    
    # 生成 classes.txt
    with open(os.path.join(OUTPUT_DIR, "classes.txt"), "w") as f:
        f.write("\n".join(CLASSES))

    total_generated = 0
    
    for class_id, class_name in enumerate(CLASSES):
        seed_path = SEEDS[class_name]
        seed_img = cv2.imread(seed_path)
        
        if seed_img is None:
             print(f"❌ 读取失败: {seed_path}")
             continue

        print(f"🚀 正在生成类别 [{class_name}] ...")
        
        for i in range(IMG_COUNT):
            bg = create_background()
            target = random_augment(seed_img)
            t_h, t_w = target.shape[:2]
            
            if t_w >= IMG_SIZE: 
                scale = (IMG_SIZE - 20) / t_w
                target = cv2.resize(target, (0,0), fx=scale, fy=scale)
                t_h, t_w = target.shape[:2]

            x_offset = random.randint(0, IMG_SIZE - t_w - 1)
            y_offset = random.randint(0, IMG_SIZE - t_h - 1)
            
            bg[y_offset:y_offset+t_h, x_offset:x_offset+t_w] = target
            
            center_x = (x_offset + t_w / 2) / IMG_SIZE
            center_y = (y_offset + t_h / 2) / IMG_SIZE
            norm_w = t_w / IMG_SIZE
            norm_h = t_h / IMG_SIZE
            
            filename = f"{class_name}_{i:03d}"
            
            cv2.imwrite(os.path.join(OUTPUT_DIR, "images", filename + ".jpg"), bg)
            with open(os.path.join(OUTPUT_DIR, "labels", filename + ".txt"), "w") as f:
                f.write(f"{class_id} {center_x:.6f} {center_y:.6f} {norm_w:.6f} {norm_h:.6f}")
            
            total_generated += 1

    print(f"\n✅ 数据集生成完毕！共 {total_generated} 张。")
    print(f"📂 保存在: {os.path.abspath(OUTPUT_DIR)}")

if __name__ == "__main__":
    generate()