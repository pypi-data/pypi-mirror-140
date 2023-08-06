def read(file):	
		try:
			with open(file, "r") as f:
				contents = f.read()
				print (contents)
		except Exception as e:
			print (e)
def replace(file, new):
		try:
			with open(file, "w") as f:
				f.write(new)
		except Exception as e:
			print (e)
def write(file, new):
		try:
			with open (file, "a") as f:
				f.write(new)
		except Exception as e:
			print (e)
def clear(file):
		try:
			with open (file, "w") as f:
				f.write("")
		except Exception as e:
			print (e)