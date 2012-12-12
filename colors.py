colorDict =({'Rset1': ["#FFF200", "#7065AD", "#EE2971", "#51B848"],
			'Rset2':["#297fff", "#7137f8", "#00d400", "#ff7f2a", "#ff0000","#808080", "#000000", "#ffcc00", "#37c8ab", "#ff2ad4"],
			'CBset3':["#A7CEE2","#2078B4", "#B4D88B", "#34A048", "#F69999", "#E21F26","#FDBF6E", "#F57E20"],
			'd3set10':["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd","#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"],
			'd3set20' : ["#1f77b4", "#aec7e8","#ff7f0e", "#ffbb78","#2ca02c", "#98df8a","#d62728", "#ff9896","#9467bd", "#c5b0d5","#8c564b", "#c49c94","#e377c2", "#f7b6d2","#7f7f7f", "#c7c7c7","#bcbd22", "#dbdb8d","#17becf", "#9edae5"],
			'd3set20b':["#393b79", "#5254a3", "#6b6ecf", "#9c9ede","#637939", "#8ca252", "#b5cf6b", "#cedb9c","#8c6d31", "#bd9e39", "#e7ba52", "#e7cb94","#843c39", "#ad494a", "#d6616b", "#e7969c","#7b4173", "#a55194", "#ce6dbd", "#de9ed6"],
			'd3set20c':["#3182bd", "#6baed6", "#9ecae1", "#c6dbef","#e6550d", "#fd8d3c", "#fdae6b", "#fdd0a2","#31a354", "#74c476", "#a1d99b", "#c7e9c0","#756bb1", "#9e9ac8", "#bcbddc", "#dadaeb","#636363", "#969696", "#bdbdbd", "#d9d9d9"],
			'Rset3':["#ff6600", "#2a7fff", "#6f7c91", "#37c871","#00ffff", "#ffff00", "#ff7f2a", "#ff2a2a","#5f5fd3", "#8a6f91", "#37c871", "#8d5fd3","#87aade", "#d3bc5f", "#918a6f", "#d35f5f","#8dd35f", "#ff80b2", "#93aca7", "#37c871"]}
			)
cSet = 'Rset2'
axisdict = {'0d':'d3.format(\',f\')','1d':'d3.format(\',.1f\')','2d':'d3.format(\',.2f\')','3d':'d3.format(\',.3f\')','strf':'function(d) { return d3.time.format(\'%x\')(new Date(d))}'}