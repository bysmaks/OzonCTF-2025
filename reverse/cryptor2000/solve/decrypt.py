from base64 import b64decode
from itertools import batched

KEY = [141, 165, 7, 117, 32, 22, 56, 68, 108, 129, 14, 161, 87, 248, 27, 12]
IV = [140, 112, 141, 224, 143, 177, 188, 255, 186, 159, 220, 151, 176, 86, 52, 179]

PBOX = [3, 5, 0, 6, 9, 4, 11, 1, 12, 10, 14, 8, 2, 13, 7, 15]
SBOX = [5, 125, 71, 189, 67, 210, 212, 37, 185, 0, 80, 49, 227, 
	     29, 61, 112, 134, 168, 251, 11, 237, 99, 38, 41, 1, 145, 
		 28, 98, 97, 115, 92, 240, 160, 22, 228, 209, 60, 135, 2, 
		 83, 173, 175, 18, 36, 40, 74, 141, 121, 136, 200, 25, 129, 
		 77, 171, 105, 188, 244, 199, 231, 248, 130, 122, 24, 245, 
		 91, 152, 197, 52, 104, 253, 118, 234, 178, 167, 90, 154, 
		 32, 139, 255, 147, 208, 6, 159, 93, 131, 172, 117, 249, 
		 181, 182, 196, 109, 17, 137, 150, 223, 101, 241, 162, 12, 
		 198, 58, 86, 204, 116, 214, 33, 44, 242, 127, 76, 94, 65, 
		 151, 224, 120, 64, 190, 221, 203, 110, 233, 220, 230, 217, 
		 69, 34, 50, 193, 156, 70, 26, 85, 155, 75, 15, 100, 95, 68, 
		 79, 163, 84, 206, 78, 114, 186, 164, 39, 96, 16, 106, 144, 
		 161, 143, 222, 88, 142, 20, 53, 128, 19, 146, 225, 103, 59, 
		 177, 243, 215, 239, 10, 54, 202, 232, 7, 119, 254, 51, 174, 
		 133, 14, 107, 184, 207, 132, 226, 42, 187, 149, 252, 27, 179, 
		 46, 48, 9, 170, 87, 108, 250, 35, 236, 55, 165, 148, 21, 56, 
		 211, 4, 219, 81, 111, 30, 191, 205, 113, 62, 158, 66, 31, 229, 
		 47, 238, 73, 138, 166, 213, 180, 72, 183, 153, 157, 43, 57, 82, 
		 89, 45, 176, 123, 126, 246, 13, 216, 3, 124, 194, 195, 63, 235, 
		 8, 247, 102, 218, 140, 23, 192, 169, 201]
INV_SBOX = [0 for i in SBOX]
for i,v in enumerate(SBOX):
    INV_SBOX[v] = i

PBOX = [3, 5, 0, 6, 9, 4, 11, 1, 12, 10, 14, 8, 2, 13, 7, 15]
INV_PBOX = [PBOX.index(i) for i in range(16)]

ct = "xiR1TOdQ07nZnhQ+P3RI76lxsQTBlcQA3JjobfV3WbE="
ct = b64decode(ct)

def unshift_bits(ct):
    res = b''
    for i in ct:
        res += bytes([
            ((i << 3) & 0xFF) | ((i >> 5) & 0xFF)
        ])
    return res

def substract_key(ct):
    res = b''
    for i,k in zip(ct, KEY):
        res += bytes([i ^ k])
    return res

def unpbox(ct):
    return bytes([
        ct[INV_PBOX[i]] for i in range(16)
    ])

def unsbox(ct):
    return bytes([
        INV_SBOX[i] for i in ct
    ])

def unblock(block):
    for _ in range(9):
        block = unsbox(block)
        block = unshift_bits(block)
        block = substract_key(block)
        block = unpbox(block)
    return block

def decrypt(ct):
    res = b''
    travel = bytes(IV)
    for block_tuple in batched(ct, 16):
        block = bytes(block_tuple)
        res += bytes([p ^ i for p,i in zip(unblock(block), travel)])
        travel = block
    return res

print(decrypt(ct))
