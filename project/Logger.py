import cv2
__author__ = 'emontenegro'

outputDirectory = "./output/"


def save_image(name, img):
    cv2.imwrite(outputDirectory+name, img)
    # print "Saved %s at %s" % (name, outputDirectory+name)

class Logger:
    pass
