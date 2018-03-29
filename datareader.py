import numpy as np
import scipy.sparse as sp
import os.path

from myutils import msg

from functools import lru_cache # cache large I/O result

class DataReader:
	
	######## CONFIG #########
	data_dir = "data/"
	figure_dir = "figures/"

	users_file = data_dir + 'users_big'
	items_file = data_dir + 'movies_big'
	ratings_file = data_dir + 'ratings_big'

	ratings_cache_file = data_dir + 'ratings.npz'

	nyms_file = data_dir + 'P'
	nym_count = 8 # number of nyms in 'data/P'
	#########################
	

	def read_numpy_file(self, filename, dtype=np.float32):
		""" Read from numpy file if it exists, otherwise from raw text file """
		with msg(f'Reading "{filename}"'):
			if os.path.isfile(filename + ".npy"): 
				return np.load(filename + ".npy")
			else: 
				return np.loadtxt(open(filename + ".txt", "r"), dtype=dtype)

	@lru_cache(maxsize=1)
	def get_ratings(self):
		""" Returns the ratings matrix in compressed sparse column (csc) format.
		Stores csc matrix to ratings_cache_file for faster loading in future.
		Cached result to allow single load on multiple calls. 
		"""
		filename = self.ratings_cache_file
		if os.path.isfile(filename):
			with msg(f'Loading rating matrix from "{filename}"'):
				ratings = sp.load_npz(filename)
		else:
			f_ratings = self.read_numpy_file(self.ratings_file)
			f_users = self.read_numpy_file(self.users_file, dtype=int)
			f_items = self.read_numpy_file(self.items_file, dtype=int)
			with msg('Forming rating matrix'):
				ratings = sp.coo_matrix((f_ratings, (f_users, f_items)), dtype=np.float32).tocsc()
			with msg('Saving rating matrix to "{}"'.format(filename)):
				sp.save_npz(filename, ratings)
		return ratings

	@lru_cache(maxsize=1)
	def get_nyms(self):
		""" Returns the nyms as a list of numpy arrays.
		Cached result to allow single load on multiple calls.
		"""
		filename = self.nyms_file
		with msg(f'Reading nyms from "{filename}"'), open(filename, 'r') as f: 
			nyms_raw = np.loadtxt(f, delimiter=',', dtype=int)
			# parse into list of nyms
			return [ nyms_raw[:,0][nyms_raw[:,1]==nym_n] for nym_n in range(0, self.nym_count) ]