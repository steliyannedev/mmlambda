

import string
import random

letters = string.ascii_letters
filename = ''.join(random.choice(letters) for i in range(15))

print(filename)