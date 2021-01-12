# Keyboard layout benchmarker
# Copyright (c) 2017 MakotoKurauchi
# MIT License

import sys
import time
import json
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter

# make charactors into Caps in a dataframe
def cap (dtfr):
	for i, v in dtfr.iterrows():
		for j in dtfr[i:i]:
			dtfr.at[i, j] = str( dtfr.at[i, j] ). upper()
			#print(dtfr.at[i, j])
	return dtfr

############### pick up keymap.txt ################
def pickup_txt(lines):
	c_dict = {}
	for i, line in enumerate(lines):
		#print(line)
		for j, c in enumerate(line):
			if(c != "\n"):
				#print(c, end="")
				#print(i, end="")
				#print(j, end="\n")
				c_dict[c] = [i, j]
	#print(c_dict)
	return c_dict

###################### cost ################################
def calc_cost(txt_lst, keymap, cost):
	p_cost = 0
	h_cost = 0
	count = 0
	lasthand = 0
	lastfinger = 0
	for i, c in enumerate(txt_lst):
		if (c in keymap) or (c.upper() in keymap):
			#Each element of `keymip_dict` is like `"a":[3, 2]`
			#That means A key is at 3rd row and 2nd colum.
			row = keymap_dict[c][0]
			col = keymap_dict[c][1]

			# position cost
			p_cost += cost["position"][row][col]

			# hand/finger cost
			## Alternating one hand and the other is nice
			if lasthand != cost["hand"][row][col]:
				h_cost += 1
			else:
				if lastfinger != cost["finger"][row][col]:
					h_cost += 4
				else:
					h_cost += 5

			lasthand = cost["hand"][row][col]
			lastfinger = cost["finger"][row][col]
			count += 1
			
	print("\nPosition cost   :", "{0:4d}".format(int(p_cost/count*100)))
	print("Hand/Finger cost:", "{0:4d}".format(int(h_cost/count*100)))
	print("Total cost      :", "{0:4d}".format(int((p_cost/count + h_cost/count)*100)))


######################### heatmap ############################
def draw_heatmap(txt_lst, keymap_dict, layout_name, mode):
	lst = []
	keycounter_dict = Counter(txt_lst)
	for k, v in keycounter_dict.items():
		if k in keymap_dict:
			lst.append([k, v, keymap_dict[k][0], keymap_dict[k][1]])
		#else:
			#print(k ,"is no match.")

	df = pd.DataFrame(lst,columns=["key", "num", "row", "col"])
	pivots = df.pivot("row","col","num")
	labels = df.pivot("row","col","key")
	labels_cap = cap(labels)
	#labels.str.replace(str.upper())
	for i, v in labels.iterrows():
		for j in labels[i:i]:
			labels.at[i, j] = str( labels.at[i, j] ). upper()

	print("\nkeymap: ")
	print(labels)

	sns.heatmap(pivots, annot=labels, fmt='', cbar=False, square=True, linewidths=1, cmap="PuRd")

	plt.title(layout_name)
	if(mode == "show"):
		plt.show()
	elif(mode == "save"):
		img_name = "img/" + layout_name + ".jpg"
		plt.savefig(img_name)




if __name__ == '__main__':
	######################### load files ###############################
	argvs = sys.argv
	if (len(argvs) != 4):
		print ('Usage: $ python %s textfile keymap.json cost.json' % argvs[0])
		quit()

	f = open(argvs[1],'r')						#text's name will
	txt_lst = f.read()								#charactor array
	print("\n\""+ argvs[1] +"\" has ",len( txt_lst) , " charactors.")
	f.close()

	'''f = open(argvs[2],'r')						#[keymap].json
	keymap_dict = json.load(f)
	print(keymap_dict)
	f.close()'''
	f = open(argvs[2] + "/" + argvs[3] + ".txt", 'r')						#[keymap].json
	keymap_dict = pickup_txt(f)
	pickup_txt(f.readlines())
	f.close()

	f = open(argvs[2] + "/cost.json" ,'r')						#cost.json
	cost_dict = json.load(f)
	f.close()

	calc_cost( txt_lst, keymap_dict, cost_dict)

	keymap_name = argvs[3]
	draw_heatmap( txt_lst, keymap_dict, keymap_name, "show" )    # choose one.    
	#draw_heatmap( txt_lst, keymap_dict, keymap_name, "save" )
