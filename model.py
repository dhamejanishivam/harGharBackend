import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image
import os

"""
Prections
1 = Munga
0 = Not Munga
"""



class IMAGECLASSIFIER:
    def __init__(self):
        modelPath = 'modelFile/cnn_mobilenetv2_model.h5'
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(CURRENT_DIR, modelPath)
        self.model = load_model(model_path)

    def predict(self, img_path: str) -> tuple[int, int]:
        img = self.preprocess_image(img_path)
        pred = self.model.predict(img, verbose=0)[0]
        pred_value = pred[0] if isinstance(pred, (np.ndarray, list)) else pred
        predicted_class = 1 if pred_value >= 0.5 else 0
        confidence = pred_value if predicted_class == 1 else 1 - pred_value
        confidence_percentage = int(round(confidence * 100))
        return predicted_class, confidence_percentage


    def preprocess_image(self, image_path: str) -> np.ndarray:
        img = Image.open(image_path).convert('RGB')
        img = img.resize((224, 224))
        img = np.array(img) / 255.0
        img = np.expand_dims(img, axis=0)
        return img



"""
if __name__ == "__main__":
    base_folder = 'images/notcorrect'
    full_base_path = '/Users/shivam/Documents/harGharProject/harGharAiModel'
    obj = IMAGECLASSIFIER()

    for filename in os.listdir(os.path.join(full_base_path, base_folder)):
        test_image_path = os.path.join(full_base_path, base_folder, filename)
        result = obj.predict(test_image_path)
        print(result)
        # print(f"Class = {result[0]}, Confidence = {result[1]}%")
"""