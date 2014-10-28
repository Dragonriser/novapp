import matplotlib.pyplot as plt
import Logger
__author__ = 'emontenegro'


class GraphGenerator:

    currentImage = None
    error_pixels = 0

    def __init__(self, currentImage, error_pixels):
        self.currentImage = currentImage
        self.error_pixels = error_pixels

    def calculate_graphs(self):
        self.currentImage.calculate_contours()

        self.generate_graph(self.currentImage.midPatternPointsTransformed[self.currentImage.TOP_LEFT][0],
                            self.currentImage.midPatternPointsTransformed[self.currentImage.TOP_RIGHT][0],
                            self.currentImage.midPatternPointsTransformed[self.currentImage.TOP_LEFT][1],
                            self.currentImage.midPatternPointsTransformed[self.currentImage.BOT_LEFT][1],
                            "graph_mid_pattern.png")

        minYFirstPattern = self.topPointsProcessFirstPattern(1)
        maxYFirstPattern = self.botPointsProcessFirstPattern(self.currentImage.midPatternPointsTransformed[self.currentImage.TOP_LEFT][1])

        self.generate_graph(self.currentImage.midPatternPointsTransformed[self.currentImage.TOP_LEFT][0],
                            self.currentImage.midPatternPointsTransformed[self.currentImage.TOP_RIGHT][0],
                            minYFirstPattern,
                            maxYFirstPattern,
                            "gaph_top_pattern.png")

        minYSecondPattern = self.topPointsProcessSecondPattern(self.currentImage.midPatternPointsTransformed[self.currentImage.BOT_LEFT][1])
        maxYSecondPattern = self.botPointsProcessSecondPattern(self.currentImage.midPatternPointsTransformed[self.currentImage.BOT_LEFT][1])
        self.generate_graph(self.currentImage.midPatternPointsTransformed[self.currentImage.TOP_LEFT][0],
                            self.currentImage.midPatternPointsTransformed[self.currentImage.TOP_RIGHT][0],
                            minYSecondPattern,
                            maxYSecondPattern,
                            "gaph_bot_pattern.png")

        # Finally draw the line in the original image
        # cv2.line(img, bPoint1, bPoint2, 255, 1)
        # cv2.line(img, tPoint1, tPoint2, 255, 1)
        # cv2.line(img, lPoint1, lPoint2, 255, 1)
        # cv2.line(img, rPoint1, rPoint2, 255, 1)

    def generate_graph(self, xStart, xEnd, yStart, yEnd, name):
        avgGreyScale = []
        for x in range(xStart, xEnd):
            avg = 0
            for y in range(yStart, yEnd-1):
                avg = avg + self.currentImage.get_transformed_pixel(x, y)
            avg = avg/abs(yEnd-yStart)
            avgGreyScale.append(255-avg)
        # avgGreyScale = avgGreyScale[::-1]
        figurePlot = plt.figure()
        graphPlot = figurePlot.add_subplot(111)
        graphPlot.plot(avgGreyScale)
        figurePlot.savefig(Logger.outputDirectory+name)

    def topPointsProcessFirstPattern(self, yCoordRef):
        tmpMinY = self.currentImage.get_height()
        # tmpMinX = 0
        for toppoint in self.currentImage.topContourPointsTransformed:
            xtmp, ytmp = toppoint
            if yCoordRef < min(tmpMinY, ytmp):  # if yCoordRef < ytmp and ytmp == min(tmpMinY, ytmp):
                tmpMinY = min(tmpMinY, ytmp)
                # tmpMinX = xtmp
        # cv2.circle(img, (tmpMinX, tmpMinY), 1, 250)
        return tmpMinY

    def topPointsProcessSecondPattern(self, yCoordRef):
        tmpMinY = self.currentImage.get_height()
        # tmpMinX = 0
        for botpoint in self.currentImage.topContourPointsTransformed:
            xtmp, ytmp = botpoint
            if yCoordRef < min(tmpMinY, ytmp):  # if yCoordRef<ytmp and ytmp==min(tmpMinY, ytmp):
                tmpMinY = min(tmpMinY, ytmp)
                # tmpMinX = xtmp
        # print tmpMinX, tmpMinY
        # cv2.circle(img, (tmpMinX, tmpMinY), 1, 250)
        return tmpMinY

    def botPointsProcessFirstPattern(self, yCoordRef):
        tmpMaxY = 0
        # tmpMaxX = 0
        for botpoint in self.currentImage.botContourPointsTransformed:
            xtmp, ytmp = botpoint
            if yCoordRef > max(tmpMaxY, ytmp):  # if yCoordRef>ytmp and ytmp==max(tmpMaxY, ytmp):
                tmpMaxY = max(tmpMaxY, ytmp)
                # tmpMaxX = xtmp
        # cv2.circle(img, (tmpMaxX, tmpMaxY), 1, 250)
        return tmpMaxY

    def botPointsProcessSecondPattern(self, yCoordRef):
        tmpMinY = self.currentImage.get_height()
        # tmpMinX = 0
        for botpoint in self.currentImage.botContourPointsTransformed:
            xtmp, ytmp = botpoint
            if yCoordRef + self.error_pixels < min(tmpMinY, ytmp):  # yCoordRef+ImageProcessor.errorPixels < min(tmpMinY, ytmp):
                tmpMinY = min(tmpMinY, ytmp)
                # tmpMinX = xtmp
        # cv2.circle(img, (tmpMinX, tmpMinY), 1, 250)
        return tmpMinY