__version__ = '0.1.0'

__version__ = '0.1.0'

# MUST ACTIVATE OR FUNCTIONS WILL RETURN NONE

activated = False

def activate(quiet): # activates module
	global activated
	activated = True
	if quiet == True: # boi.activate(quiet = True) passes
		pass
	else: # boi.activate(quiet = False) thanks client for using this module
		print("Thank You For Using The Boi Module!")
		import time
		time.sleep(2)
		import os
		os.system('clear')

def unactivate():
	global activated
	if activated == True:
		activated = False
	else:
		pass

def multiples(num, multiples): # prints multiples of num
	if activated == True:
		for i in range(multiples + 1):
			if num * i != 0:
				print(num * i)

def add(x, y): # returns the sum of x and y
	if activated == True:
		return x + y

def minus(x, y): # returns the difference of x and y
	if activated == True:
		return x - y

def divide(x, y): # returns the quotient of x and y
	if activated == True:
		return x / y

def multiply(x, y): # returns the product of x and y
	if activated == True:
		return x * y

def none(): # returns None
	if activated == True:
		return None

def true(): # returns True
	if activated == True:
		return True

def false(): # returns False
	if activated == True:
		return False

def scan(x, y): # if y is in x then it will return True else it will return false
	if activated == True:
		for i in x:
			if i == y:
				return True
		else:
			return False

def abval(n): # returns the absolute value of n
	if activated == True:
		if n > 0:
			return n
		elif n < 0:
			n = n - (n * 2)
			return n
		else:
			return 0

# NO NEED TO ACTIVATE FOR TEXT MODS
# print color text with these - example: print(boi.blue + "hello")
class textmods():

	black = "\033[0;30m"
	red = "\033[0;31m"
	yellow = "\033[0;33m"
	green = "\033[0;32m"
	blue = "\033[0;34m"
	purple = "\033[0;35m"

	white_bg = "\x1b[6;30;47m"
	red_bg = "\x1b[6;30;41m"
	yellow_bg = "\x1b[6;30;43m"
	green_bg = "\x1b[6;30;42m"
	blue_bg = "\x1b[6;30;46m"
	purple_bg = "\x1b[6;30;45m"

	underline = "\033[0;4m"
	color_reset = "\033[0m"

def fuse(x, y): # joins the two lists (x and y)
	if activated == True:
		for i in x:
			y.append(i)
		x.clear()
		return y

def slowtype(string, delay): # types each letter in the string after the delay timing
	if activated == True:
		for i in string:
			print(i, end = "", flush = True)
			import time
			time.sleep(delay)
		print()

def greet(name, program_name): # greets the client
	if activated == True:
		print(f"Hello {name}, Welcome To {program_name}")

def power_of(num, powerof): # returns the num to the power of powerof
	if activated == True:
		return num ** powerof

def root(num, root): # returns the certain given root of num
	if activated == True:
		return int(num) ** (1 / int(root))

def randint(x, y): # returns random integer between x and y
	if activated == True:
		import random
		return random.randint(x, y)

def randfloat(x, y): # returns random float between x and y
	if activated == True:
		import random
		return random.uniform(x, y)

def file_write(file_name, string): # opens and writes message in file_name (files name)
	if activated == True:
		file = open(file_name, "a")
		file.write(string)

def loop_print(string_to_print, loop_length): # prints a string loop_length times
	if activated == True:
		for i in range(loop_length):
			print(string_to_print)

def bold(x): # returns the bold reprint of x
	if activated == True:
		b = "𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇"
		Bold = list(b)
		result = []
		t = Bold
		for i in x:
			if i == "a":result.append(t[ord(i) - 97])
			if i == "b":result.append(t[ord(i) - 97])
			if i == "c":result.append(t[ord(i) - 97])
			if i == "d":result.append(t[ord(i) - 97])
			if i == "e":result.append(t[ord(i) - 97])
			if i == "f":result.append(t[ord(i) - 97])
			if i == "g":result.append(t[ord(i) - 97])
			if i == "h":result.append(t[ord(i) - 97])
			if i == "i":result.append(t[ord(i) - 97])
			if i == "j":result.append(t[ord(i) - 97])
			if i == "k":result.append(t[ord(i) - 97])
			if i == "l":result.append(t[ord(i) - 97])
			if i == "m":result.append(t[ord(i) - 97])
			if i == "n":result.append(t[ord(i) - 97])
			if i == "o":result.append(t[ord(i) - 97])
			if i == "p":result.append(t[ord(i) - 97])
			if i == "q":result.append(t[ord(i) - 97])
			if i == "r":result.append(t[ord(i) - 97])
			if i == "s":result.append(t[ord(i) - 97])
			if i == "t":result.append(t[ord(i) - 97])
			if i == "u":result.append(t[ord(i) - 97])
			if i == "v":result.append(t[ord(i) - 97])
			if i == "w":result.append(t[ord(i) - 97])
			if i == "x":result.append(t[ord(i) - 97])
			if i == "y":result.append(t[ord(i) - 97])
			if i == "z":result.append(t[ord(i) - 97])
			if i == " ":result.append(" ")

		return "".join(result)

def italic(x): # returns the italic reprint of x
	if activated == True:
		i = "𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻"
		Italic = list(i)
		result = []
		t = Italic
		for i in x:
			if i == "a":result.append(t[ord(i) - 97])
			if i == "b":result.append(t[ord(i) - 97])
			if i == "c":result.append(t[ord(i) - 97])
			if i == "d":result.append(t[ord(i) - 97])
			if i == "e":result.append(t[ord(i) - 97])
			if i == "f":result.append(t[ord(i) - 97])
			if i == "g":result.append(t[ord(i) - 97])
			if i == "h":result.append(t[ord(i) - 97])
			if i == "i":result.append(t[ord(i) - 97])
			if i == "j":result.append(t[ord(i) - 97])
			if i == "k":result.append(t[ord(i) - 97])
			if i == "l":result.append(t[ord(i) - 97])
			if i == "m":result.append(t[ord(i) - 97])
			if i == "n":result.append(t[ord(i) - 97])
			if i == "o":result.append(t[ord(i) - 97])
			if i == "p":result.append(t[ord(i) - 97])
			if i == "q":result.append(t[ord(i) - 97])
			if i == "r":result.append(t[ord(i) - 97])
			if i == "s":result.append(t[ord(i) - 97])
			if i == "t":result.append(t[ord(i) - 97])
			if i == "u":result.append(t[ord(i) - 97])
			if i == "v":result.append(t[ord(i) - 97])
			if i == "w":result.append(t[ord(i) - 97])
			if i == "x":result.append(t[ord(i) - 97])
			if i == "y":result.append(t[ord(i) - 97])
			if i == "z":result.append(t[ord(i) - 97])
			if i == " ":result.append(" ")

		return "".join(result)

def small(x): # returns the small reprint of x
	if activated == True:
		s = "ᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖᵠʳˢᵗᵘᵛʷˣʸᶻ"
		Small_letters = list(s)
		result = []
		t = Small_letters
		for i in x:
			if i == "a":result.append(t[ord(i) - 97])
			if i == "b":result.append(t[ord(i) - 97])
			if i == "c":result.append(t[ord(i) - 97])
			if i == "d":result.append(t[ord(i) - 97])
			if i == "e":result.append(t[ord(i) - 97])
			if i == "f":result.append(t[ord(i) - 97])
			if i == "g":result.append(t[ord(i) - 97])
			if i == "h":result.append(t[ord(i) - 97])
			if i == "i":result.append(t[ord(i) - 97])
			if i == "j":result.append(t[ord(i) - 97])
			if i == "k":result.append(t[ord(i) - 97])
			if i == "l":result.append(t[ord(i) - 97])
			if i == "m":result.append(t[ord(i) - 97])
			if i == "n":result.append(t[ord(i) - 97])
			if i == "o":result.append(t[ord(i) - 97])
			if i == "p":result.append(t[ord(i) - 97])
			if i == "q":result.append(t[ord(i) - 97])
			if i == "r":result.append(t[ord(i) - 97])
			if i == "s":result.append(t[ord(i) - 97])
			if i == "t":result.append(t[ord(i) - 97])
			if i == "u":result.append(t[ord(i) - 97])
			if i == "v":result.append(t[ord(i) - 97])
			if i == "w":result.append(t[ord(i) - 97])
			if i == "x":result.append(t[ord(i) - 97])
			if i == "y":result.append(t[ord(i) - 97])
			if i == "z":result.append(t[ord(i) - 97])
			if i == " ":result.append(" ")

		return "".join(result)

def dollarword(x): # returns True if x is a dollar word otherwise returns False
	if activated == True:
		result = 0
		for i in x:
			if i == "a": result = result + (ord(i) - 96)
			if i == "b": result = result + (ord(i) - 96)
			if i == "c": result = result + (ord(i) - 96)
			if i == "d": result = result + (ord(i) - 96)
			if i == "e": result = result + (ord(i) - 96)
			if i == "f": result = result + (ord(i) - 96)
			if i == "g": result = result + (ord(i) - 96)
			if i == "h": result = result + (ord(i) - 96)
			if i == "i": result = result + (ord(i) - 96)
			if i == "j": result = result + (ord(i) - 96)
			if i == "k": result = result + (ord(i) - 96)
			if i == "l": result = result + (ord(i) - 96)
			if i == "m": result = result + (ord(i) - 96)
			if i == "n": result = result + (ord(i) - 96)
			if i == "o": result = result + (ord(i) - 96)
			if i == "p": result = result + (ord(i) - 96)
			if i == "q": result = result + (ord(i) - 96)
			if i == "r": result = result + (ord(i) - 96)
			if i == "s": result = result + (ord(i) - 96)
			if i == "t": result = result + (ord(i) - 96)
			if i == "u": result = result + (ord(i) - 96)
			if i == "v": result = result + (ord(i) - 96)
			if i == "w": result = result + (ord(i) - 96)
			if i == "x": result = result + (ord(i) - 96)
			if i == "y": result = result + (ord(i) - 96)
			if i == "z": result = result + (ord(i) - 96)
			if i == " ": result = result + (ord(i) - 96)
		if result == 100: return True
		else: return False

def clock(offset): # displays UTC time minus the offset
	if activated == True:
		import time
		return (int(time.strftime("%H")) - int(offset), int(time.strftime("%M")), int(time.strftime("%S")))

def wait(n): # delays n seconds
	if activated == True:
		import time
		time.sleep(n)

def clear(): # clears console
	if activated == True:
		import os
		os.system('clear')

def loser(): # patorjk.com/software/taag
	if activated == True:
		print("""
_____ ___                ____                        
\__  |   | ____  __ __  |    |    ____  ______ ____  
 /   |   |/  _ \|  |  \ |    |   /  _ \/  ___// __ \ 
 \____   (  <_> )  |  / |    |__(  <_> )___\ \  ___/ 
 / ______|\____/|____/  |_______ \____/____ \ \___ |
 \/                             \/         \/     \/ 		""")

def winner(): # patorjk.com/software/taag
	if activated == True:
		print("""
_____ ___                __      __ __        
\__  |   | ____  __ __  /  \    /  \__| ____  
 /   |   |/  _ \|  |  \ \   \/\/   /  |/    \ 
 \____   (  <_> )  |  /  \         |  |   |  |
 / ______|\____/|____/    \__/\  / |__|___|  /
 \/                            \/          \/ 
 		""")

def rgb(r, g, b, text): # Returns RGB Text
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)

def big(string):
	if activated == True:
		from Boi.items import big_letters
		letters = big_letters.All

		for i in string:
			if i == "a": print(letters[ord(i) - 97])
			if i == "b": print(letters[ord(i) - 97])
			if i == "c": print(letters[ord(i) - 97])
			if i == "d": print(letters[ord(i) - 97])
			if i == "e": print(letters[ord(i) - 97])
			if i == "f": print(letters[ord(i) - 97])
			if i == "g": print(letters[ord(i) - 97])
			if i == "h": print(letters[ord(i) - 97])
			if i == "i": print(letters[ord(i) - 97])
			if i == "j": print(letters[ord(i) - 97])
			if i == "k": print(letters[ord(i) - 97])
			if i == "l": print(letters[ord(i) - 97])
			if i == "m": print(letters[ord(i) - 97])
			if i == "n": print(letters[ord(i) - 97])
			if i == "o": print(letters[ord(i) - 97])
			if i == "p": print(letters[ord(i) - 97])
			if i == "q": print(letters[ord(i) - 97])
			if i == "r": print(letters[ord(i) - 97])
			if i == "s": print(letters[ord(i) - 97])
			if i == "t": print(letters[ord(i) - 97])
			if i == "u": print(letters[ord(i) - 97])
			if i == "v": print(letters[ord(i) - 97])
			if i == "w": print(letters[ord(i) - 97])
			if i == "x": print(letters[ord(i) - 97])
			if i == "y": print(letters[ord(i) - 97])
			if i == "z": print(letters[ord(i) - 97])
			if i == " ": print(letters[ord(i) - 97])

		print()