# importing setup from setup tools
from setuptools import setup

setup(
   name='cvpackage',
   packages=['cvpackage'],
   version='0.0.7',
   license='MIT',
   description='An helper library for openCv developer.',
   long_description='This an Computer Vision library uses mediapipe solutions at base level.An open cv developer can '
                    'use it, to fastly use all solutions provided by mediapipe by writing few lines of code.',
   author='Kartik Panchal',
   author_email='clickshare07@gmail.com',
   url='https://github.com/MrBucks07/CvPack',
   keywords=['MediaPipe', 'FaceMesh', 'FaceDetection', 'HandTracking', 'HandModule', 'FaceModule'],
   install_requires=[
      'opencv-python',
      'mediapipe'
   ],
   classifiers=[
      'License :: OSI Approved :: MIT License',
      'Intended Audience :: Developers',
      'Programming Language :: Python :: 3',
      'Operating System :: OS Independent'
    ],
)
