import cv2
import numpy as np
import logging
import os

# 尝试导入 onnxruntime
try:
    import onnxruntime as ort
    HAS_ORT = True
except ImportError:
    HAS_ORT = False

logger = logging.getLogger("yolo")

class YoloEngine:
    def __init__(self, model_path="models/best.onnx", conf_thres=0.5, iou_thres=0.5):
        """
        初始化 YOLO ONNX 引擎
        model_path: 模型路径
        conf_thres: 置信度阈值 (低于这个分数的框不要)
        iou_thres:  重叠度阈值 (两个框重叠太厉害就删掉一个)
        """
        self.model_path = model_path
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self.session = None
        
        # 类别名称 (必须和训练时的顺序一致: 0=flavor, 1=date)
        self.classes = {0: "flavor", 1: "date"}

        if not os.path.exists(model_path) or not HAS_ORT:
            self.simulate_mode = True
            logger.warning(f"⚠️ [YOLO] 未找到模型 {model_path}，启动 [仿真模式]")
        else:
            self.simulate_mode = False
            try:
                # 加载模型到内存
                self.session = ort.InferenceSession(model_path)
                
                # 获取输入输出节点的名称
                self.input_name = self.session.get_inputs()[0].name
                self.output_name = self.session.get_outputs()[0].name
                
                # 获取模型期待的输入尺寸 (通常是 640x640)
                self.input_shape = self.session.get_inputs()[0].shape # [1, 3, 640, 640]
                self.img_size = self.input_shape[2] 
                
                logger.info(f"✅ [YOLO] 模型加载成功! 输入尺寸: {self.img_size}x{self.img_size}")
            except Exception as e:
                logger.error(f"❌ [YOLO] 模型加载失败: {e}")
                self.simulate_mode = True

    def detect(self, image_path):
        """
        输入: 图片路径
        输出: list of dict [{'class_id': 0, 'box': [x,y,w,h], 'conf': 0.95}, ...]
        """
        if self.simulate_mode:
            return self._mock_inference(image_path)

        # 1. 读取图片
        src_img = cv2.imread(image_path)
        if src_img is None:
            logger.error(f"无法读取图片: {image_path}")
            return []

        # 2. 预处理 (Pre-process)
        # 把图片缩放、填充黑边到 640x640，并归一化
        blob, ratio, dwdh = self._preprocess(src_img)

        # 3. 推理 (Inference) - 核心一步
        outputs = self.session.run([self.output_name], {self.input_name: blob})[0]
        # outputs 形状通常是 [1, 6, 8400] (4个坐标+2个类别概率, 8400个框)

        # 4. 后处理 (Post-process)
        # 解析输出，去掉重叠框 (NMS)
        results = self._postprocess(outputs, ratio, dwdh)
        
        return results

    def _preprocess(self, img):
        """把任意尺寸图片处理成 YOLO 需要的 640x640"""
        image = img.copy()
        h, w = image.shape[:2]
        
        # 计算缩放比例
        scale = min(self.img_size / h, self.img_size / w)
        inp_h, inp_w = int(h * scale), int(w * scale)
        image = cv2.resize(image, (inp_w, inp_h))
        
        # 填充黑边 (Padding)
        dw, dh = self.img_size - inp_w, self.img_size - inp_h
        dw, dh = dw / 2, dh / 2  # 居中填充
        
        # cv2.copyMakeBorder 需要上下左右的像素数
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        image = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114))
        
        # 转换格式: HWC -> CHW, BGR -> RGB, 0-255 -> 0.0-1.0
        image = image.transpose((2, 0, 1))[::-1] # BGR to RGB, to 3x640x640
        image = np.ascontiguousarray(image)
        image = image.astype(np.float32) / 255.0
        image = image[None] # 增加 batch 维度: [1, 3, 640, 640]
        
        return image, (scale, scale), (dw, dh)

    def _postprocess(self, outputs, ratio, dwdh):
        """解析 YOLO 输出的乱码，还原成真实坐标"""
        # outputs shape: [1, 4+nc, 8400] -> 转置为 [1, 8400, 4+nc]
        predictions = np.transpose(outputs, (0, 2, 1))
        prediction = predictions[0] # 取第一个 batch

        boxes = []
        confidences = []
        class_ids = []

        # 遍历所有 8400 个预测框 (这里可以用 numpy 加速，但为了好懂先用循环)
        # YOLOv8 输出前4个是 cx, cy, w, h，后面是各类别概率
        
        # 优化: 利用 numpy 批量筛选置信度
        scores = np.max(prediction[:, 4:], axis=1) # 每一行的最大概率
        mask = scores > self.conf_thres            # 筛选出大于阈值的行
        
        valid_preds = prediction[mask]
        valid_scores = scores[mask]
        valid_class_ids = np.argmax(valid_preds[:, 4:], axis=1) # 每一行的最大概率对应的索引
        valid_boxes = valid_preds[:, :4]

        for i in range(len(valid_preds)):
            # 解析坐标 cx, cy, w, h
            cx, cy, w, h = valid_boxes[i]
            
            # 还原到原图尺寸 (减去 padding，除以缩放比例)
            rx, ry = ratio
            pad_w, pad_h = dwdh
            
            x = (cx - w / 2 - pad_w) / rx
            y = (cy - h / 2 - pad_h) / ry
            w = w / rx
            h = h / ry
            
            boxes.append([int(x), int(y), int(w), int(h)])
            confidences.append(float(valid_scores[i]))
            class_ids.append(int(valid_class_ids[i]))

        # NMS (非极大值抑制) - 去掉重叠的框
        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.conf_thres, self.iou_thres)
        
        results = []
        if len(indices) > 0:
            for i in indices.flatten():
                results.append({
                    "class_id": class_ids[i],
                    "class_name": self.classes.get(class_ids[i], "unknown"),
                    "conf": round(confidences[i], 2),
                    "box": boxes[i] # [x, y, w, h]
                })
        
        return results

    def _mock_inference(self, image_path):
        """仿真逻辑 (备用)"""
        import time
        time.sleep(0.02) # 模拟 20ms 耗时
        return [
            {"class_id": 0, "class_name": "flavor", "conf": 0.99, "box": [100, 100, 200, 100]},
            {"class_id": 1, "class_name": "date",   "conf": 0.95, "box": [300, 400, 150, 40]}
        ]