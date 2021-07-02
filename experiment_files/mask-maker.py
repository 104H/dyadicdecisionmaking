
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# defining the variables
sigma = 30
muu = 140
radius = 240
smoothness = 100  # smoothness of the blur

theta = np.linspace(0, 2 * np.pi, 1024)  # theta goes from 0 to 2pi

x = radius * np.cos(theta)
y = radius * np.sin(theta)

x, y = np.meshgrid(x, y)

# calculating the distance of all points to the center
distance = np.sqrt(x*x + y*y)

# calculating the Gaussian array
gauss = (1 / sigma * np.sqrt(2 * np.pi)) * np.exp(-0.5 * ( ( distance - muu ) / sigma)**2)

# plotting the mask
plt.gray()
fig, ax = plt.subplots(1)
ax.set_aspect(1)
ax.contourf(x, y, gauss, smoothness)
ax.axis('off')
#plt.show()

plt.savefig("mask.png", bbox_inches='tight', pad_inches=0, dpi=1200)

# import the mask and convert it to a numpy array
img = Image.open('mask.png').convert('LA')

maskarray = np.asarray(img)
maskarray = maskarray[:,:,0]

maskarray = np.interp(maskarray, (maskarray.min(), maskarray.max()), (-1, +1)) # normalize [-1,1]
maskarray[np.where(maskarray == 1)] = -1

np.save('maskarray', maskarray)