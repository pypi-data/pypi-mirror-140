import pandas as pd
import os
import pickle
import pkg_resources

from glycowork.motif.processing import get_lib

io = pkg_resources.resource_stream(__name__, "glyco_targets_species_seq_all_V5.csv")
df_species = pd.read_csv(io)
io = pkg_resources.resource_stream(__name__, "v5_sugarbase.csv")
df_glycan = pd.read_csv(io)
io = pkg_resources.resource_stream(__name__, "df_glysum_v5.csv")
df_glysum = pd.read_csv(io)
df_glysum = df_glysum.iloc[:,1:]
io = pkg_resources.resource_stream(__name__, "glycan_motifs.csv")
motif_list = pd.read_csv(io)
io = pkg_resources.resource_stream(__name__, "glycan_binding.csv")
glycan_binding = pd.read_csv(io)
this_dir, this_filename = os.path.split(__file__)  # Get path of data.pkl
data_path = os.path.join(this_dir, 'glycan_representations_species.pkl')
glycan_emb = pickle.load(open(data_path, 'rb'))

lib = get_lib(list(set(df_glycan.glycan.values.tolist() +
                       df_species.target.values.tolist() +
                       motif_list.motif.values.tolist() +
                       glycan_binding.columns.values.tolist()[:-1] +
                       ['monosaccharide','Sia'])))

linkages = ['a1-1','a1-2','a1-3','a1-4','a1-5','a1-6','a1-7','a1-8','a1-9','a1-11','a1-z','a2-1','a2-2','a2-3','a2-4','a2-5','a2-6','a2-7','a2-8','a2-9','a2-11','b1-1','b1-2','b1-3','b1-4','b1-5','b1-6','b1-7','b1-8','b1-9','b1-z','b2-1','b2-2','b2-3','b2-4','b2-5','b2-6','b2-7','b2-8','z1-z','z2-z','z1-2','z1-3','z1-4','z1-6','z2-3','z2-6','z2-8']
Hex = ['Glc', 'Gal', 'Man', 'Hex']
dHex = ['Fuc', 'Qui', 'Rha', 'dHex']
HexNAc = ['GlcNAc', 'GalNAc', 'ManNAc', 'HexNAc']
Sia = ['Neu5Ac', 'Neu5Gc', 'Kdn', 'Sia']

def unwrap(nested_list):
  """converts a nested list into a flat list"""
  out = [item for sublist in nested_list for item in sublist]
  return out

def find_nth(haystack, needle, n):
  """finds n-th instance of motif\n
  | Arguments:
  | :-
  | haystack (string): string to search for motif
  | needle (string): motif
  | n (int): n-th occurrence in string\n
  | Returns:
  | :-
  | Returns starting index of n-th occurrence in string 
  """
  start = haystack.find(needle)
  while start >= 0 and n > 1:
    start = haystack.find(needle, start+len(needle))
    n -= 1
  return start

def reindex(df_new, df_old, out_col, ind_col, inp_col):
  """Returns columns values in order of new dataframe rows\n
  | Arguments:
  | :-
  | df_new (pandas dataframe): dataframe with the new row order
  | df_old (pandas dataframe): dataframe with the old row order
  | out_col (string): column name of column in df_old that you want to reindex
  | ind_col (string): column name of column in df_old that will give the index
  | inp_col (string): column name of column in df_new that indicates the new order; ind_col and inp_col should match\n
  | Returns:
  | :-
  | Returns out_col from df_old in the same order of inp_col in df_new
  """
  if ind_col != inp_col:
    print("Mismatching column names for ind_col and inp_col. Doesn't mean it's wrong but pay attention.")
  out = [df_old[out_col].values.tolist()[df_old[ind_col].values.tolist().index(k)] for k in df_new[inp_col].values.tolist()]
  return out

def load_file(file):
  """loads .csv files from glycowork package\n
  | Arguments:
  | :-
  | file (string): name of the file to be loaded
  """
  try:
    temp = pd.read_csv("../glycan_data/" + file)
  except:
    temp = pd.read_csv("glycowork/glycan_data/" + file)
  return temp
