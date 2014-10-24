__author__ = 'emontenegro'

class GraphGenerator:

    currentImage = None

    def __init__(self, currentImage):
        self.currentImage = currentImage

    def calculate_graphs(self):
        self.currentImage.calculate_contours()

        self.generate_graph(self.currentImage.midPatternPointsTransformed[self.TOP_LEFT],
                            self.currentImage.midPatternPointsTransformed[self.TOP_RIGHT],
                            self.currentImage.midPatternPointsTransformed[self.TOP_LEFT],
                            self.currentImage.midPatternPointsTransformed[self.BOT_LEFT],
                            "graph_mid_pattern.png")

        minYFirstPattern = topPointsProcessFirstPattern(1, cnt, transformedImage)
        maxYFirstPattern = botPointsProcessFirstPattern(outP1[1], cnt, transformedImage)

        self.generate_graph(self.currentImage.midPatternPointsTransformed[self.TOP_LEFT],
                            self.currentImage.midPatternPointsTransformed[self.TOP_RIGHT],
                            minYFirstPattern,
                            maxYFirstPattern,
                            "gaph_top_pattern.png")

        minYSecondPattern = topPointsProcessSecondPattern(outP2[1], cnt, transformedImage)
        maxYSecondPattern = botPointsProcessSecondPattern(outP2[1], cnt, transformedImage)
        self.generate_graph(self.currentImage.transformedSatelliteImage, outP1[0], outP3[0], minYSecondPattern, maxYSecondPattern, "gaph_bot_pattern.png")

        saveImage("transformed_image.png", transformedImage)  # save image
        # Finally draw the line in the original image
        cv2.line(img, bPoint1, bPoint2, 255, 1)
        cv2.line(img, tPoint1, tPoint2, 255, 1)
        cv2.line(img, lPoint1, lPoint2, 255, 1)
        cv2.line(img, rPoint1, rPoint2, 255, 1)

    def generate_graph(self, xStart, xEnd, yStart, yEnd, name):
        avgGreyScale = []
        for x in range(xStart, xEnd):
            avg = 0
            for y in range(yStart, yEnd-1):
                avg = avg + img[y][x]
            avg = avg/abs(yEnd-yStart)
            avgGreyScale.append(255-avg)
        # avgGreyScale = avgGreyScale[::-1]
        figurePlot = plt.figure()
        graphPlot = figurePlot.add_subplot(111)
        graphPlot.plot(avgGreyScale)
        figurePlot.savefig(outputDirectory+name)