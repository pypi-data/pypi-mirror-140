import glob
import pandas as pd
import os

ss_folders = glob.glob('single_source*')
metadata_list = []

for i,folder in enumerate(ss_folders):
	print(folder)
	# First we want to move all of the numpy images to the desired folder
	npy_files = glob.glob(os.path.join(folder,'*.npy'))
	for j,file in enumerate(npy_files):
		new_path = os.path.join('ss_comp/image_%07d' % (i*50000+j))
		# Don't do this if the file is already there
		if os.path.exists(new_path):
			raise ValueError('%s already exists'%(new_path))
		else:
			print(new_path)
			os.rename(file,new_path)

	# Read the metadata file
	cm = pd.read_csv(os.path.join(folder,'metadata.csv'))
	metadata_list.append(cm)

metadata = pd.concat(metadata_list)
metadata.to_csv('ss_comp/metadata.csv', index=None)