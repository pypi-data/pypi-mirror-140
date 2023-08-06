# Author : Kartik Panchal
# All required dependency
import math

import cv2
import mediapipe as mp


# ***********************

# Creating FaceDetection class.
class MbFaceDetection:
    # Constructor
    def __init__(self, iMinDetectionCon=0.5, iModelSelect=1):
        # important params
        self.modelSelect = iModelSelect
        self.minDetectionCon = iMinDetectionCon

        # some useful variables
        self.mpDrawing = mp.solutions.drawing_utils
        self.mpDrawingStyles = mp.solutions.drawing_styles
        self.mpFace = mp.solutions.face_detection

        # configuring face detection solution from media pipe
        self.faces = self.mpFace.FaceDetection(
            model_selection=self.modelSelect,
            min_detection_confidence=self.minDetectionCon
        )

    # Detect faces method
    def detectFaces(self, inputImage, draw=False):
        # first converting input image to rgb
        inputImage.flags.writeable = False
        imageRgb = cv2.cvtColor(inputImage, cv2.COLOR_BGR2RGB)

        # now detecting face
        result = self.faces.process(imageRgb)

        if result.detections:
            # drawing box on face
            for detection in result.detections:
                if draw:
                    self.mpDrawing.draw_detection(
                        image=inputImage,
                        detection=detection,
                    )
        return inputImage




