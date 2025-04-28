#!/usr/bin/python3

rol = lambda val, r_bits, max_bits: (val << r_bits % max_bits) & (2**max_bits - 1) | (
    (val & (2**max_bits - 1)) >> (max_bits - (r_bits % max_bits))
)

# Rotate right: 0b1001 --> 0b1100
ror = lambda val, r_bits, max_bits: ((val & (2**max_bits - 1)) >> r_bits % max_bits) | (
    val << (max_bits - (r_bits % max_bits)) & (2**max_bits - 1)
)


flag = b"GO0001_y0u_c4n_r3v3r53"

nums = [0x95, 0x89, 0x85, 0x84, 0x88, 0x8E]

encoded = b""
decoded = b""

for i, k in zip(flag, range(len(flag))):
    encoded += ror(i, nums[k % len(nums)], 8).to_bytes(1, "big")

print(encoded)
for i, k in zip(encoded, range(len(flag))):
    decoded += rol(i, nums[k % len(nums)], 8).to_bytes(1, "big")

strx = "{"

for i in encoded:
    strx += str(i) + ","

print(strx + "}")
print(len(encoded))
print(len(flag))

print(decoded)
