import os
import re

import cv2
import numpy as np


def round_corners(image, r, t, c):
	"""
	:param image: image as NumPy array
	:param r: radius of rounded corners
	:param t: thickness of border
	:param c: color of border
	:return: new image as NumPy array with rounded corners
	"""
	# thickness for drawing lines must be greater than 0
	dt = max(1, t)

	c += (255,)

	h, w = image.shape[:2]

	# Create new image (three-channel hardcoded here...)
	new_image = np.ones((h + 2 * t, w + 2 * t, 4), np.uint8) * 255
	new_image[:, :, 3] = 0

	mask = new_image[:, :, 3].copy()

	# Draw four rounded corners
	new_image = cv2.ellipse(new_image, (int(r + t / 2), int(r + t / 2)), (r, r), 180, 0, 90, c, dt)
	new_image = cv2.ellipse(new_image, (int(w - r + 3 * t / 2 - 1), int(r + t / 2)), (r, r), 270, 0, 90, c, dt)
	new_image = cv2.ellipse(new_image, (int(r + t / 2), int(h - r + 3 * t / 2 - 1)), (r, r), 90, 0, 90, c, dt)
	new_image = cv2.ellipse(new_image, (int(w - r + 3 * t / 2 - 1), int(h - r + 3 * t / 2 - 1)), (r, r), 0, 0, 90, c,
	                        dt)

	# Draw four edges
	new_image = cv2.line(new_image, (int(r + t / 2), int(t / 2)), (int(w - r + 3 * t / 2 - 1), int(t / 2)), c, dt)
	new_image = cv2.line(new_image, (int(t / 2), int(r + t / 2)), (int(t / 2), int(h - r + 3 * t / 2)), c, dt)
	new_image = cv2.line(new_image, (int(r + t / 2), int(h + 3 * t / 2)),
	                     (int(w - r + 3 * t / 2 - 1), int(h + 3 * t / 2)), c, dt)
	new_image = cv2.line(new_image, (int(w + 3 * t / 2), int(r + t / 2)), (int(w + 3 * t / 2), int(h - r + 3 * t / 2)),
	                     c, dt)

	# Generate masks for proper blending
	if t != 0:
		mask = new_image[:, :, 3].copy()
	mask = cv2.floodFill(mask, None, (int(w / 2 + t), int(h / 2 + t)), 128)[1]
	mask[mask != 128] = 0
	mask[mask == 128] = 1
	mask = np.stack((mask, mask, mask), axis=2)

	# Blend images
	temp = np.zeros_like(new_image[:, :, :3])
	temp[t:(h + t), t:(w + t)] = image.copy()
	new_image[:, :, :3] = new_image[:, :, :3] * (1 - mask) + temp * mask

	# Set proper alpha channel in new image
	temp = new_image[:, :, 3].copy()
	new_image[:, :, 3] = cv2.floodFill(temp, None, (int(w / 2 + t), int(h / 2 + t)), 255)[1]

	return new_image


def round_and_save(file: str):
	img = cv2.imread(file)
	name = file
	has_ext = len(re.findall(r"\..+$", name)) > 0
	if not has_ext:
		name = file + ".png"
	if cv2.imwrite(name, round_corners(img, 23, 0, (0, 0, 0))):
		if not has_ext:
			os.rename(name, file)
		return True
	return False


if __name__ == "__main__":
	img = cv2.imread('image_cache/ab67616d00001e0274f062e52719ab05b992eecc')
	# cv2.imshow('img', img)

	new_img = round_corners(img, 20, 0, (0, 0, 0))
	cv2.imwrite('image_cache/round.png', new_img)
	# cv2.imshow('new_img', new_img)

	cv2.waitKey(0)
	cv2.destroyAllWindows()
