# imports
import sys
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Ellipse
from matplotlib.image import NonUniformImage

def save_png(plt):
	name = 'heatmap'
	plt.savefig(name + ".png")

def draw_lines(axes):
		plt.xlim([0,100])
		plt.ylim([0,68])
		axes.add_line(plt.Line2D([50, 50], [100, 0], c='w'))
		axes.add_patch(plt.Rectangle((82.3, 20.24), 15.71, 29.5, ec='w', fc='none'))
		axes.add_patch(plt.Rectangle((0, 20.24), 15.71, 29.53, ec='w', fc='none'))                       
		axes.add_patch(plt.Rectangle((94.8, 23.05), 5.2, 26.9, ec='w', fc='none'))
		axes.add_patch(plt.Rectangle((0, 23.05), 5.2, 26.9, ec='w', fc='none'))                       
		axes.add_patch(Ellipse((50, 35), 17.43, 26.91, ec='w', fc='none'))

		return axes

# helper definitions
def _create_histogram(array):
	x, y = array[:,1], array[:,2]
	heatmap, xedges, yedges = np.histogram2d(x, y, bins=50, range=[[0, 105], [0, 68]])
	heatmap = heatmap.T
	fig = plt.figure(figsize=(105/15, 68/15))
	axes = fig.add_subplot(1, 1, 1)
	im = NonUniformImage(axes, interpolation='bilinear',cmap='gnuplot')
	xcenters = (xedges[:-1] + xedges[1:]) / 2
	ycenters = (yedges[:-1] + yedges[1:]) / 2
	im.set_data(xcenters, ycenters,heatmap)
	axes.images.append(im)
	axes = draw_lines(axes)
	plt.axis('off')

	return plt

def _is_ndarray(array):
	if type(array) is np.ndarray:
		return True
	else:
		return False

# public definitions

# takes a numpy.ndarray
def heatmap(array):
	try:
		ndarray = _is_ndarray(array)
		if(ndarray):
			pass
		else:
			raise ValueError()
	except ValueError:
		print("Heatmap takes ndarray")
		sys.exit()

	plot = _create_histogram(array)

	return plot








