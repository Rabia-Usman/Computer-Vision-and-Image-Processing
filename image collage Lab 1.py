# -*- coding: utf-8 -*-
"""
Created on Sat Jan 27 17:10:30 2024

@author: Hp
"""
import sys
sys.path.append('C:\\Users\\Hp\\AppData\\Local\\Programs\\Python\\Python310\\Lib\\site-packages')
import cv2
import numpy as np

def resize_image(image, target_size):
    # Resize the image while maintaining the aspect ratio
    return cv2.resize(image, target_size)

def create_collage(images, rows, cols):
    collage_height = sum(image.shape[0] for image in images) // rows
    collage_width = sum(image.shape[1] for image in images) // cols

    collage = np.zeros((collage_height, collage_width, 3), dtype=np.uint8)

    row_start = 0
    col_start = 0

    for image in images:
        resized_image = resize_image(image, (collage_width // cols, collage_height // rows))

        collage[row_start:row_start + resized_image.shape[0], col_start:col_start + resized_image.shape[1]] = resized_image

        col_start += resized_image.shape[1]
        if col_start >= collage_width:
            col_start = 0
            row_start += resized_image.shape[0]

    return collage

if __name__ == "__main__":
    # Example usage
    image_paths = ["D:\\image1.png", "D:\\image2.jpeg", "D:\\image1_gray.png"]  # Replace with your image paths
    images = [cv2.imread(image_path) for image_path in image_paths]

    # Specify the number of rows and columns in the collage grid
    rows = 2
    cols = 2

    collage = create_collage(images, rows, cols)

    # Display the result
    cv2.imshow("Collage", collage)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
