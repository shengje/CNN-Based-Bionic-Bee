# CNN-Based-Bionic-Bee

Project for CNN application

## Environment
* System OS : windows 10
* Python : Python 3.6.2
* Keras : Keras 2.0.8

## Introduction
We create this project to apply CNN(Convolution Neural Network), using keras backend tensorflow to construct our network.
Our network are using 5 layers of convolution + maxpooling and 1 layer of fully connected (dense layer).  
We try to using CNN to control Drone, making it self control without human.
Further more we want to make this drone can find flowers and recognize its species using CNN.

## Now Progress
Now we can make the drone fly automatically by about 10 meters long in the hallway.

Following link is a video example.

https://drive.google.com/a/g.ncu.edu.tw/file/d/1s4xx9KmXxhEMji93oRxBfrH0Nh-MzdZs/view?usp=sharing

We're now able to let the drone fly in the long hallway automaticly. And the precision is around 90% (less than 10% of the time need human intervention).

Next step we try to add the flower recognition system on the drone.
Our solution will be YOLO object detection with Tiny Darknet structure.
