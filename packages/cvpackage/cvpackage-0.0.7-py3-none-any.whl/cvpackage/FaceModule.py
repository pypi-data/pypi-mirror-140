# Author : Kartik Panchal
# All required dependency
import math

import cv2
import mediapipe as mp


# ***********************

# Creating Face Detector Class.
class MbFaceDetector:
    # Constructor
    def __init__(self, iMaxFaces=1, iMinDetectionCon=0.7):
        # important params
        self.maxNumFaces = iMaxFaces
        self.minDetectionConfidence = iMinDetectionCon

        # some useful variables
        self.mpDrawing = mp.solutions.drawing_utils
        self.mpDrawingStyles = mp.solutions.drawing_styles
        self.mpFace = mp.solutions.face_mesh
        # face mesh contour specifications
        self.drawSpec = self.mpDrawing.DrawingSpec(thickness=1, circle_radius=1)

        # configuring face solutions from media pipe
        self.faces = self.mpFace.FaceMesh(
            max_num_faces=iMaxFaces,
            min_detection_confidence=iMinDetectionCon
        )

    # Detect faces method
    def detectFaces(self, inputImage, draw=False):
        # first converting input image to rgb
        inputImage.flags.writeable = False
        imageRgb = cv2.cvtColor(inputImage, cv2.COLOR_BGR2RGB)

        # now detecting face
        result = self.faces.process(imageRgb)

        faces = []
        if result.multi_face_landmarks:
            # drawing face skeleton
            for self.faceLandmarks in result.multi_face_landmarks:
                if draw:
                    self.mpDrawing.draw_landmarks(
                        image=inputImage,
                        landmark_list=self.faceLandmarks,
                        landmark_drawing_spec=self.drawSpec,
                        connections=self.mpFace.FACEMESH_CONTOURS,
                        connection_drawing_spec=self.mpDrawingStyles
                            .get_default_face_mesh_contours_style()
                    )
                # face landmarks to return
                face = []
                for index, landmark in enumerate(self.faceLandmarks.landmark):
                    imgH, imgW, imgC = inputImage.shape
                    x, y = int(landmark.x * imgW), int(landmark.y * imgH)
                    face.append([x, y])
                # now appending to faces
                faces.append(face)
        return inputImage, faces

    # method to find distance  between two points
    def getDistance(self, point1, point2):
        self.passMethod()
        # points coordinates
        x0, y0 = point1
        x1, y1 = point2

        # using maths finding distance.
        dist = math.hypot(x1 - x0, y1 - y0)

        return dist

    def passMethod(self):
        pass
