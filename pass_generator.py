#Yet another simple Password Generator
#not truly random and showing a password in the output, so beware
import random

letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

print("Welcome to the PyPassword Generator!")
nr_letters= int(input("How many letters would you like in your password?\n"))
nr_symbols = int(input(f"How many symbols would you like?\n"))
nr_numbers = int(input(f"How many numbers would you like?\n"))

password = []

for letter_idx in range(nr_letters):
    password.append(random.choice(letters))

for symbol_idx in range(nr_symbols):
    password.append(random.choice(symbols))

for number_idx in range(nr_numbers):
    password.append(random.choice(numbers))

for shuffle_round in range(0, random.randint(0, 1000)):
    random_position = random.randint(0, len(password)-1)
    random_character = password.pop(random_position)
    password.append(random_character)

print(''.join(password))
