import pickle
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os, os.path # Get directory info



# Get the list of all files in the directory
DIR = './camera_cal/'
image_names = [name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))]


images = []
grays = []
rets = []
corners = []
nx = 9 # the number of inside corners in x
ny = 6 # the number of inside corners in y

count = 0
# Read in all images
for i in range (len(image_names)):
    filename = DIR + image_names[i]
    image = cv2.imread(DIR + image_names[i])
    images.append(image)
    grays.append(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
    ret, corn = cv2.findChessboardCorners(grays[i], (nx, ny), None)
    rets.append(ret)
    corners.append(corn)

    if rets[i] == True:
        # Draw and display the corners
        cv2.drawChessboardCorners(images[i], (nx, ny), corners[i], rets[i])
        count += 1
    print(filename)

print(count)




#ret, corners = cv2.findChessboardCorners(grays[0], (nx, ny), None)

#if rets[0] == True:
    # Draw and display the corners
    #cv2.drawChessboardCorners(images[0], (nx, ny), corners[0], rets[0])
    #plt.imshow(images[0])

#plt.show()

# MODIFY THIS FUNCTION TO GENERATE OUTPUT 
# THAT LOOKS LIKE THE IMAGE ABOVE
def corners_unwarp(img, nx, ny, mtx, dist):
    # Pass in your image into this function
    # Write code to do the following steps
    # 1) Undistort using mtx and dist
    undist = cv2.undistort(img, mtx, dist, None, mtx)
    # 2) Convert to grayscale
    gray = cv2.cvtColor(undist,cv2.COLOR_BGR2GRAY) # Convert to grayscale
    # 3) Find the chessboard corners
    ret, corners = cv2.findChessboardCorners(gray, (nx, ny), None)
    # 4) If corners found: 
    if ret == True:
        # If we found corners, draw them! (just for fun)
        cv2.drawChessboardCorners(undist, (nx, ny), corners, ret)
        # Choose offset from image corners to plot detected corners
        # This should be chosen to present the result at the proper aspect ratio
        # My choice of 100 pixels is not exact, but close enough for our purpose here
        offset = 100 # offset for dst points
        # Grab the image shape
        img_size = (gray.shape[1], gray.shape[0])

        # For source points I'm grabbing the outer four detected corners
        src = np.float32([corners[0], corners[nx-1], corners[-1], corners[-nx]])
        # For destination points, I'm arbitrarily choosing some points to be
        # a nice fit for displaying our warped result 
        # again, not exact, but close enough for our purposes
        dst = np.float32([[offset, offset], [img_size[0]-offset, offset], 
                                     [img_size[0]-offset, img_size[1]-offset], 
                                     [offset, img_size[1]-offset]])
        # Given src and dst points, calculate the perspective transform matrix
        M = cv2.getPerspectiveTransform(src, dst)
        # Warp the image using OpenCV warpPerspective()
        warped = cv2.warpPerspective(undist, M, img_size)
    #delete the next two lines
    #M = None
    #warped = np.copy(gray) 
    return warped, M

#top_down, perspective_M = corners_unwarp(img, nx, ny, mtx, dist)
#f, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 9))
#f.tight_layout()
#plt.imshow(img)
#ax1.set_title('Original Image', fontsize=50)
#ax2.imshow(top_down)
#ax2.set_title('Undistorted and Warped Image', fontsize=50)
#plt.subplots_adjust(left=0., right=1, top=0.9, bottom=0.)


# Set up subplot details
'''
f, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 9))
f.tight_layout()
ax1.imshow(img)
ax1.set_title('Original Image', fontsize=50)
ax2.imshow(img)
'''
# Set up subplot details
fig, axs = plt.subplots(5,4, figsize=(16, 4))
fig.subplots_adjust(hspace = .2, wspace=.001)
axs = axs.ravel()

for i in range(20):
    #index = random.randint(0, len(train['features']))
    image = images[i]

    axs[i].axis('off')
    axs[i].imshow(image, cmap='gray')
    axs[i].set_title(i)
plt.show()