# Define a function to pass stored images to
# reading rover position and yaw angle from csv file
# This function will be used by moviepy to create an output video
def process_image(img):
    # Example of how to use the Databucket() object defined above
    # to print the current x, y and yaw values 
    # print(data.xpos[data.count], data.ypos[data.count], data.yaw[data.count])

    # TODO: 
    # 1) Define source and destination points for perspective transform
    dst_size = 5 
    bottom_offset = 6
    source = np.float32([[14, 140], [301 ,140],[200, 96], [118, 96]])
    destination = np.float32([[img.shape[1]/2 - dst_size, img.shape[0] - bottom_offset],
                      [img.shape[1]/2 + dst_size, img.shape[0] - bottom_offset],
                      [img.shape[1]/2 + dst_size, img.shape[0] - 2*dst_size - bottom_offset], 
                      [img.shape[1]/2 - dst_size, img.shape[0] - 2*dst_size - bottom_offset],
                      ])
    
    # 2) Apply perspective transform
    warped = perspect_transform(grid_img, source, destination)
    
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    threshed_terrain = color_thresh(warped)
    threshed_obstacle = obstacle_thresh(warped)
    threshed_rocks = rock_thresh(warped)
    
    
    # 4) Convert thresholded image pixel values to rover-centric coords
    xpix, ypix = rover_coords(threshed_terrain)
    xpix_obstacle, ypix_obstacle = rover_coords(threshed_terrain)
    xpix_rock, ypix_rock = rover_coords(threshed_terrain)
    
    # 5) Convert rover-centric pixel values to world coords
    xpix, ypix = pix_to_world(xpix, ypix, data.xpos[data.count-1], data.ypos[data.count-1], data.yaw[data.count-1], data.worldmap.shape[0], 10)
    xpix_obstacle_world, ypix_obstacle_world = pix_to_world(xpix_obstacle, ypix_obstacle, data.xpos[data.count-1], data.ypos[data.count-1], data.yaw[data.count-1], data.worldmap.shape[0], 10)
    xpix_rocks_world, ypix_rocks_world = pix_to_world(xpix_rock, ypix_rock, data.xpos[data.count-1], data.ypos[data.count-1], data.yaw[data.count-1], data.worldmap.shape[0], 10)
    
    # 6) Update worldmap (to be displayed on right side of screen)
        # Example: data.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        #          data.worldmap[rock_y_world, rock_x_world, 1] += 1
        #          data.worldmap[navigable_y_world, navigable_x_world, 2] += 1
    
    data.worldmap[ypix_obstacle_world, xpix_obstacle_world, 0] = 255
    data.worldmap[ypix_rocks_world, xpix_rocks_world, 1] = 142
    data.worldmap[ypix, xpix, 2] = 142
    
    
    # 7) Make a mosaic image, below is some example code
        # First create a blank image (can be whatever shape you like)
    output_image = np.zeros((img.shape[0] + data.worldmap.shape[0], img.shape[1]*2, 3))
    
        # Next you can populate regions of the image with various output
        # Here I'm putting the original image in the upper left hand corner
    output_image[0:img.shape[0], 0:img.shape[1]] = img

        # Let's create more images to add to the mosaic, first a warped image
    warped = perspect_transform(img, source, destination)
    
        # Add the warped image in the upper right hand corner
    output_image[0:img.shape[0], img.shape[1]:] = warped

        # Overlay worldmap with ground truth map
    map_add = cv2.addWeighted(data.worldmap, 1, data.ground_truth, 0.5, 0)
    
        # Flip map overlay so y-axis points upward and add to output_image 
    output_image[img.shape[0]:, 0:data.worldmap.shape[1]] = np.flipud(map_add)


        # Then putting some text over the image
    cv2.putText(output_image,"Populate this image with your analyses to make a video!", (20, 20), 
                cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255), 1)
    data.count += 1 # Keep track of the index in the Databucket()
    
    return output_image
