import numpy as np
import cv2
import math
import matplotlib.pyplot as plt

################################ FILTRAR PUNTOS ################################

errorPixels = 6
outputDirectory = "./output/"

def leftMost(cnt):
	return tuple(cnt[cnt[:,:,0].argmin()][0])

def rightMost(cnt):
	return tuple(cnt[cnt[:,:,0].argmax()][0])

def topMost(cnt):
	return tuple(cnt[cnt[:,:,1].argmin()][0])

def bottomMost(cnt):
	return tuple(cnt[cnt[:,:,1].argmax()][0])
	
def getLines(img):
	cnt = getContours(img)
	# cv2.drawContours(img, cnt, -1, (0,255,0), 2) # To draw all the contours in an image (-1)
	# cv2.drawContours(img, contours, 3, (0,255,0), 3) # To draw an individual contour, say 4th contour
	# cnt = contours[4] # But most of the time, below method will be useful
	# cv2.drawContours(img, [cnt], 0, (0,255,0), 3)
	processPoints(cnt, img)
	
def processPoints(cnt, img):
	filteredBottomMostPoints, botLine, bPoint1, bPoint2 = bottomPointsProcess(cnt, img)
	filteredTopMostPoints, topLine, tPoint1, tPoint2 = topPointsProcess(cnt, img)
	leftMostPoint = leftPointsProcess(cnt, img, filteredBottomMostPoints[0], filteredTopMostPoints[0])
	rightMostPoint = rightPointsProcess(cnt, img, filteredBottomMostPoints[len(filteredBottomMostPoints)-1], filteredTopMostPoints[len(filteredTopMostPoints)-1])
	
	[vx,vy,x,y] = topLine
	
	# Obteniendo la linea izquierda
	# X = (Y-Y0)* -(1/M)+ X0 recta inversa
	topX = int(((			 -leftMostPoint[1])*vy/-vx) + leftMostPoint[0])
	botX = int(((img.shape[0]-1-leftMostPoint[1])*vy/-vx) + leftMostPoint[0])
	lPoint1 = (botX, img.shape[0]-1)
	lPoint2 = (topX,0)
	
	# Obteniendo la linea derecha
	# X = (Y-Y0)* -(1/M)+ X0 recta inversa
	topX = int(((			 -rightMostPoint[1])*vy/-vx) + rightMostPoint[0])
	botX = int(((img.shape[0]-1-rightMostPoint[1])*vy/-vx) + rightMostPoint[0])
	rPoint1 = (botX, img.shape[0]-1)
	rPoint2 = (topX,0)
	
	inP1 = line_intersection(tPoint1, tPoint2, lPoint1, lPoint2) #TOP LEFT
	inP2 = line_intersection(bPoint1, bPoint2, lPoint1, lPoint2) #BOT LEFT
	inP3 = line_intersection(tPoint1, tPoint2, rPoint1, rPoint2) #TOP RIGHT
	inP4 = line_intersection(bPoint1, bPoint2, rPoint1, rPoint2) #BOT RIGHT
	
	##CALCULANDO LA IMAGEN TRANSFORMADA
	outP1 = inP1			   # TOP LEFT
	outP2 = [inP1[0], inP2[1]] # BOT LEFT
	outP3 = [inP3[0], inP1[1]] # TOP RIGHT
	
	dest = get_transformed_img(img, list(inP1), list(inP2), list(inP3), outP1, outP2, outP3)
	
	cnt = getContours(dest)
	generate_graph(dest, outP1[0], outP3[0], outP1[1], outP2[1], "graph_mid_pattern.png")
	
	minYFirstPattern = topPointsProcessFirstPattern(1, cnt, dest)
	maxYFirstPattern = botPointsProcessFirstPattern(outP1[1] ,cnt, dest)
	generate_graph(dest, outP1[0], outP3[0], minYFirstPattern, maxYFirstPattern, "gaph_top_pattern.png")
	
	minYSecondPattern = topPointsProcessSecondPattern(outP2[1] ,cnt, dest)
	maxYSecondPattern = botPointsProcessSecondPattern(outP2[1] ,cnt, dest)
	generate_graph(dest, outP1[0], outP3[0], minYSecondPattern, maxYSecondPattern, "gaph_bot_pattern.png")
	
	saveImage("transformed_image.png", dest) # save image
	# Finally draw the line in the original image
	cv2.line(img, bPoint1, bPoint2, 255, 1)
	cv2.line(img, tPoint1, tPoint2, 255, 1)
	cv2.line(img, lPoint1, lPoint2, 255, 1)
	cv2.line(img, rPoint1, rPoint2, 255, 1)

##### CODIGO DUPLICADO												

def topPointsProcessFirstPattern(yCoordRef, cnt, img):
	tmpMinY = len(img)
	tmpMinX = 0
	for contour in cnt:
		xtmp, ytmp = topMostPoint = topMost(contour)
		if yCoordRef<ytmp and ytmp==min(tmpMinY, ytmp):
			tmpMinY = min(tmpMinY, ytmp)
			tmpMinX = xtmp
	cv2.circle(img, (tmpMinX, tmpMinY), 1, 250)
	return tmpMinY

def topPointsProcessSecondPattern(yCoordRef, cnt, img):
	tmpMinY = len(img)
	tmpMinX = 0
	for contour in cnt:
		xtmp, ytmp = botMostPoint = topMost(contour)
		if yCoordRef<ytmp and ytmp==min(tmpMinY, ytmp):
			tmpMinY = min(tmpMinY, ytmp)
			tmpMinX = xtmp
	# print tmpMinX, tmpMinY
	cv2.circle(img, (tmpMinX, tmpMinY), 1, 250)
	return tmpMinY

def botPointsProcessFirstPattern(yCoordRef, cnt, img):
	tmpMaxY = 0
	tmpMaxX = 0
	for contour in cnt:
		xtmp, ytmp = botMostPoint = bottomMost(contour)
		if yCoordRef>ytmp and ytmp==max(tmpMaxY, ytmp):
			tmpMaxY = max(tmpMaxY, ytmp)
			tmpMaxX = xtmp
	cv2.circle(img, (tmpMaxX, tmpMaxY), 1, 250)
	return tmpMaxY

def botPointsProcessSecondPattern(yCoordRef, cnt, img):
	tmpMinY = len(img)
	tmpMinX = 0
	for contour in cnt:
		xtmp, ytmp = botMostPoint = bottomMost(contour)
		if yCoordRef+errorPixels<ytmp and ytmp==min(tmpMinY, ytmp):
			tmpMinY = min(tmpMinY, ytmp)
			tmpMinX = xtmp
	cv2.circle(img, (tmpMinX, tmpMinY), 1, 250)
	return tmpMinY

def generate_graph(img, xStart, xEnd, yStart, yEnd, name):
	avgGreyScale = []
	for x in range(xStart,xEnd):
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

def get_transformed_img(img, inP1, inP2, inP3, outP1, outP2, outP3):
	pts1 = np.float32([inP1,  inP2,  inP3])
	pts2 = np.float32([outP1, outP2, outP3])
	M = cv2.getAffineTransform(pts1,pts2)
	rows, cols = img.shape
	dest =  cv2.warpAffine(img,M,(cols,rows))
	return dest
	
#### Interseccion de Segmentos
def line_intersection(point1, point2, point3, point4):
    xdiff = (point1[0] - point2[0], point3[0] - point4[0])
    ydiff = (point1[1] - point2[1], point3[1] - point4[1]) #Typo was here

    def det(pA, pB):
        return pA[0] * pB[1] - pA[1] * pB[0]

    div = det(xdiff, ydiff)
    if div == 0:
       raise Exception('lines do not intersect')

    d = (det(point1, point2), det(point3, point4))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y
	
	
#### Filtrado de puntos para la transformacion
def rightPointsProcess(cnt, img, pointBot, pointTop):
	filteredRightMostPoints = []
	rightPointReturn = 0
	for contour in cnt[1:]:
		rightMostPoint = rightMost(contour)
		filteredRightMostPoints.append(rightMostPoint)
		
	filteredRightMostPoints = sorted(filteredRightMostPoints, key=lambda point: point[0], reverse=True)
	
	shortestDistanceTop = math.sqrt(math.pow(pointTop[0]-filteredRightMostPoints[0][0], 2)+math.pow(pointTop[1]-filteredRightMostPoints[0][1], 2))
	shortestDistanceBot = math.sqrt(math.pow(pointBot[0]-filteredRightMostPoints[0][0], 2)+math.pow(pointBot[1]-filteredRightMostPoints[0][1], 2))
	
	for pointEvaluated in filteredRightMostPoints[1:]:
		shortestDistanceTopTmp = math.sqrt(math.pow(pointTop[0]-pointEvaluated[0], 2)+math.pow(pointTop[1]-pointEvaluated[1], 2))
		shortestDistanceBotTmp = math.sqrt(math.pow(pointBot[0]-pointEvaluated[0], 2)+math.pow(pointBot[1]-pointEvaluated[1], 2))
		
		if shortestDistanceTopTmp<shortestDistanceTop and shortestDistanceBotTmp<shortestDistanceBot:
			shortestDistanceTop = shortestDistanceTopTmp
			shortestDistanceBot = shortestDistanceBotTmp
			rightPointReturn = pointEvaluated
		else:
			break
	# cv2.circle(img, tuple(pointBot), 3, 150)
	# cv2.circle(img, tuple(pointTop), 3, 150)
	# cv2.circle(img, rightPointReturn, 3, 250)
	
	# for i, p in zip(range(len(filteredRightMostPoints)), filteredRightMostPoints):
		# cv2.circle(img, tuple(p), 1, 250)
	
	return rightPointReturn

def leftPointsProcess(cnt, img, pointBot, pointTop):
	filteredLeftMostPoints = []
	leftPointReturn = 0
	for contour in cnt[1:]:
		leftMostPoint = leftMost(contour)
		filteredLeftMostPoints.append(leftMostPoint)
		
	filteredLeftMostPoints = sorted(filteredLeftMostPoints, key=lambda point: point[0])
	
	shortestDistanceTop = math.sqrt(math.pow(pointTop[0]-filteredLeftMostPoints[0][0], 2)+math.pow(pointTop[1]-filteredLeftMostPoints[0][1], 2))
	shortestDistanceBot = math.sqrt(math.pow(pointBot[0]-filteredLeftMostPoints[0][0], 2)+math.pow(pointBot[1]-filteredLeftMostPoints[0][1], 2))
	
	for pointEvaluated in filteredLeftMostPoints[1:]:
		shortestDistanceTopTmp = math.sqrt(math.pow(pointTop[0]-pointEvaluated[0], 2)+math.pow(pointTop[1]-pointEvaluated[1], 2))
		shortestDistanceBotTmp = math.sqrt(math.pow(pointBot[0]-pointEvaluated[0], 2)+math.pow(pointBot[1]-pointEvaluated[1], 2))
		
		if shortestDistanceTopTmp<shortestDistanceTop and shortestDistanceBotTmp<shortestDistanceBot:
			shortestDistanceTop = shortestDistanceTopTmp
			shortestDistanceBot = shortestDistanceBotTmp
			leftPointReturn = pointEvaluated
		else:
			break
	# cv2.circle(img, tuple(pointBot), 3, 150)
	# cv2.circle(img, tuple(pointTop), 3, 150)
	# cv2.circle(img, leftPointReturn, 3, 250)
	
	# for i, p in zip(range(len(filteredLeftMostPoints)), filteredLeftMostPoints):
		# cv2.circle(img, tuple(p), 1, 250)
	
	return leftPointReturn
		
def topPointsProcess(cnt, img):
	imageMiddle = len(img)/2
	filteredTopMostPoints = []
	tmpMinY = len(img)

	for contour in cnt[1:]:
		xtmp, ytmp = topMostPoint = topMost(contour)
		if ytmp<imageMiddle and (abs(ytmp) > abs(ytmp-imageMiddle)) :
			filteredTopMostPoints.append(topMostPoint)
			tmpMinY = min(tmpMinY, ytmp)

	filteredTopMostPoints = sorted(filteredTopMostPoints, key=lambda point: point[0])
	filteredTopMostPoints = [list(point) for point in filteredTopMostPoints if (abs(point[1]-tmpMinY)<abs(imageMiddle-point[1])) and abs(point[1]-tmpMinY)<errorPixels]
	
	[vx,vy,x,y] = cv2.fitLine(np.float32(filteredTopMostPoints),cv2.cv.CV_DIST_L12,0,0.01,0.01)
	# Now find two extreme points on the line to draw line

	lefty = int((-x*vy/vx) + y)
	righty = int(((img.shape[1]-x)*vy/vx)+y)
	
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
		
	return filteredTopMostPoints, [vx,vy,x,y], (img.shape[1]-1,righty), (0,lefty)

def bottomPointsProcess(cnt, img):
	imageMiddle = len(img)/2
	filteredBottomMostPoints = []
	bmpMaxY = 0
	
	for contour in cnt[1:]:
		xbmp, ybmp = bottomMostPoint = bottomMost(contour)
		if ybmp>imageMiddle and (len(img)-ybmp > ybmp-imageMiddle) :
			filteredBottomMostPoints.append(bottomMostPoint)
			bmpMaxY = max(bmpMaxY, ybmp)
			
	filteredBottomMostPoints = [list(point) for point in filteredBottomMostPoints if (abs(point[1]-bmpMaxY)<abs(imageMiddle-point[1])) and abs(point[1]-bmpMaxY)<errorPixels]
	filteredBottomMostPoints = sorted(filteredBottomMostPoints, key=lambda point: point[0])

	[vx,vy,x,y] = cv2.fitLine(np.float32(filteredBottomMostPoints),cv2.cv.CV_DIST_L12,0,0.01,0.01)
	# Now find two extreme points on the line to draw line
	lefty = int((-x*vy/vx) + y)
	righty = int(((img.shape[1]-x)*vy/vx)+y)

	#Finally draw the line
	# cv2.line(img,(img.shape[1]-1,righty),(0,lefty),255,1)
	
	# for i, p in zip(range(len(filteredBottomMostPoints)), filteredBottomMostPoints):
		# if i+1 < len(filteredBottomMostPoints):
			# cv2.line(img, tuple(p), tuple(filteredBottomMostPoints[i+1]), (255,0,0), 1)
		# cv2.circle(img, tuple(p), 1, 50)
		
	return filteredBottomMostPoints, [vx,vy,x,y], (img.shape[1]-1,righty), (0,lefty)
	
#########################


def getContours(img):
	# imgGray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
	# ret, thresh = cv2.threshold(imgGray, 127, 255, cv2.THRESH_BINARY)
	ret, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
	saveImage('black_and_white_image.png', thresh)
	contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
	return contours

def saveImage(name, img):
	cv2.imwrite(outputDirectory+name, img)
	# print "Saved %s at %s" % (name, outputDirectory+name)
	
################################     MAIN     ################################

	
img = cv2.imread("test_case.png", cv2.CV_LOAD_IMAGE_GRAYSCALE) # open image in grayscale format

# img = cv2.imread('samples/Imagen_E5356.tif',-1)

getLines(img)

saveImage("output_after_process_limits.png", img) # save image