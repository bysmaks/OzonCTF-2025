#include <iostream>
#include <cstdint>
#include <cstdlib>
#include <string>

uint64_t ror(uint64_t value, unsigned int shift) {
    shift %= 64;
    return (value >> shift) | (value << (64 - shift));
}

uint64_t rol(uint64_t value, unsigned int shift) {
    shift %= 64;
    return (value << shift) | (value >> (64 - shift));
}

int main() {
    uint64_t check[40] = {
        12682136550675316830ull,
        87ull,
        12682136550675316828ull,
        13835058055282163799ull,
        8070450532247928921ull,
        2305843009213694043ull,
        4611686018427387995ull,
        17293822569102704727ull,
        13835058055282163803ull,
        2305843009213694041ull,
        8070450532247928922ull,
        14987979559889010779ull,
        3458764513820541022ull,
        14987979559889010778ull,
        16140901064495857760ull,
        8070450532247928930ull,
        5764607523034234975ull,
        13835058055282163805ull,
        89ull,
        8070450532247928924ull,
        5764607523034234972ull,
        2305843009213694046ull,
        11529215046068469850ull,
        91ull,
        2305843009213694044ull,
        3458764513820541019ull,
        16140901064495857754ull,
        14987979559889010785ull,
        8070450532247928929ull,
        2305843009213694047ull,
        8070450532247928922ull,
        10376293541461622875ull,
        2305843009213694042ull,
        5764607523034234971ull,
        17293822569102704733ull,
        11529215046068469851ull,
        5764607523034234971ull,
        8070450532247928925ull,
        2305843009213694044ull,
        10376293541461622873ull
    };

    std::string recovered;
    recovered.resize(40);
    
    char firstChar;
    std::cout << "Enter the first character of the string: ";
    std::cin >> firstChar;
    
    uint64_t computed0 = ror(((0xddull ^ static_cast<uint64_t>(firstChar)) + 1337ull), 4);
    if (computed0 != check[0]) {
        std::cerr << "The provided first character does not match the expected encryption." << std::endl;
        return EXIT_FAILURE;
    }
    recovered[0] = firstChar;
    
    for (int i = 1; i < 40; i++) {
        uint64_t A = check[i] + (static_cast<uint64_t>(recovered[i-1]) & 0x07ull);
        uint64_t temp = rol(A, 4) - 1337ull;
        char ch = static_cast<char>(0xddull ^ temp);
        recovered[i] = ch;
    }
    
    std::cout << "Recovered string: " << recovered << std::endl;
    return EXIT_SUCCESS;
}
