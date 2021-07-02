import numpy as np
from scipy import ndimage as ndi
import cv2

X = 2048 # size of the mask, has to be to the power of two
center = int(X/2)
radius = 252 # 4.8 degress of visual angle; the value in pixels is for 80cm distance to screen
sigma = 94 # 1.8 degrees of visual angle; the value in pixels is for 80cm distance to screen


x = np.zeros((X, X))
cv2.circle(x, (center,center), radius=radius, color = 1, thickness=1)
x = ndi.filters.gaussian_filter(x, sigma=sigma)
x = np.interp(x, (x.min(), x.max()), (-1, 1))
x[np.where(x == 1)] = -1
np.save('gaussian_ann.npy', x)
