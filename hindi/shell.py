import bh

while True:
		text = input('bhasha > ')
		result, error = bh.run('<stdin>', text)

		if error: print(error.as_string())
		elif result: print(result)
