################################################################################
# Step 4: Extract Features
#
# Script parses lyrics to consider gender and love/sex/affection references 
# and adds relevant features to the data.
#
################################################################################

# Import packages
#---------------------------------------------
import pandas as pd

# Setup
#---------------------------------------------

# Paths
lyricdatapath = './output/song-data-lyrics.csv'
flaglistspath = './process/flag-words.xlsx'
outputpath = './output/song-data-plus.csv'

# Read in lyric data
data = pd.read_csv(lyricdatapath)

# Read in list of flag words (downloaded as .xlsx from Google drive) and save to lists
femflags = pd.read_excel(flaglistspath, sheet_name='womanFlags', header=None).values[:, 0].tolist()
mascflags = pd.read_excel(flaglistspath, sheet_name='manFlags', header=None).values[:, 0].tolist() # if always reads first sheet, update pandas package (pip install --upgrade pandas)
loveflags = pd.read_excel(flaglistspath, sheet_name='loveFlags', header=None).values[:, 0].tolist()

# Pad each flag in lists with spaces (instead of tokenizing?)
femflags = [(" " + f + " ") for f in femflags]
mascflags = [(" " + f + " ") for f in mascflags]
loveflags = [(" " + f + " ") for f in loveflags]
 
# Functions
#---------------------------------------------

def referenceType(row):
	'''
	Takes row of songs with lyrics dataframe
	Catagorizes songs based on the gender of the artist and gender references in the lyrics
	'''
	if row['femflag'] == 0 & row['mascflag'] == 0:
		return 'No reference'
	elif row['femflag'] == 1 & row['mascflag'] == 1:
		return 'Masc & fem reference'
	elif (row['gender'] == 'man' and row['mascflag'] == 1) | (row['gender'] == 'woman' and row['femflag'] == 1):
		return 'Same-gender'
	elif (row['gender'] == 'man' and row['femflag'] == 1) | (row['gender'] == 'woman' and row['mascflag'] == 1):
		return 'Opposite-gender'

def proPhraseRegex(flaglist):
	'''
	Takes a List
	Creates a regex to match the phrase (5 words before and after) a pronoun search term
	Wont get phrases at the beginning or end of song, regex to capture those too took too long
	TODO - if taking too long, only do this for ones that contain the pronoun, but we dont have too much data
	'''
	regex = '(?:[a-z]+ ){5}[a-z]+'
	for f in flaglist[:-1]:
		regex = regex + f + '(?:[a-z]+ ){5}[a-z]+' + '|' + '(?:[a-z]+ ){5}[a-z]+'
	return regex + flaglist[-1] + '(?:[a-z]+ ){5}[a-z]+'

# Data process
#---------------------------------------------

# Pad spaces (instead of tokenizing?)
data['lyrics'] = " " + data['lyrics'] + " "

# Create indicator variables for flag words
data['femflag'] = data['lyrics'].apply(lambda x: any([f in x for f in femflags])).astype(int)
data['mascflag'] = data['lyrics'].apply(lambda x: any([f in x for f in mascflags])).astype(int)
data['loveflag'] = data['lyrics'].apply(lambda x: any([f in x for f in loveflags])).astype(int)

# Create category variable for song based on gender references in lyrics and artist identity
data['genderref'] = data.apply(referenceType, axis=1)
print(data['genderref'].value_counts()) # Quick table
print(data.loc[data['loveflag'] == 1]['genderref'].value_counts()) # Quick table

# Extract pronoun phrases, remove dups (maybe should keep?)
data['femphrases'] = data['lyrics'].str.findall(proPhraseRegex(femflags))
data['femphrases'] = [', '.join(map(str, l)) for l in list(map(set,data['femphrases']))]
data['mascphrases'] = data['lyrics'].str.findall(proPhraseRegex(mascflags))
data['mascphrases'] = [', '.join(map(str, l)) for l in list(map(set,data['mascphrases']))]
data['lovephrases'] = data['lyrics'].str.findall(proPhraseRegex(loveflags))
data['lovephrases'] = [', '.join(map(str, l)) for l in list(map(set,data['lovephrases']))]

# Write out
data.to_csv(outputpath, index=False, encoding='utf-8-sig')