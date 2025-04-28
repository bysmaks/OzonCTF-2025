from pwn import *
import itertools
from tqdm import tqdm


def solve_challenge(host='127.0.0.1', port=5000):
    conn = remote(host, port)

    print(conn.recvuntil(b'Round').decode())

    for round_num in range(200):
        response = conn.recvuntil(b'Your answer:').decode()
        print(response)

        idx = response.find(":")
        if idx == -1:
            log.error("Could not find 'Round' in response!")
            exit(0)

        lines = response[idx:].split('\n')

        need = lines[1].split()
        print(need)

        def makepal(words):
            for var in tqdm(itertools.permutations(words, len(words))):
                str1 = ''.join(var)
                if str1 == str1[::-1]:
                    print(*var)
                    return var
            else:
                log.error("No palindrome found!")
                exit(0)

        answer = ' '.join(makepal(need))
        print(f"sending: {answer}")
        conn.sendline(answer)

    final_response = conn.recvall().decode()
    print(final_response)

    conn.close()


if __name__ == "__main__":
    solve_challenge()
