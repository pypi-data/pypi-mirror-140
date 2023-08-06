# Author : Kartik panchal
# required dependency
import cv2
import mediapipe as mp


# *******************

# Creating pose detection class
class MbPoseDetection:
    # Constructor
    def __init__(self, iModelComplexity=1, iMinDetectionCon=0.5, iEnableSegmentation=True):
        # important params
        self.modelComplexity = iModelComplexity
        self.minDetectionCon = iMinDetectionCon
        self.enableSegmentation = iEnableSegmentation

        # some useful variables
        self.mpDrawing = mp.solutions.drawing_utils
        self.mpDrawingStyles = mp.solutions.drawing_styles
        self.mpPose = mp.solutions.pose

        # configuring pose solution from media pipe
        self.poses = self.mpPose.Pose(
            model_complexity=self.modelComplexity,
            enable_segmentation=self.enableSegmentation,
            min_detection_confidence=self.minDetectionCon
        )

    # Method to detect poses
    def detectPoses(self, inputImage, draw=False):
        # first converting input image to rgb
        inputImage.flags.writeable = False
        imageRgb = cv2.cvtColor(inputImage, cv2.COLOR_BGR2RGB)

        # detecting different poses
        result = self.poses.process(imageRgb)

        if result.pose_landmarks:
            # drawing pose connections
            if draw:
                self.mpDrawing.draw_landmarks(
                    image=inputImage,
                    landmark_list=result.pose_landmarks,
                    connections=self.mpPose.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mpDrawingStyles.get_default_pose_landmarks_style()
                )

        return inputImage, result.pose_landmarks
