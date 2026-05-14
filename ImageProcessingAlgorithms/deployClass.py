import tensorflow as tf
import numpy as np
MODEL_PATH = "ImageProcessingAlgorithms/mobilenetv3_4class_model.keras"
IMG_SIZE = (224, 224)

model = tf.keras.models.load_model(MODEL_PATH)
print("Model loaded successfully")
def load_and_preprocess_image(img_path):
    img = tf.keras.utils.load_img(img_path, target_size=IMG_SIZE)
    img_array = tf.keras.utils.img_to_array(img)
    img_array = img_array / 255.0          # normalization
    img_array = np.expand_dims(img_array, axis=0)  # add batch dimension
    return img_array
# Must match folder order used during training
CLASS_NAMES = ['Grade1', 'Grade2', 'Grade3', 'Grade4']

#======================================

def predict_image(img_path):
    img = load_and_preprocess_image(img_path)
    predictions = model.predict(img)

    class_index = np.argmax(predictions)
    confidence = predictions[0][class_index]

    # Dictionary
    return {
        "class": CLASS_NAMES[class_index],
        "confidence": confidence
    }

#USe this
# def predict_image(img_path):#INPUT
#     img = load_and_preprocess_image(img_path)
#     predictions = model.predict(img)
# 
#     class_index = np.argmax(predictions)#OUTPUT
#     confidence = predictions[0][class_index]#CONFIDENCE
# 
#     print(f"Predicted class: {CLASS_NAMES[class_index]}")
#     print(f"Confidence: {confidence:.2f}")

#======================================
