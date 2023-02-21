import random

def get_random_code(code_len):
    return random.randint(10**(code_len - 1), 10**code_len-1)