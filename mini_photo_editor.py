import numpy as np
import cv2
from PIL import Image

def to_bgr(pil_img):
    img = np.array(pil_img)
    if img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    else:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img

def to_rgb(cv_img):
    return cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)



def adjust_brightness(img, brightness=0):
    # alpha = 1.0  # no changes to the current image
    # beta = 0.0 # no second image
    # gamma = brightness # how much constant value we wanna add
    # bright_image =  cv2.addWeighted(img, alpha, img, beta, gamma)
    bright_image = cv2.convertScaleAbs(img, alpha=1.0, beta=brightness)

    return bright_image

def adjust_contrast(img, contrast=0):
    # alpha = contrast  # no changes to the current image
    # beta = 0.0 # no second image
    # gamma = 0 # no Scalar value needed
    # contrast_image =  cv2.addWeighted(img, alpha, img, beta, gamma)
    contrast_image =  cv2.convertScaleAbs(img, alpha=contrast, beta=0)
    return contrast_image

def convert_grayscale(img):
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray_image


def adjust_padding(img, padding=0, border_type='constant', aspect_ratio=None, custom_ratio=None):
    h, w = img.shape[:2]
    pad_top = pad_bottom = pad_left = pad_right = 0

    if aspect_ratio == 'square':
        max_side = max(h, w)
        pad_vert = max_side - h
        pad_horz = max_side - w
        pad_top += pad_vert // 2
        pad_bottom += pad_vert - pad_top
        pad_left += pad_horz // 2
        pad_right += pad_horz - pad_left

    elif aspect_ratio == 'rectangle':
        target_ratio = 4 / 3
        current_ratio = w / h
        if current_ratio < target_ratio:
            # Image too narrow → add width
            new_w = int(h * target_ratio)
            pad_horz = new_w - w
            pad_left += pad_horz // 2
            pad_right += pad_horz - pad_left
        else:
            # Image too wide → add height
            new_h = int(w / target_ratio)
            pad_vert = new_h - h
            pad_top += pad_vert // 2
            pad_bottom += pad_vert - pad_top

    elif aspect_ratio == 'custom' and custom_ratio:
        try:
            x, y = map(float, custom_ratio.split(":"))
            target_ratio = x / y
            current_ratio = w / h
            if current_ratio < target_ratio:
                # Too narrow → add width
                new_w = int(h * target_ratio)
                extra_w = new_w - w
                pad_left += extra_w // 2
                pad_right += extra_w - pad_left
            else:
                # Too wide → add height
                new_h = int(w / target_ratio)
                extra_h = new_h - h
                pad_top += extra_h // 2
                pad_bottom += extra_h - pad_top
        except Exception as e:
            print("Invalid custom ratio:", e)

    # Add extra user-defined padding 
    pad_top += padding
    pad_bottom += padding
    pad_left += padding
    pad_right += padding

    border_dict = {
        'constant': cv2.BORDER_CONSTANT,
        'reflect': cv2.BORDER_REFLECT,
        'replicate': cv2.BORDER_REPLICATE,
        'wrap': cv2.BORDER_WRAP
    }
    border = border_dict.get(border_type, cv2.BORDER_CONSTANT)
    value = [0, 0, 255]  # Red border if constant

    padded_img = cv2.copyMakeBorder(img, pad_top, pad_bottom, pad_left, pad_right, border, value=value)
    return padded_img

def threshold_image(img, thresh_val=127, mode='binary'):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if mode == 'binary':
        _, thresh_img = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
    else:
        _, thresh_img = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY_INV)
    
    return cv2.cvtColor(thresh_img, cv2.COLOR_GRAY2BGR)

def blend_images(img1, img2, alpha=0.5):
    h1, w1 = img1.shape[:2]
    img2 = cv2.resize(img2, (w1, h1))
    blended = cv2.addWeighted(img1, alpha, img2, 1 - alpha, 0)
    return blended
