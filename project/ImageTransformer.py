import cv2
from ImageProcessor import ImageProcessor
import numpy as np
import math
from SatelliteImage import SatelliteImage

__author__ = 'emontenegro'


class ImageTransformer:
    # Attributes
    imageToTransform = None

    def __init__(self, imageobject):
        """

        :param imageobject:
        """
        self.imageToTransform = imageobject

    def transform_image(self):
        """

        :return:
        """
        # obtengo los contornos que serviran para la tansformacion
        self.imageToTransform.calculate_contours()
        # imgContours = self.imageToTransform.ImageContours
        filteredTopMostPoints, topLine, tPoint1, tPoint2 = self.__filter_top_points()
        filteredBotMostPoints, botLine, bPoint1, bPoint2 = self.__filter_bot_points()

        leftMostPoint = self.__filter_lft_points()
        rightMostPoint = self.__filter_rgt_points()
        # filtrar los puntos de top bot rgt lft de los contornos
        lPoint1, lPoint2 = self.__get_lft_line(filteredBotMostPoints[0], filteredTopMostPoints[0])
        rPoint1, rPoint2 = self.__get_rgt_line(filteredBotMostPoints[len(filteredBotMostPoints)-1], filteredTopMostPoints[len(filteredTopMostPoints)-1])
        inP1 = ImageTransformer.line_intersection(tPoint1, tPoint2, lPoint1, lPoint2)  # TOP LEFT
        inP2 = ImageTransformer.line_intersection(bPoint1, bPoint2, lPoint1, lPoint2)  # BOT LEFT
        inP3 = ImageTransformer.line_intersection(tPoint1, tPoint2, rPoint1, rPoint2)  # TOP RIGHT
        # inP4 = ImageTransformer.line_intersection(bPoint1, bPoint2, rPoint1, rPoint2)  # BOT RIGHT

        # CALCULANDO LA IMAGEN TRANSFORMADA
        self.imageToTransform.transformedSatelliteImage = ImageTransformer.__get_transformed_img(self.imageToTransform, list(inP1), list(inP2), list(inP3), outP1, outP2, outP3)
        self.imageToTransform.midPatternPointsTransformed[SatelliteImage.TOP_LEFT] = inP1                   # TOP LEFT
        self.imageToTransform.midPatternPointsTransformed[SatelliteImage.BOT_LEFT] = [inP1[0], inP2[1]]     # BOT LEFT
        self.imageToTransform.midPatternPointsTransformed[SatelliteImage.TOP_RIGHT] = [inP3[0], inP1[1]]    # TOP RIGHT
        self.imageToTransform.midPatternPointsTransformed[SatelliteImage.BOT_RIGHT] = [inP2[0], inP3[1]]    # BOT RIGHT

    def __filter_bot_points(self):
        """

        :return:
        """
        imagemiddle = self.imageToTransform.get_height()/2
        filteredbotmostpoints = []
        botmostpointmaxy = 0

        for botPoint in self.imageToTransform.botContourPoints:
            xbmp, ybmp = botPoint
            if ybmp > imagemiddle and (self.imageToTransform.get_height()-ybmp > ybmp-imagemiddle):
                filteredbotmostpoints.append(botPoint)
                botmostpointmaxy = max(botmostpointmaxy, ybmp)

        filteredbotmostpoints = [list(point) for point in filteredbotmostpoints
                                    if (abs(point[1]-botmostpointmaxy) < abs(imagemiddle-point[1]))
                                    and abs(point[1]-botmostpointmaxy) < ImageProcessor.error_pixels]
        filteredbotmostpoints = sorted(filteredbotmostpoints, key=lambda point: point[0])

        [vx, vy, x, y] = cv2.fitLine(np.float32(filteredbotmostpoints), cv2.cv.CV_DIST_L12, 0, 0.01, 0.01)
        # Now find two extreme points on the line to draw line
        lefty = int((-x*vy/vx) + y)
        righty = int(((self.imageToTransform.get_width()-x)*vy/vx)+y)

        #Finally draw the line
        # cv2.line(img,(img.shape[1]-1,righty),(0,lefty),255,1)

        # for i, p in zip(range(len(filteredBottomMostPoints)), filteredBottomMostPoints):
            # if i+1 < len(filteredBottomMostPoints):
                # cv2.line(img, tuple(p), tuple(filteredBottomMostPoints[i+1]), (255,0,0), 1)
            # cv2.circle(img, tuple(p), 1, 50)

        return filteredbotmostpoints, [vx, vy, x, y], (self.imageToTransform.get_width()-1, righty), (0, lefty)

    def __filter_top_points(self):
        """

        :return:
        """
        imagemiddle = self.imageToTransform.get_height()/2
        filteredtopmostpoints = []
        topmostpointminy = self.imageToTransform.get_height()

        for topPoint in self.imageToTransform.topContourPoints:
            xtmp, ytmp = topPoint
            if ytmp < imagemiddle and (abs(ytmp) > abs(ytmp-imagemiddle)):
                filteredtopmostpoints.append(topPoint)
                topmostpointminy = min(topmostpointminy, ytmp)

        filteredtopmostpoints = [list(point) for point in filteredtopmostpoints
                                 if (abs(point[1]-topmostpointminy) < abs(imagemiddle-point[1]))
                                 and abs(point[1]-topmostpointminy)<ImageProcessor.error_pixels]
        filteredtopmostpoints = sorted(filteredtopmostpoints, key=lambda point: point[0])

        [vx, vy, x, y] = cv2.fitLine(np.float32(filteredtopmostpoints), cv2.cv.CV_DIST_L12, 0, 0.01, 0.01)
        # Now find two extreme points on the line to draw line

        lefty = int((-x*vy/vx) + y)
        righty = int(((self.imageToTransform.get_height()-x)*vy/vx)+y)

        # for point in filteredTopMostPoints:
            # print "The point is %s" % (point,)
            # print "abs(point[1]-tmpMinY) = %s" % (abs(point[1]-tmpMinY),)
            # print "abs(imageMiddle-point[1]) = %s" % (abs(imageMiddle-point[1]),)
            # print "abs(point[1]-tmpMinY)<5 = %s" % (abs(point[1]-tmpMinY),)
            # if (abs(point[1]-tmpMinY)<abs(imageMiddle-point[1])) and abs(point[1]-tmpMinY)<5:
                # print True
            # else:
                # print False

        # for i, p in zip(range(len(filteredTopMostPoints)), filteredTopMostPoints):
            # if i+1 < len(filteredTopMostPoints):
                # cv2.line(img, tuple(p), tuple(filteredTopMostPoints[i+1]), (255,0,0), 1)
            # cv2.circle(img, tuple(p), i, 50)

        return filteredtopmostpoints, [vx, vy, x, y], (self.imageToTransform.get_width()-1, righty), (0, lefty)

    def __filter_lft_points(self, pointBot, pointTop):
        """

        :param pointBot:
        :param pointTop:
        :return:
        """
        filteredleftmostpoints = sorted(self.imageToTransform.lftContourPoints, key=lambda point: point[0])

        shortestdistancetop = math.sqrt(math.pow(pointTop[0]-filteredleftmostpoints[0][0], 2)+math.pow(pointTop[1]-filteredleftmostpoints[0][1], 2))
        shortestdistancebot = math.sqrt(math.pow(pointBot[0]-filteredleftmostpoints[0][0], 2)+math.pow(pointBot[1]-filteredleftmostpoints[0][1], 2))

        for pointEvaluated in filteredleftmostpoints:
            shortestdistancetoptmp = math.sqrt(math.pow(pointTop[0]-pointEvaluated[0], 2)+math.pow(pointTop[1]-pointEvaluated[1], 2))
            shortestdistancebottmp = math.sqrt(math.pow(pointBot[0]-pointEvaluated[0], 2)+math.pow(pointBot[1]-pointEvaluated[1], 2))

            if shortestdistancetoptmp < shortestdistancetop and shortestdistancebottmp < shortestdistancebot:
                shortestdistancetop = shortestdistancetoptmp
                shortestdistancebot = shortestdistancebottmp
                leftpointreturn = pointEvaluated
            else:
                break
        # cv2.circle(img, tuple(pointBot), 3, 150)
        # cv2.circle(img, tuple(pointTop), 3, 150)
        # cv2.circle(img, leftPointReturn, 3, 250)

        # for i, p in zip(range(len(filteredLeftMostPoints)), filteredLeftMostPoints):
            # cv2.circle(img, tuple(p), 1, 250)

        return leftpointreturn

    def __filter_rgt_points(self, pointBot, pointTop):
        """

        :param pointBot:
        :param pointTop:
        :return:
        """
        filteredrightmostpoints = sorted(self.imageToTransform.rgtContourPoints, key=lambda point: point[0], reverse=True)

        shortestdistancetop = math.sqrt(math.pow(pointTop[0]-filteredrightmostpoints[0][0], 2)+math.pow(pointTop[1]-filteredrightmostpoints[0][1], 2))
        shortestdistancebot = math.sqrt(math.pow(pointBot[0]-filteredrightmostpoints[0][0], 2)+math.pow(pointBot[1]-filteredrightmostpoints[0][1], 2))

        for pointEvaluated in filteredrightmostpoints:
            shortestdistancetoptmp = math.sqrt(math.pow(pointTop[0]-pointEvaluated[0], 2)+math.pow(pointTop[1]-pointEvaluated[1], 2))
            shortestdistancebottmp = math.sqrt(math.pow(pointBot[0]-pointEvaluated[0], 2)+math.pow(pointBot[1]-pointEvaluated[1], 2))

            if shortestdistancetoptmp < shortestdistancetop and shortestdistancebottmp < shortestdistancebot:
                shortestdistancetop = shortestdistancetoptmp
                shortestdistancebot = shortestdistancebottmp
                rightpointreturn = pointEvaluated
            else:
                break
        # cv2.circle(img, tuple(pointBot), 3, 150)
        # cv2.circle(img, tuple(pointTop), 3, 150)
        # cv2.circle(img, rightPointReturn, 3, 250)

        # for i, p in zip(range(len(filteredRightMostPoints)), filteredRightMostPoints):
            # cv2.circle(img, tuple(p), 1, 250)

        return rightpointreturn

    def __get_lft_line(self, leftMostPoint, vx, vy):
        # Obteniendo la linea izquierda
        # X = (Y-Y0)* -(1/M)+ X0 recta inversa
        topX = int(((0-leftMostPoint[1])*vy/-vx) + leftMostPoint[0])
        botX = int(((self.imageToTransform.get_height(self)-1-leftMostPoint[1])*vy/-vx) + leftMostPoint[0])
        lPoint1 = (botX, self.imageToTransform.get_height(self)-1)
        lPoint2 = (topX, 0)
        return lPoint1, lPoint2

    def __get_rgt_line(self, rightMostPoint, vx, vy):
        # Obteniendo la linea derecha
        # X = (Y-Y0)* -(1/M)+ X0 recta inversa
        topX = int(((0-rightMostPoint[1])*vy/-vx) + rightMostPoint[0])
        botX = int(((self.imageToTransform.get_height(self)-1-rightMostPoint[1])*vy/-vx) + rightMostPoint[0])
        rPoint1 = (botX, self.imageToTransform.get_height(self)-1)
        rPoint2 = (topX, 0)
        return rPoint1, rPoint2

    @staticmethod
    def line_intersection(point1, point2, point3, point4):
        xdiff = (point1[0] - point2[0], point3[0] - point4[0])
        ydiff = (point1[1] - point2[1], point3[1] - point4[1])

        def det(pA, pB):
            return pA[0] * pB[1] - pA[1] * pB[0]

        div = det(xdiff, ydiff)
        if div == 0:
            raise Exception('lines do not intersect')

        d = (det(point1, point2), det(point3, point4))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        return x, y

    def __get_transformed_img(self, inP1, inP2, inP3, outP1, outP2, outP3):
        pts1 = np.float32([inP1,  inP2,  inP3])
        pts2 = np.float32([outP1, outP2, outP3])
        M = cv2.getAffineTransform(pts1, pts2)
        dest = cv2.warpAffine(self.imageToTransform, M, (self.imageToTransform.get_width(), self.imageToTransform.get_height()))
        return dest