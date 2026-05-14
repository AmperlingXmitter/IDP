import cv2
import numpy as np
from .mobileunet import mobileunet0
import tensorflow as tf
import os

# -------------------------
# CONFIG
# -------------------------
image_format = ".jpg"
MODEL_PATH = "ImageProcessingAlgorithms/mobileunet_weak_patch.keras"


PATCH = 192
THRESH = 0.5

# -------------------------
# LOAD MODEL
# -------------------------
model = mobileunet0(input_size=(PATCH, PATCH, 3))
model.load_weights(MODEL_PATH)

#==========================
#INPUT
def evaluate(IMAGE_PATH, save_directory, timestamp):
    # LOAD IMAGE
    # -------------------------
    image = cv2.imread(IMAGE_PATH)
    h, w, _ = image.shape

    # normalize
    image_f = image.astype(np.float32) / 255.0

    # -------------------------
    # OUTPUT MASK
    # -------------------------
    prob_mask = np.zeros((h, w), dtype=np.float32)

    total_patches = 0
    positive_patches = 0

    # -------------------------
    # SLIDING WINDOW
    # -------------------------
    for y in range(0, h - PATCH + 1, PATCH):
        for x in range(0, w - PATCH + 1, PATCH):

            patch = image_f[y:y+PATCH, x:x+PATCH]
            patch = np.expand_dims(patch, axis=0)

            pred = model.predict(patch, verbose=0)[0, :, :, 0]

            prob_mask[y:y+PATCH, x:x+PATCH] = pred

            if np.mean(pred) > THRESH:
                positive_patches += 1

            total_patches += 1

    #OUTPUTS
    # -------------------------
    # FINAL METRICS
    # -------------------------
    ratio = positive_patches / total_patches
    # print(f"Detected ratio: {ratio:.4f}")

    # -------------------------
    # SAVE OUTPUTS
    # -------------------------
    binary_mask = (prob_mask > THRESH).astype(np.uint8) * 255

    overlay = image.copy()
    overlay[binary_mask == 255] = (
        0.6 * overlay[binary_mask == 255] +
        0.4 * np.array([0, 0, 255])
    )
    
    mask_path = os.path.join(save_directory, f"mask_{timestamp}{image_format}")
    overlay_path = os.path.join(save_directory, f"overlay_{timestamp}{image_format}")
    
    cv2.imwrite(mask_path, binary_mask)
    cv2.imwrite(overlay_path, overlay)

    # Dictionary
    return {
        "ratio": ratio,
    }

    #OUTPUT
#     cv2.imwrite("probability_mask.png", (prob_mask * 255).astype(np.uint8))
#     cv2.imwrite("binary_mask.png", binary_mask)
#     cv2.imwrite("overlay.png", overlay)
