import pandas as pd
import pylab as pl
import matplotlib.pyplot as plt
import numpy as np
import pprint as pp

numerics = ['x', 'y']
plot_components = ['x', 'y', 'color', 'shape']

def get_subplot(df, groupers):
	plot_dict = {}
	for col in df:
		if col in numerics:
			plot_dict[col] = df[col].tolist()
		elif col in groupers:
			if len(df[col].unique())==0:
				continue
			plot_dict[col] = np.unique(df[col]).tolist()[0]
		else:
			plot_dict[col] = df[col].tolist()
	return plot_dict

def prep_for_plot(df, facets=[]):
	plot_data = []
	if len(facets) > 0:
		for facet in facets:
			print "facet", facet
			facet_values = df[facet].unique()
			for facet_value in facet_values:
				facet_mask = df[facet]==facet_value
				plt_df = df[facet_mask]
				subplot = get_subplot(plt_df)
				plot_data.append(subplot)
	else:
		plot_data.append(get_subplot(df))
	print plot_data
	return plot_data


df = pd.DataFrame({
	"x": range(1, 20),
})

df['y'] = df['x'].apply(lambda x: x * 10 if x%2==0 else x - 10)
df['color'] = df['x'].apply(lambda x: "blue" if x%2==0 else "green")
df['mood'] = df['x'].apply(lambda x: "sad" if x%3==0 else "happy")
df['name'] = df['x'].apply(lambda x: "sam" if x%5==0 else "greg")






facets = []
facets = ['mood']
facet_values = []
facet_x = 'mood'
facet_y = 'name'
facet_values_x = []
facet_values_y = []

# facet wrap
subplots = []
for facet in facets:
	facet_values += df[facet].unique().tolist()
	for facet_value in df[facet].unique():
		mask = df[facet]==facet_value
		layers = df[mask].groupby(groupers).apply(get_subplot).tolist()
		subplots.append(layers)
if len(facets)==0:
	subplots.append(df.groupby(groupers).apply(get_subplot).tolist())

fix, axs = plt.subplots(len(subplots))

if len(facets)==0:
	axs = [axs]

for (ax, facet_name, subplot) in zip(axs, facet_values, subplots):
	for layer in subplot:
		layer = {k: v for k, v in layer.iteritems() if k in plot_components}
		ax.scatter(**layer)
	ax.set_title(facet_name)

pl.show()

def facet_grid(df, groupers, facet_x, facet_y):
	
	groupers = [group for group in groupers if group in df.columns]

	facet_values_x = df[facet_x].unique()
	facet_values_y = df[facet_y].unique()


	fig_plots = []
	for x_value in facet_values_x:
		subplots = []
		for y_value in facet_values_y:
			mask = (df[facet_x]==x_value) & (df[facet_y]==y_value)
			if groupers:
				layers = df[mask].groupby(groupers).apply(lambda x: get_subplot(x, groupers + [facet_x, facet_y])).tolist()
			else:
				layers = [get_subplot(df[mask], groupers + [facet_x, facet_y])]
			subplots += layers
			# subplots.append(layers)
		fig_plots.append(subplots)
	return fig_plots


	fig, axs = plt.subplots(len(facet_values_x), len(facet_values_y))

	for dim, subplots in zip(axs, fig_plots):
		for (ax, subplot) in zip(dim, subplots):
			for layer in subplot:
				layer = {k: v for k, v in layer.iteritems() if k in plot_components}
				ax.scatter(**layer)

	return axs

# plots = df.groupby(groupers).apply(prep_for_plot)
# for plot in plots:
# 	print plot
# print len(plots)

# facets = ['x']
# plots = df.groupby(facets).apply(prep_for_plot).tolist()
# # plots = df.groupby(groupers).apply(lambda x: prep_for_plot(x, ["x"])).tolist()
# # for plot in plots:
# # 	print plot


# facet_levels = len(plots)
# print facet_levels
# fix, axs = plt.subplots(facet_levels)

# pp.pprint(plots)

# for ax, plot in zip(axs, plots):
# 	ax.scatter(**plot)


# for plot_dict in plot_dicts:
# 	pl.scatter(**plot_dict)
# pl.show()
