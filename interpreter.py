from nltk.corpus import wordnet
import sys
import  nltk
from nltk.stem.lancaster import LancasterStemmer
st = LancasterStemmer()

doc_name = sys.argv[1]
# table_data = sys.argv[2]

# doc_name :: file consisting of natural language queries which need to be converted
# to SQL queries
#
# table_data :: file containing the table columns, of each table
# student : name, id, age ...
# teacher : name, Emp_id ...
#
#
#
#
#

d = {'a':0, 'an':0, 'the':0, 'select':0, 'find':0, 'which':0, 'whose':0, 'is':0, 'of':0, 'a':0, 'with':0, 'to':0, 'for':0, 'are':0, 'and':0, 'what':0, 'who':0, 'got':0}
Noun_list = []
col_dict = {}
table_names = []
cols_in_table = {}

def line(sentence):
	"""
	function tokenizes, removes stop words and escape words

	"""
	sentence = sentence.lower()
	toks = nltk.word_tokenize(sentence)
	final_list = []

	for word in toks:
		try:
			d[word]
		except:
			# final_list.append(st.stem(word))
			final_list.append(word)

	return final_list

# print(st.stem('over'))
# line('Select players who are above 80')
line('find the names of students having marks between 40 and 70')

def noun_table(table_data):
	file = open(table_data)
	global col_dict
	global table_names
	global Noun_list
	global cols_in_table

	for line in file:
		line = line.rstrip().lower()
		L = line.split(' ')

		for l in L:
			if(l not in Noun_list):
				Noun_list.append(l)

		table_name = L[0]; table_columns = L[1:]
		table_names.append(table_name)
		cols_in_table[table_name] = table_columns

		for col in table_columns:
			try:
				col_dict[col].append(table_name)
			except:
				col_dict[col] = [table_name]


def match_sentence(sentence):
	# sent = line(sentence)
	sent = sentence
	tables = []
	marking = []
	symbols = ['<', '>', '=']

	for word in sent:
		if(word in table_names):
			# asssuming same word as table name appeared in the sentence
			tables.append(word)
			marking.append('tab')
		elif(word in Noun_list):
			marking.append('col')
		elif(word in symbols):
			marking.append('sym')
		else:
			marking.append('val')

	# print(marking)
	return marking


def parse_sentence(sentence):
	S = sentence.split('-')
	sentence = S[0]; columns = S[1]
	columns = columns.split(' ')
	words = line(sentence)
	N = len(words)

	feed_input = []
	i = 0
	while(i < N):
		if(i < N-1 and words[i] == 'more' and words[i+1] == 'than'):
			feed_input.append('>')
			i += 2
		if(i < N-1 and words[i] == 'less' and words[i+1] == 'than'):
			feed_input.append('<')
			i += 2
		if(words[i] == 'between'):
			feed_input.append('btwin')
			i += 1
		else:
			feed_input.append(words[i])
			i += 1

	words_type = match_sentence(feed_input)
	print(feed_input)
	print(words_type)

	final_query = {}
	tables = []
	# print(words_type)

	for i in range(len(words_type)):
		if(words_type[i] == 'tab'):
			tables.append(i)

	print(tables)

	if(len(tables) == 1):
		final_query = {'tab' : {'list' : []}, 'join' : False, 'conds' : [], 'cols':columns}
		final_query['tab']['list'] = [feed_input[tables[0]]]
		final_query['join'] = False
		conds = []
		final_query['tab']['conds'] = conds

		i = 0; N = len(words_type)
		pred = []
		dic = {'name' : '', 'preds': []}

		VALSET = False; SYMSET = False; COLSET = False
		val = 0; sym = ''; col = ''
		while(i < N):
			print(i)
			if(words_type[i] != 'tab'):
				
				if(words_type[i] == 'sym'):
					sym = feed_input[i]
					SYMSET = True
				if(words_type[i] == 'val'):
					val = feed_input[i]
					VALSET = True
				
				if(VALSET and SYMSET):
					pred.append([sym, val])
					VALSET = False; SYMSET = False
					if(dic['name'] != ''):
						dic['preds'].extend(pred)
						pred = []
				
				if(not COLSET and words_type[i] == 'col'):
					col = feed_input[i]
					COLSET = True
					dic['name'] = col
					if(pred != []):
						dic['preds'].extend(pred)
						pred = []
					i += 1
					continue

				if(COLSET and words_type[i] == 'col'):
					if(pred != []):
						dic['preds'].extend(pred)
						pred = []
					
					conds.append(dic)
					col = feed_input[i]	
					# print(col)
					dic = {'name' : col, 'preds': []}
					i += 1
					continue

				i += 1

			elif(words_type[i] == 'tab'):
				i += 1
		
		if(pred != [] or dic['preds'] != []):
			dic['preds'].extend(pred)
			conds.append(dic)
	
	else:
	# Natural Join tables
		sentence = S[0].split('*')
		tables = sentence[1]
		sentence = sentence[0]+sentence[2]
		words = line(sentence)
		tables = tables.split(' ')

		N = len(words)

		feed_input = []
		i = 0
		while(i < N):
			if(i < N-1 and words[i] == 'more' and words[i+1] == 'than'):
				feed_input.append('>')
				i += 2
			if(i < N-1 and words[i] == 'less' and words[i+1] == 'than'):
				feed_input.append('<')
				i += 2
			if(words[i] == 'between'):
				feed_input.append('btwin')
				i += 1
			else:
				feed_input.append(words[i])
				i += 1

		words_type = match_sentence(feed_input)
		print(feed_input)
		print(words_type)

		final_query = {}

		final_query = {'tab' : {'list' : []}, 'join' : False, 'conds' : [], 'cols':columns}
		final_query['tab']['list'] = tables
		final_query['join'] = True
		conds = []
		final_query['tab']['conds'] = conds

		i = 0; N = len(words_type)
		pred = []
		dic = {'name' : '', 'preds': []}

		VALSET = False; SYMSET = False; COLSET = False
		val = 0; sym = ''; col = ''
		
		while(i < N):
				if(words_type[i] == 'sym'):
					sym = feed_input[i]
					SYMSET = True
				if(words_type[i] == 'val'):
					val = feed_input[i]
					VALSET = True
				
				if(VALSET and SYMSET):
					pred.append([sym, val])
					VALSET = False; SYMSET = False
					if(dic['name'] != ''):
						dic['preds'].extend(pred)
						pred = []
				
				if(not COLSET and words_type[i] == 'col'):
					col = feed_input[i]
					COLSET = True
					dic['name'] = col
					if(pred != []):
						dic['preds'].extend(pred)
						pred = []
					i += 1
					continue

				if(COLSET and words_type[i] == 'col'):
					if(pred != []):
						dic['preds'].extend(pred)
						pred = []
					
					conds.append(dic)
					col = feed_input[i]	
					# print(col)
					dic = {'name' : col, 'preds': []}
					i += 1
					continue

				i += 1
		
		if(pred != [] or dic['preds'] != []):
			dic['preds'].extend(pred)
			conds.append(dic)


	print(final_query)
	dic_to_table(final_query)

def same_column(table1, table2):
	col_table1 = cols_in_table[table1]
	col_table2 = cols_in_table[table2]

	l = [value for value in col_table1 if value in col_table2]

	part_query = ''
	
	for i in range(len(l)):
		part_query += table1 + '.' + l[i] + ' = '+ table2 + '.' + l[i] 
		part_query += '\n'
	return part_query


def dic_to_table(DIC):
	query = ''
	join = DIC['join']
	table_names = DIC['tab']['list']
	cols = DIC['cols']

	if(len(table_names) == 1):
		TABLE = table_names[0]
		
		if(len(cols) == 0):
			COL = '*'
		else:
			COL = ','.join(cols)


		query = query + 'SELECT ' + COL + ' FROM ' + TABLE

		# Conditions unpack
		holder = DIC['tab']['conds']
		PRED = ''
		for i in range(len(holder)):
			l = holder[i]
			col_name = l['name']
			preds = l['preds']
			
			for j in range(len(preds)):
				p = preds[j]
				s = col_name + ' ' + p[0] + ' ' + p[1] 
				if(PRED != ''):
					PRED += ' AND ' + s
				else:
					PRED += s
		query += ' WHERE ' + PRED
		print(query)
	
	else:
		# Natural join on the table columns
		query = 'SELECT '

		if(len(cols) == 0):
			COL = '*'
		else:
			COL = ','.join(cols)

		join_pred = same_column(table_names[0], table_names[1])
		query += COL + ' FROM ' + table_names[0]
		query += '\n'
		query += 'INNER JOIN ' + table_names[1] + ' ON ' + join_pred + '\n' 
		# Conditions unpack
		holder = DIC['tab']['conds']
		PRED = ''

		for i in range(len(holder)):
			l = holder[i]
			col_name = l['name']
			preds = l['preds']
			
			for j in range(len(preds)):
				p = preds[j]
				s = col_name + ' ' + p[0] + ' ' + p[1] 
				if(PRED != ''):
					PRED += ' AND ' + s
				else:
					PRED += s
		query += ' WHERE ' + PRED
		print(query)



noun_table('in.txt')
print(table_names)
# print(col_dict)
# print(Noun_list)
# match_sentence('student who got more than 10 marks')
parse_sentence('student who got more than 10 and less than 45 marks with roll_no more than 50-marks')