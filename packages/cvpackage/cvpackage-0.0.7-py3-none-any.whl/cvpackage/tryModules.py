# required dependency
import cv2
# Solutions you can try (uncomment the solution and try it)
# from FaceDetectionModule import MbFaceDetection
# from FaceMeshDetectionModule import MbFaceMeshDetector
from HandDetectionModule import MbHandDetector
# from PoseDetectionModule import MbPoseDetection
# from HolisticModule import MbHolisticPoseDetection
# *********************

# reading web cam using cv2
cam = cv2.VideoCapture(0)

# import and apply the model you want to try.
ht = MbHandDetector(iMinDetectionCon=0.7, iMaxHands=1)
# ....

while cam.isOpened():
    success, images = cam.read()

    # use method of different modules to detect anything.
    if success:
        images = ht.detectHands(inputImage=images, draw=True)
    # ....

    # output
    cv2.imshow("OP", images)
    cv2.waitKey(1)
