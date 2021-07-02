import numpy as np
from scipy import ndimage as ndi
import cv2

X = 1024 # size of the mask, has to be a power of two
center = int(X/2)
radius = 186 # 4.8 degress of visual angle; the value in pixels is for 60cm distance to screen
sigma = 70 # 1.8 degrees of visual angle; the value in pixels is for 60cm distance to screen


x = np.zeros((X, X))
cv2.circle(x, (center,center), radius=radius, color = 1, thickness=1)
x = ndi.filters.gaussian_filter(x, sigma=sigma)
x = np.interp(x, (x.min(), x.max()), (-1, 1))
x[np.where(x == 1)] = -1
np.save('gaussian_ann.npy', x)
