import cv2
import numpy as np
import Queue

def MyConvolve(image, ff):
	result = np.zeros(image.shape)
	width = image.shape[0]
	height = image.shape[1]

	# Flip the filter
	ff = np.transpose(np.transpose(ff[::-1])[::-1])

	kernelSize = ff.shape[0]
	margin = kernelSize/2

	# Create a bigger matrix to pad with zeroes
	biggerResult = np.zeros([width+margin*2,height+margin*2])
	biggerResult[1:width+margin,1:height+margin] = image

	# Convolve
	for i in range(1,width+margin):
		for j in range(1,height+margin):
			multiplied = np.multiply(biggerResult[i-margin:i+margin+1,j-margin:j+margin+1],ff)
			summed = np.sum(multiplied)
			result[i-margin,j-margin] = summed

	return result

def nms(image):
	result = np.zeros(image.shape)
	edges = sobel(image)

	width = image.shape[0]
	height = image.shape[1]

	for i in range(width):
		for j in range(height):
			this = edges[i,j]

			# Save the neigbour values, make sure they are within the matrix (hence the mins and maxs)
			top = edges[max(i-1,0),j]
			bottom = edges[min(i+1,width-1),j]
			left = edges[i,max(j-1,0)]
			right = edges[i,min(j+1,height-1)]

			# Retain the edge if it's maximum in either axis
			if (max(top,bottom,this)==this) or (max(left,right,this)==this):
				result[i,j] = this

	return result

def sobel(image):
	result = np.zeros(image.shape)
	horizontal = np.zeros(image.shape)
	vertical = np.zeros(image.shape)

	horizontalFilter = np.matrix([[-1,0,1],[-2,0,2],[-1,0, 1]])
	verticalFilter = np.matrix([[1,2,1],[0,0,0],[-1,-2,-1]])

	# Find the horizontal and vertical edges first
	horizontal = MyConvolve(image, horizontalFilter)
	vertical = MyConvolve(image, verticalFilter)

	# Combine the two to get all edges
	result = np.sqrt(horizontal*horizontal+vertical*vertical)/4

	return result

def sobel_hor(image):
	result = np.zeros(image.shape)
	horizontal = np.zeros(image.shape)

	horizontalFilter = np.matrix([[1,2,1],[0,0,0],[-1,-2,-1]])

	# Find the horizontal edges first
	horizontal = MyConvolve(image, horizontalFilter)

	# Combine the two to get all edges
	result = horizontal/4

	return result

def sobel_ver(image):
	result = np.zeros(image.shape)
	vertical = np.zeros(image.shape)

	verticalFilter = np.matrix([[-1,0,1],[-2,0,2],[-1,0, 1]])

	# Find the vertical edges first
	vertical = MyConvolve(image, verticalFilter)

	# Combine the two to get all edges
	result = vertical/4

	return result

def gauss_kernels(size,sigma=1.0):
	## returns a 2d gaussian kernel
	if size<3:
		size = 3
	m = size/2
	x, y = np.mgrid[-m:m+1, -m:m+1]
	kernel = np.exp(-(x*x + y*y)/(2*sigma*sigma))
	kernel_sum = kernel.sum()
	if not sum==0:
		kernel = kernel/kernel_sum
	return kernel

def corner_detector(image, imageRGB):

	gx = sobel_hor(image)
	gy = sobel_ver(image)

	Ixx = gx*gx
	Ixy = gx*gy
	Iyy = gy*gy

	kernel = gauss_kernels(3,1)

	Wxx = MyConvolve(Ixx, kernel)
	Wxy = MyConvolve(Ixy, kernel)
	Wyy = MyConvolve(Iyy, kernel)

	k = 0.06
	threshold = 0.1
	stepsize = 10

	responses = np.zeros(Wxx.shape)

	for i in range(0,Wxx.shape[0],stepsize):
		for j in range(0,Wxx.shape[1],stepsize):
			W = np.zeros([2,2])
			W[0,0] = Wxx[i,j]
			W[0,1] = Wxy[i,j]
			W[1,0] = Wxy[i,j]
			W[1,1] = Wyy[i,j]

			detW = W[0,0]*W[1,1]-W[0,1]*W[1,0]
			traceW = W[0,0]+W[1,1]

			response = detW-k*traceW*traceW

			responses[i,j] = response

	maxVal = np.max(responses)

	for i in range(4,Wxx.shape[0]-4):
		for j in range(4,Wxx.shape[1]-4):
			if responses[i,j] >= maxVal*threshold:
				imageRGB[i-4:i+4,j-4,0] = 0
				imageRGB[i-4:i+4,j-4,1] = 0
				imageRGB[i-4:i+4,j-4,2] = 255

				imageRGB[i-4:i+4,j+4,0] = 0
				imageRGB[i-4:i+4,j+4,1] = 0
				imageRGB[i-4:i+4,j+4,2] = 255

				imageRGB[i-4,j-4:j+4,0] = 0
				imageRGB[i-4,j-4:j+4,1] = 0
				imageRGB[i-4,j-4:j+4,2] = 255

				imageRGB[i+4,j-4:j+5,0] = 0
				imageRGB[i+4,j-4:j+5,1] = 0
				imageRGB[i+4,j-4:j+5,2] = 255



	return imageRGB

def rgbToHue(colour):
	hue = 0

	b = colour[0]/255.0
	g = colour[1]/255.0
	r = colour[2]/255.0
	Cmax = max(b,g,r)
	Cmin = min(b,g,r)
	delta = Cmax-Cmin

	if delta == 0:
		hue = 0
	elif Cmax == r:
		hue = 60*(((g-b)/delta)%6)
	elif Cmax == g:
		hue = 60*(((b-r)/delta)+2)
	elif Cmax == b:
		hue = 60*(((r-g)/delta)+4)

	return hue

def rgbToSat(colour):
	sat = 0

	b = colour[0]/255.0
	g = colour[1]/255.0
	r = colour[2]/255.0
	Cmax = max(b,g,r)
	Cmin = min(b,g,r)
	delta = Cmax-Cmin

	if Cmax == 0:
		s = 0
	else:
		s = delta/Cmax

	return sat			

def rgbToBri(colour):
	bri = 0

	b = colour[0]/255.0
	g = colour[1]/255.0
	r = colour[2]/255.0
	Cmax = max(b,g,r)
	Cmin = min(b,g,r)
	delta = Cmax-Cmin

	bri = Cmax

	return bri

def patchColour(image,indicatedLocation):
	size = 2
	# Cropping out a window around the indicated component to find its colour	
	sample = image[indicatedLocation[0]-size:indicatedLocation[0]+size,indicatedLocation[1]-size:indicatedLocation[1]+size]
	greenAvg = np.mean(sample[:,:,0])
	blueAvg = np.mean(sample[:,:,1])
	redAvg = np.mean(sample[:,:,2])

	return [greenAvg,blueAvg,redAvg]

def hueDistance(colour1,colour2):
	colour1Hue = rgbToHue(colour1)
	colour2Hue = rgbToHue(colour2)

	hueDist = min(abs(colour1Hue-colour2Hue), 360-abs(colour1Hue-colour2Hue));

	return hueDist

def rgbDistance(colour1,colour2):
	rgbDist = np.linalg.norm([colour1[0]-colour2[0], colour1[1]-colour2[1], colour1[2]-colour2[2]])

	return rgbDist

# Convert rgb to Lab using RGB -> XYZ -> Lab
def rgb2lab(rgb):

	#print rgb
	## Convert RGB to XYZ
	num = 0
	RGB = [0, 0, 0]

	for value in rgb :
	   value = float(value) / 255

	   if value > 0.04045 :
	       value = np.power(((value+0.055)/1.055), 2.4)
	   else :
	       value = value / 12.92

	   RGB[num] = value * 100
	   num = num + 1

	XYZ = [0, 0, 0,]

	X = RGB[0] * 0.4124 + RGB[1] * 0.3576 + RGB[2] * 0.1805
	Y = RGB[0] * 0.2126 + RGB[1] * 0.7152 + RGB[2] * 0.0722
	Z = RGB[0] * 0.0193 + RGB[1] * 0.1192 + RGB[2] * 0.9505

	XYZ[0] = round(X, 4)
	XYZ[1] = round(Y, 4)
	XYZ[2] = round(Z, 4)

	#print XYZ
	## Convert XYZ to Lab

	XYZ[0] = float(XYZ[0]) / 95.047		# ref_X =  95.047   Observer= 2 deg, Illuminant= D65
	XYZ[1] = float(XYZ[1]) / 100.0		# ref_Y = 100.000
	XYZ[2] = float(XYZ[2]) / 108.883	# ref_Z = 108.883

	num = 0
	for value in XYZ :

	   if value > 0.008856 :
	       value = np.power(value, float(1)/3)
	   else :
	       value = (7.787*value) + (16/116)

	   XYZ[num] = value
	   num = num + 1

	Lab = [0, 0, 0]

	L = (116 * XYZ[1]) - 16
	a = 500 * (XYZ[0] - XYZ[1])
	b = 200 * (XYZ[1] - XYZ[2])

	Lab [ 0 ] = round( L, 4 )
	Lab [ 1 ] = round( a, 4 )
	Lab [ 2 ] = round( b, 4 )

	#print Lab

	return Lab


# Calculate the difference between two Lab colors
def deltaE(lab1, lab2):

	L1, a1, b1 = lab1[0], lab1[1], lab1[2]
	L2, a2, b2 = lab2[0], lab2[1], lab2[2]

	diff = np.sqrt(np.power(L1-L2, 2) + np.power(a1-a2, 2) + np.power(b1-b2, 2))

	return diff

def labDistance(colour1,colour2):
	lab1 = rgb2lab(colour1)
	lab2 = rgb2lab(colour2)

	labDist = deltaE(lab1, lab2)

	return labDist

def findColourDistance(colour1,colour2):
	colour1Hue = rgbToHue(colour1)
	colour2Hue = rgbToHue(colour2)

	hueDist = hueDistance(colour1, colour2)
	rgbDist = rgbDistance(colour1, colour2)
	labDist = labDistance(colour1, colour2)

	return labDist

# THIS NEEDS CHANGING
def findNewCentre(image, indicatedLocation, previousColour):
	sampleColour = patchColour(image,indicatedLocation)
	colourDistance = findColourDistance(sampleColour,previousColour)
	rayRange = 10

	print("Colour distance bad")
	for i in range(1,rayRange):

		nPatch = [indicatedLocation[0]-2*i,indicatedLocation[1]]
		nePatch = [indicatedLocation[0]-2*i,indicatedLocation[1]+2*i]
		ePatch = [indicatedLocation[0],indicatedLocation[1]+2*i]
		sePatch = [indicatedLocation[0]+2*i,indicatedLocation[1]+2*i]
		sPatch = [indicatedLocation[0]+2*i,indicatedLocation[1]]
		swPatch = [indicatedLocation[0]+2*i,indicatedLocation[1]-2*i]
		wPatch = [indicatedLocation[0],indicatedLocation[1]-2*i]
		nwPatch = [indicatedLocation[0]-2*i,indicatedLocation[1]-2*i]

		nPatchColour = patchColour(image, nPatch)
		nePatchColour = patchColour(image, nePatch)
		ePatchColour = patchColour(image, ePatch)
		sePatchColour = patchColour(image, sePatch)
		sPatchColour = patchColour(image, sPatch)
		swPatchColour = patchColour(image, swPatch)
		wPatchColour = patchColour(image, wPatch)
		nwPatchColour = patchColour(image, nwPatch)

		nColourDistance = findColourDistance(nPatchColour,previousColour)
		neColourDistance = findColourDistance(nePatchColour,previousColour)
		eColourDistance = findColourDistance(ePatchColour,previousColour)
		seColourDistance = findColourDistance(sePatchColour,previousColour)
		sColourDistance = findColourDistance(sPatchColour,previousColour)
		swColourDistance = findColourDistance(swPatchColour,previousColour)
		wColourDistance = findColourDistance(wPatchColour,previousColour)
		nwColourDistance = findColourDistance(nwPatchColour,previousColour)

		if nColourDistance < colourDistance:
			colourDistance = nColourDistance
			indicatedLocation = nPatch
		if neColourDistance < colourDistance:
			colourDistance = neColourDistance
			indicatedLocation = nePatch
		if eColourDistance < colourDistance:
			colourDistance = eColourDistance
			indicatedLocation = ePatch
		if seColourDistance < colourDistance:
			colourDistance = seColourDistance
			indicatedLocation = sePatch
		if sColourDistance < colourDistance:
			colourDistance = sColourDistance
			indicatedLocation = sPatch
		if swColourDistance < colourDistance:
			colourDistance = swColourDistance
			indicatedLocation = swPatch
		if wColourDistance < colourDistance:
			colourDistance = wColourDistance
			indicatedLocation = wPatch
		if nwColourDistance < colourDistance:
			colourDistance = nwColourDistance
			indicatedLocation = nwPatch

	return indicatedLocation

def findBottomest(image,notSameColour):
	bottomestX = 0
	bottomestY = 0

	for i in range(image.shape[0]):
		for j in range(image.shape[1]):
			if notSameColour[i,j]:
				if i > bottomestX:
					bottomestX = i
					bottomestY = j

	return int(bottomestX), int(bottomestY)

def findCloseEdges(image, indicatedLocation):
	region = image[indicatedLocation[0]-50:indicatedLocation[0]+50,indicatedLocation[1]-50:indicatedLocation[1]+50]
	regionGray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
	regionEdges = sobel(regionGray)
	regionEdges[regionEdges<40] = 0
	regionEdges[regionEdges>=40] = 1
	
	regionEdges.astype(bool)

	imageEdges = np.zeros([image.shape[0], image.shape[1]], dtype=bool)
	imageEdges[indicatedLocation[0]-50:indicatedLocation[0]+50,indicatedLocation[1]-50:indicatedLocation[1]+50] = regionEdges
	
	return imageEdges

def componentCoords(image,indicatedLocation,previousColour):
	# Finding the average colour of the component
	sampleColour = patchColour(image,indicatedLocation)

	# Calculating different measures of how different the previous and current colour patches are
	colourDistance = findColourDistance(sampleColour,previousColour)

	# If the colour patches are very different - start looking for a new starting point
	# Trying to find the point in the neighborhood that is more similar to the previous patch
	threshold = 5

	if colourDistance > threshold:
		indicatedLocation = findNewCentre(image, indicatedLocation, previousColour)
		sampleColour = patchColour(image, indicatedLocation)

	# Finding the edges
	imageEdges = findCloseEdges(image, indicatedLocation)

	# Traversing
	visited = np.zeros([image.shape[0], image.shape[1]], dtype=bool)
	toVisit = Queue.Queue()
	notSameColour = np.zeros([image.shape[0], image.shape[1]], dtype=bool)

	toVisit.put(indicatedLocation)

	sumX = 0
	sumY = 0
	total = 0.0

	visited[indicatedLocation[0],indicatedLocation[1]] = True
	
	while not toVisit.empty():
		currentX,currentY,visited,notSameColour,toVisit = traverseOut(image,sampleColour,visited,toVisit,notSameColour,imageEdges)
		sumX += currentX
		sumY += currentY
		total += 1

	bottomestX, bottomestY = findBottomest(image, notSameColour)

	# Centre of the component is assumed to be at the average of all of its coordinates
	centreX = int(sumX/total)
	centreY = int(sumY/total)

	return centreX, centreY, bottomestX, bottomestY, notSameColour, visited, sampleColour
	
def traverseOut(image,sampleColour,visited,toVisit,notSameColour,imageEdges):
	tolerance = 0.2

	[i,j] = toVisit.get()

	sameColour = True

	[sampleGreen, sampleRed, sampleBlue] = sampleColour
	[green, red, blue] = image[i,j]
	currentColour = image[i,j]

	# Comparing colour based on Euclidean distance
	threshold = 6
	colourDistance = findColourDistance(sampleColour, currentColour)
	sameColour = colourDistance < threshold

	if not sameColour:
		notSameColour[i,j] = True
		return i, j, visited, notSameColour, toVisit

	# If we are still within the same sample, traverse out further
	if sameColour:
		if not visited[i-1,j-1] and not imageEdges[i-1,j-1]:
			visited[i-1,j-1] = True
			toVisit.put([i-1,j-1])
		if not visited[i-1,j] and not imageEdges[i-1,j]:
			visited[i-1,j] = True
			toVisit.put([i-1,j])
		if not visited[i-1,j+1] and not imageEdges[i-1,j+1]:
			visited[i-1,j+1] = True
			toVisit.put([i-1,j+1])
		if not visited[i,j+1] and not imageEdges[i,j-1]:
			visited[i,j+1] = True
			toVisit.put([i,j+1])
		if not visited[i+1,j+1] and not imageEdges[i+1,j+1]:
			visited[i+1,j+1] = True
			toVisit.put([i+1,j+1])
		if not visited[i+1,j] and not imageEdges[i+1,j]:
			visited[i+1,j] = True
			toVisit.put([i+1,j])
		if not visited[i+1,j-1] and not imageEdges[i+1,j-1]:
			visited[i+1,j-1] = True
			toVisit.put([i+1,j-1])
		if not visited[i,j-1] and not imageEdges[i,j-1]:
			visited[i,j-1] = True
			toVisit.put([i,j-1])

	return i, j, visited, notSameColour, toVisit
