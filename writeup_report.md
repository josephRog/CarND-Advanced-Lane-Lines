# **Advanced Lane Finding** 

## Writeup, Joseph Rogers

---

**Advanced Lane Finding Project**

The goals / steps of this project are the following:

* Compute the camera calibration matrix and distortion coefficients given a set of chessboard images.
* Apply a distortion correction to raw images.
* Use color transforms, gradients, etc., to create a thresholded binary image.
* Apply a perspective transform to rectify binary image ("birds-eye view").
* Detect lane pixels and fit to find the lane boundary.
* Determine the curvature of the lane and vehicle position with respect to center.
* Warp the detected lane boundaries back onto the original image.
* Output visual display of the lane boundaries and numerical estimation of lane curvature and vehicle position.

[//]: # (Image References)

[image1]: ./report_images/orig_dist_chess.png "Original Distorted Chessboard"
[image2]: ./report_images/undist_chess.png "Undistorted Chessboard"
[image3]: ./report_images/orig_road.png "Original Distorted Road"
[image4]: ./report_images/undist_road.png "Undistorted Road"
[image5]: ./report_images/orig_vs_binary.png "Binary Image Result"
[image6]: ./report_images/road_lines.png "Road Lines"
[image7]: ./report_images/warped_binary_hist.png "Warped binary and histogram"
[image8]: ./report_images/detected_lanes.png "Detected Lanes with fitted polynomial"
[image9]: ./report_images/warped_color.png "Warped color road image"
[image10]: ./report_images/colored_road.png "Undistored road with color overlay"
[image11]: ./report_images/text_road.png "Text overlayed on the road"
[video1]: ./project_video_processed.mp4 "Video"

## [Rubric](https://review.udacity.com/#!/rubrics/571/view) Points

### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---

### Writeup / README
 
Here is a link to my full [github repository.](https://github.com/josephRog/CarND-Advanced-Lane-Lines)

All code used to process the videos is contained within the `adv_lane_finding.ipynb` jupyter notebook file.

### Camera Calibration

#### Briefly state how you computed the camera matrix and distortion coefficients. Provide an example of a distortion corrected calibration image.

Firstly, a set of target points `objp` was defined to be used for calibration process. In order to compute the camera matrix I used a loop to read in all of the chessboard calibration images. As each image was opened, it was converted to grayscale and then `cv2.findChessboardCorners()` was called to see if any corners could be detected.

Each time a set of corners were detected they were automatically appended to the `imgpoints` array. Additionally a copy of `objp` was appended to the `objpoints` array to keep both the same size.

I then defined a function `cal_undistort(img, objpoint, imgpoints)`. This function was able to undistort any image passed to it. It did this using the `cv2.calibrateCamera()` function followed by `cv2.undistort()`. The following results were produced when undistorting a calibration chessboard image.

This can be tested and performed by running the first 4 cells of the jupyter notebook `adv_lane_finding.ipynb` file.

![alt text][image1] ![alt text][image2]

### Image Processing Pipeline

Now that the camera was calibrated, I was able to implement the full image processing pipeline in order to detect lanes on the road. The pipeline is broken into several discrete steps, each of which will be briefly explained.

* 1. Undistort the current image frame
* 2. Convert the image to binary using sobel, HLS, etc...
* 3. Warp the image to "bird's eye view"
* 4. Detect lines on the warped image
* 5. Update info in the `Lane` class
* 6. Add colors to the lane area
* 7. Warp back to the regular perspective
* 8. Add text to the image

#### 1. Undistort the current image frame

As each image frame of the video came in, I used the previously described `cal_undistort()` function to undistort the image frame.

![alt text][image4]

#### 2. Convert the image to binary using sobel, HLS, etc...

In order to convert the image to a suitable binary, I used a combination of techniques. Images were first converted to the HLS color space so that I could keep track of lane colors easier even if they were going in and out of shadowed areas. This is because the hue of the lane should remain constant even through these changes in its lightness.

I then performed a sobel detection in the x direction to try and isolate lines in the image that were relatively vertical.

These two operations were thresholded to certain values and then normalized to be on the same scale. They were then stacked on each other so that even when one technique was weaker in certain areas, it would still be complemented by the other.

This can be tested by running the 5th cell of the jupyter notebook `adv_lane_finding.ipynb`.

![alt text][image5]

#### 3. Warp the image to "bird's eye view"

I defined a new function `warpImage()` in order to perform the perspective transform of images to the bird's eye view. It used the `cv2.warpPerspective()` to do this. This function required source and desitnation points in order to perform the transformation.

This resulted in the following source and destination points:

| Source        | Destination   | 
|:-------------:|:-------------:| 
| 160, 720      | 230,720       | 
| 590, 450      | 230,0         |
| 690, 450      | 1050,0        |
| 1120, 720     | 1050,720      |

This image shows the source points overlayed on a full color image of the road.
![alt text][image6]

When testing this code I also printed a histogram of the resulting image in order to verfiy that the tranformed image would be usable for the lane finding process. The full code for this section can be tested by running cells 6 and 7 of jupyter notebook `adv_lane_finding.ipynb` file.

This image shows the final result of the transformed binary image, with a histogram of it along side. 

![alt text][image7]

#### 4. Detect lines on the warped image

To try and detect lane lines on the warped binary image, I began with the sliding window search code provided in section 33 of the Advanced Lane Finding lessons. The code searches through the warped binary image by using the peaks of its histogram as a starting point, and then trying to slide up the image and form a list a pixels that create a smooth curve. Once lane pixels had been found, a ploynomial was fit to the left and right sides using `np.polyfit()`.

I modified this code slighlty by changing some of the parameters for how many windows were used for performing the search and the margin of the search area. For the faster version of the code for subsequent frames, I reduced the margin of search from 100 down to 40. I did this to restrict how far the lanes were allowed to move from frame to frame. The idea was to reduce false positive readings of "lane looking" objects in the image that were far away from where previously detected lanes were. This helped immensly with consistency of lane prediction, as well as with how noisy they looked.

This code can be tested by running cell 8 of the notebook file. In order to see the figures however it will require uncommenting the plotting section near the bottom.

An example of the sliding window search and the fitted polynomials of each lane can be seen below:

![alt text][image8]

#### 5. Update info in the `Lane` class

The next step in the pipeline was to calculate and store all of the details for the car's position within the lane and the curvature of the lane itself. To store all of the lane details a new class `Lane` was created that would store all of the lane information for each frame, as well as some averages of the data from the previous several frames. The class definition can be viewed in section 2 of the notebook file.

For each frame, the actual curvature of the lanes was based on the code presented in section 35 of the Advanced Lane Finding lessons. This code was inserted into the same function performing the window search and polynomial generation. Each time the window search was run, it also calculated the lane curvature and then send that data to an object of the `Lane` class.

When this happened the window search would also send all of the pixel data for the left and right lane positions to the `Lane` object.

Once the window search was complete, a new function `updateCurves()` was called to calculate the new averages for radius of curvature and the left and right lane pixels for the last 5 frames. This was done to smooth the data and reduce noise during the color drawing step.

This code is present in section 10 of the notebook file.

#### 6. Add colors to the lane area

With all the lane info now stored and averaged, a new function `colorRoad()` was used to read pixel positions out of the `Lane` object and drawing colors for each of the lanes plus the road in-between them. This was done using `cv2.polylines()` to draw each of the lanes and `cv2.fillPoly()` to color the intervening road. The final result is a bird's eye color overlay of the lanes and road ready to be perspective transformed and then overlayed on the original undistorted image frame. This code can be tested by running section 11 in the notebook file.

An example of the warped color overlay image can be seen below:

![alt text][image9]

#### 7. Warp back to the regular perspective

With the warped color overlay now in hand, it could be reverse warped back to the perspective of the original undistorted image. To perform the reverse transformation the `cv2.getPerspectiveTransform()` was called again, but this time with the source and destination points swapped so as to get a reverse transform camera matrix as the result.

A function `transToRoad()` was then called to perform the actual reverse warp using `cv2.warpPerspective()` and overlaying of colors on the road using `cv2.addWeighted()`. This is presented in section 12 of the jupyter notebook.

The results of the `transToRoad()` function can be seen here:

![alt text][image10]

#### 8. Add text to the image

The final section of the image processing pipeline was to add some overlayed text displaying information about the lane curvature and verhicle position within the lane. A function `writeText()` was created to do this. This function pulled the `avg_curve` data and `lane_position` values from the `Lane`object previously stored there during the sliding window search.

Details were written to the image frame using the `cv2.putText()` function. This was the last step in the pipeline and output the final image that was then sent to the exported video. Code for the text writing can be found in section 13 of the notebook.

Example final image frame with overlayed text.
![alt text][image11]

---

### Pipeline (video)

#### 1. Provide a link to your final video output.  Your pipeline should perform reasonably well on the entire project video (wobbly lines are ok but no catastrophic failures that would cause the car to drive off the road!).

The final output video after it has been processed can be viewed by watching the `project_video_processed` file.

Here's a [link to my video result](./project_video_processed.mp4)

---

### Discussion

#### 1. Briefly discuss any problems / issues you faced in your implementation of this project.  Where will your pipeline likely fail?  What could you do to make it more robust?

Though the output video from the pipeline looks alright, there are definitely a few areas of improvment that could be addressed in the future.

There are certain types of roads where this pipeline will almost certainly have problems. Mountain roads with sharp turns will cause the lanes to turn outside of the warped image detection space, driving towards the top of hills will cause all sight of the road to be lost for a time until the crest has been reached, and night time driving may cause general difficulties for lane visibility.

Possible solutions to sharp turns might be some sort of memory where the lane prediction continues for a time in the same direction it was going in even if it fails to find any useful detections. Driving to the top of a hill might be able to be recognized visually since the lanes would progressivly become shorter and shorter and the addition of a gyroscope could be helpful. Night time images might be able to have their data augmented using an infra-red camera.

Finally the performance of the code is quite bad and could not be used in a real time scenario. I would love to implement a version of this pipeline that would run on the GPU. It's currently quite slow to run the video through the pipeline, clocking in at about 10 minutes on an intel 5930k CPU. I analyzed the time of each section of the pipeline and the most expensive part is the undistortion of the images, accounting for about 50% of the total.

It would also be possible to increase parallelism by filling all parts of the pipeline all the time. Once one frame has been undistorted there's no reason why the next frame in the video can't immediately start being undistorted as well on a 2nd thread while the first one starts going through its binary conversion. This idea could be extended to all stages of the pipeline with each having a dedicated CPU thread.
