#include <iostream>
#include <cstdint>
#include <cstdlib>
#include <string>

uint64_t ror(uint64_t value, unsigned int shift) {
    shift %= 64;
    return (value >> shift) | (value << (64 - shift));
}

int main() {
    std::string input;
    std::cout << "Enter a 40-character string: ";
    std::getline(std::cin, input);
    
    if (input.size() != 40) {
        std::cerr << "Error: The string must be exactly 40 characters long (provided: "
                  << input.size() << " characters)." << std::endl;
        return EXIT_FAILURE;
    }
    
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
    
    
    uint64_t computed[40];
    computed[0] = ror(((0xddull ^ static_cast<uint64_t>(input[0])) + 1337ull), 4);
    
    if (computed[0] != check[0]) {
        std::cerr << "Encryption check failed at position 0." << std::endl;
        return EXIT_FAILURE;
    }
    
    for (int i = 1; i < 40; i++) {
        computed[i] = ror(((0xddull ^ static_cast<uint64_t>(input[i])) + 1337ull), 4)
                      - (static_cast<uint64_t>(input[i - 1]) & 0x07ull);
        if (computed[i] != check[i]) {
            std::cerr << "Encryption check failed." << std::endl;
            return EXIT_FAILURE;
        }
    }
    
    std::cout << "Encryption check passed!" << std::endl;
    return EXIT_SUCCESS;
}
