#include <iostream>
#include <cstdint>
#include <string>
#include <cstdlib>

uint64_t ror(uint64_t value, unsigned int shift) {
    shift %= 64;
    return (value >> shift) | (value << (64 - shift));
}

int main(int argc, char **argv) {
    std::string input;
    
    if (argc > 1) {
        input = argv[1];
    } else {
        std::cout << "Enter a 40-character string: ";
        std::getline(std::cin, input);
    }
    
    if (input.size() != 40) {
        std::cerr << "Error: The string must be exactly 40 characters long (provided: " 
                  << input.size() << " characters)." << std::endl;
        return EXIT_FAILURE;
    }
    
    uint64_t check[40];
    
    check[0] = ror(((0xddull ^ static_cast<uint64_t>(input[0])) + 1337ull), 4);
    
    for (int i = 1; i < 40; i++) {
        check[i] = ror(((0xddull ^ static_cast<uint64_t>(input[i])) + 1337ull), 4)
                   - (static_cast<uint64_t>(input[i - 1]) & 0x07ull);
    }
    
    std::cout << "uint64_t check[40] = {" << std::endl;
    for (int i = 0; i < 40; i++) {
        std::cout << "    " << check[i];
        if (i != 39)
            std::cout << ",";
        std::cout << std::endl;
    }
    std::cout << "};" << std::endl;
    
    return EXIT_SUCCESS;
}
