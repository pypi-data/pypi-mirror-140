# Author : Kartik panchal
# required dependency
import cv2
import mediapipe as mp


# *******************

# Creating holistic pose detection class
class MbHolisticPoseDetection:
    # Constructor
    def __init__(self, iMinDetectionCon=0.5, iMinTrackingCon=0.5):
        # important params
        self.minDetectionCon = iMinDetectionCon
        self.minTrackingCon = iMinTrackingCon

        # some useful variables
        self.mpDrawing = mp.solutions.drawing_utils
        self.mpDrawingStyles = mp.solutions.drawing_styles
        self.mpHolistic = mp.solutions.holistic

        # face mesh contour specifications
        self.drawSpec = self.mpDrawingStyles.DrawingSpec(thickness=1, circle_radius=1)

        # configuring holistic module from media pipe
        self.holistic = self.mpHolistic.Holistic(
            min_detection_confidence=self.minDetectionCon,
            min_tracking_confidence=self.minTrackingCon
        )

    # Method to detect holistic
    def detectHolistic(self, inputImage, draw=False):
        # converting input image to rgb
        inputImage.flags.writeable = False
        imageRgb = cv2.cvtColor(inputImage, cv2.COLOR_BGR2RGB)

        # detecting holistic pose
        result = self.holistic.process(inputImage)

        if result.pose_landmarks:
            if draw:
                # drawing pose landmarks
                self.mpDrawing.draw_landmarks(
                    image=inputImage,
                    landmark_list=result.pose_landmarks,
                    connections=self.mpHolistic.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mpDrawingStyles.get_default_pose_landmarks_style(),
                )

                # drawing face landmarks
                self.mpDrawing.draw_landmarks(
                    image=inputImage,
                    landmark_list=result.face_landmarks,
                    landmark_drawing_spec=self.drawSpec,
                    connections=self.mpHolistic.FACEMESH_CONTOURS
                )

        return inputImage, result.pose_landmarks
