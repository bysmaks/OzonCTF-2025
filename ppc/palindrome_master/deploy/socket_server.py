import threading
import socket
import random
import string
import math


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

    # blob = []
    # blob.append(*sliced_pal)
    random.shuffle(sliced_pal)
    return sliced_pal


def handle_client(conn, addr):
    conn.sendall(b"Welcome to the Palindrome Challenge!\n")
    conn.sendall(b"You need to make a palindrome using some words from given.\n")
    conn.sendall(b"Type the words separated by spaces. There is 200 rounds.\n")
    conn.sendall(b"So smth like: word1 word3 word2, where concat of these words are palindrome.\n\n")

    rounds = 200
    min_words = 5
    max_words = 15
    step = 1

    for round_num in range(1, rounds + 1):
        num_words = min_words + step * (round_num // 25)
        words = generate(num_words)

        conn.sendall(f"Round {round_num}:\n".encode())
        conn.sendall(f"{' '.join(words)}\n".encode())
        conn.sendall(b"Your answer: ")

        try:
            data = conn.recv(4096)
            if not data:
                break

            response = data.decode().strip()

            try:
                response = response.split(' ')

                if not is_sublist(words, response):
                    conn.sendall(b"Incorrect. Challenge terminated1.\n")
                    conn.close()
                    return

                response = ''.join(response)
            except Exception:
                if not is_sublist(words, response):
                    conn.sendall(b"Incorrect. Challenge terminated2.\n")
                    conn.close()
                    return

                pass

            if response != response[::-1]:
                conn.sendall(b"Incorrect. Challenge terminated.\n")
                conn.close()
                return
            else:
                conn.sendall(b"Correct!\n\n")
        except Exception as e:
            conn.sendall(b"An error occurred. Challenge terminated3.\n")
            conn.close()
            return

    conn.sendall(b"Congratulations! You've completed all rounds.\n")
    conn.sendall(b"Here is your flag: ozonctf{4_15_7h3_b357_3n6l15h_p4l1ndr0m3}\n")
    conn.close()


def start_server(host='0.0.0.0', port=5000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Server listening on {host}:{port}")

    try:
        while True:
            conn, addr = server.accept()
            print(f"Connection from {addr}")
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
        server.close()


if __name__ == "__main__":
    start_server()
