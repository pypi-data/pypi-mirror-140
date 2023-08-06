def en_int(x):
	return int(x)


def en_contain(*args):

	def check(x):
		# print(x)
		argss=list(args)
		for a in argss:
			# print(a ,x)
			if str(a) in x:
				return True
			else:
				pass
		# vv=[str(v) for v in args]
		# print(vv)
		# return x in vv
	return check


# a=en_contain(':')
# a=a('dfs:sdfsdf',)
#
# print(a)