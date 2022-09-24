# KoniPy

## Task

```r
Homework

Create a program written in Python that will consist of two components where each of them is running in a separate Docker image and they communicate with each other using a virtual network. 

1) Tracking component
- Sequentially load images and xml files with labels (from outside of the Docker image where the path is a parameter of the Docker file) – the xml files contain bounding boxes of detected objects. You can utilize the enclosed dataloader.py for this task.
- In the first picture, assing random IDs to all bounding boxes
- In the following ones, assign the ID of the closest bounding box from the previous picture (simple tracking)
- Immediately send each with the bounding box coordinates and IDs to the visualizing component, i.e. do not wait until all files are loaded
- Once all files are sent, notify the visualizing component

2) Visualising component
- Receive all the necessary data from the first tracking component
- Draw the bounding boxes to the corresponding images
- Use different colors for different IDs of a bounding box
- Show the ID number on top of the bounding box
- With the same color, draw also the last 10 locations of the central point of the bounding box (it will show how the person moves)
- Save the whole visualization as a video with a framerate of 5fps. The video should be saved into the original folder with the images

The program should include:
- Unit tests
- Readme file describing how to work with it

```
