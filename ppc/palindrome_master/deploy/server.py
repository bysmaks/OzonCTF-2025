import random
import string


def is_palindrome(word):
    return word == word[::-1]


def is_sublist(words, response):
    words = sorted(words)
    response = sorted(response)

    len_response = len(response)
    if len_response == 0:
        return True
    if len_response > len(words):
        return False

    response_tuple = tuple(response)
    
    for i in range(len(words) - len_response + 1):
        if tuple(words[i:i+len_response]) == response_tuple:
            return True
    return False


def generate(size):
    chars = random.sample(string.ascii_lowercase, 26)
    pal = ''.join(random.choices(chars, k=random.randint(5, 200)))
    pal += pal[::-1]

    k = random.randint(3, size)
    split_points = sorted(random.sample(range(1, len(pal)), k-1))
    indices = [0] + split_points + [len(pal)]
    sliced_pal = [pal[indices[i]:indices[i+1]] for i in range(k)]

    random.shuffle(sliced_pal)
    return sliced_pal


def run_challenge():
    print("Welcome to the Palindrome Challenge!")
    print("You need to make a palindrome using some words from given.")
    print("Type the words separated by spaces. There is 200 rounds.")
    print("So smth like: word1 word3 word2, where concat of these words are palindrome.\n")

    rounds = 200
    min_words = 5
    max_words = 15
    step = 1

    for round_num in range(1, rounds + 1):
        num_words = min(min_words + step * (round_num // 25), max_words)
        words = generate(num_words)

        print(f"Round {round_num}:")
        print(' '.join(words))
        response = input("Your answer: ").strip()

        try:
            response_list = response.split(' ')

            if not is_sublist(words, response_list):
                print("Incorrect. Challenge terminated1.")
                return

            response_str = ''.join(response_list)

            if not is_palindrome(response_str):
                print("Incorrect. Challenge terminated.")
                return
            
            print("Correct!\n")
        except Exception as e:
            print("An error occurred. Challenge terminated3.")
            return

    print("Congratulations! You've completed all rounds.")
    print("Here is your flag: ozonctf{4_15_7h3_b357_3n6l15h_p4l1ndr0m3}")
