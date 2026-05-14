import tensorflow as tf
import numpy as np
import cv2
import os

image_format = ".jpg"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "mobileunet_foot_abnormal.keras")
IMG_SIZE = (224, 224)

# Class mapping
BACKGROUND = 0
FOOT = 1
ABNORMAL = 2

# Foot detection threshold
MIN_FOOT_PIXELS = 3000 

# -------------------------------
# Load model
# -------------------------------
model = tf.keras.models.load_model(MODEL_PATH)
print("deploy.py: Model loaded successfully.")

# -------------------------------
# Preprocess image
# -------------------------------
def preprocess_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    image_resized = cv2.resize(image, IMG_SIZE)
    image_resized = image_resized / 255.0
    image_resized = np.expand_dims(image_resized, axis=0)
    
    return image, image_resized

# -------------------------------
# Run inference
# -------------------------------
def analyze_image(original_image, tensor_image):
    pred = model.predict(tensor_image, verbose=0)[0]
    pred_mask = np.argmax(pred, axis=-1)

    foot_pixels = np.sum(pred_mask == FOOT)
    abnormal_pixels = np.sum(pred_mask == ABNORMAL)
    total_pixels = pred_mask.size

    if foot_pixels < MIN_FOOT_PIXELS:
        return {
            "detected": False,
            "message": "Foot not detected",
            "mask": pred_mask,
            "image": original_image
        }

    abnormal_pct = (abnormal_pixels / foot_pixels) * 100
    
    abnormal_probs = pred[:, :, ABNORMAL]
    abnormal_mask = (pred_mask == ABNORMAL)

    if np.sum(abnormal_mask) == 0:
        abnormal_confidence = 0.0
    else:
        # Average probability of all pixels marked as abnormal
        abnormal_confidence = np.mean(abnormal_probs[abnormal_mask]) * 100

    return {
        "detected": True,
        "abnormal_pct": abnormal_pct,
        "abnormal_confidence": abnormal_confidence,
        "foot_pixels": foot_pixels,
        "mask": pred_mask,
        "image": original_image
    }

# -------------------------------
# Overlay function
# -------------------------------
def overlay_mask(original_image, mask, alpha=0.6):
    color_map = {
        BACKGROUND: (0, 0, 0),
        FOOT: (0, 255, 0),
        ABNORMAL: (0, 0, 255)
    }

    mask_vis = np.zeros((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)
    for k, v in color_map.items():
        mask_vis[mask == k] = v

    mask_vis = cv2.resize(
        mask_vis,
        (original_image.shape[1], original_image.shape[0]),
        interpolation=cv2.INTER_NEAREST
    )

    return cv2.addWeighted(original_image, 1 - alpha, mask_vis, alpha, 0)

# -------------------------------
# Run Full Process
# -------------------------------
def run_full_process(image_path, paths, timestamp, update_status):
    print("Starting deploy.py...")
    
    update_status("AI Process: Resizing Image...")
    original_image, tensor_image = preprocess_image(image_path)
    update_status("Success: AI Resized Image!")
    
    resized_to_save = (tensor_image[0] * 255).astype(np.uint8)
    resized_to_save_bgr = cv2.cvtColor(resized_to_save, cv2.COLOR_RGB2BGR)
    
    resized_filename = f"resized_{timestamp}{image_format}"
    resized_path = os.path.join(paths['resized'], resized_filename)
    cv2.imwrite(resized_path, resized_to_save_bgr)

    update_status("AI Process: Analysing Image...")
    result = analyze_image(original_image, tensor_image)

    if result["detected"] == False:
        update_status("Error: AI could not detect foot.")
        return {
        "detected": result["detected"],
        "percentage": 0,
        "grade": "",
        "confidence": 0,
        "resized_path": "",
        "segmented_path": "",
        "overlayed_path": "",
    }
    
    # Save the raw mask
    mask_visual = cv2.resize((result["mask"] * 120).astype(np.uint8), 
                             (original_image.shape[1], original_image.shape[0]), 
                             interpolation=cv2.INTER_NEAREST)
    segmented_filename = f"segmented_{timestamp}{image_format}"
    segmented_path = os.path.join(paths['segmented'], segmented_filename)
    cv2.imwrite(segmented_path, mask_visual)

    update_status("AI Process: Overlaying Image...")
    overlay = overlay_mask(result["image"], result["mask"])
    
    overlayed_filename = f"overlayed_{timestamp}{image_format}"
    overlayed_path = os.path.join(paths['overlayed'], overlayed_filename)
    cv2.imwrite(overlayed_path, cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
    
    # Grading
    pct = result["abnormal_pct"]
    if pct < 0.5:
        grade = "Likely Normal"
    elif pct < 4.0:
        grade = "Mildly Abnormal"
    elif pct < 10.0:
        grade = "Moderately Abnormal"
    else:
        grade = "Severely Abnormal"

    return {
        "detected": result["detected"],
        "percentage": pct,
        "grade": grade,
        "confidence": result["abnormal_confidence"],
        "resized_path": resized_path,
        "segmented_path": segmented_path,
        "overlayed_path": overlayed_path,
    }
