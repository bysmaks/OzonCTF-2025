import vibe.vibe;
import std.stdio;

interface Prilozheniye123 {
	@path("/encrypt")
    @method(HTTPMethod.POST)
    string enc(string data);

	@path("/decrypt")
	@method(HTTPMethod.POST)
	string dec(string data);
}

class ConcretnoyePrilozheniye: Prilozheniye123 {
	private ubyte[256] sbox;
	private ubyte[16]  pbox;
	private ubyte[16]  key;
	private ubyte[16]  iv;

	this(ubyte[256] sbox, ubyte[16] pbox, ubyte[16] key, ubyte[16] iv) {
		this.sbox = sbox;
		this.pbox = pbox;
		this.key = key;
		this.iv = iv;
	}

	@safe private void inplace_shift(ref ubyte[16] input) {
		auto temp = input.dup;
		foreach (i; 0..16) {
			input[i] = temp[pbox[i]];
		}
	}

	@safe private void inplace_add_key(ref ubyte[16] input) {
		input[] ^= key[];
	}

	@safe private static ubyte circular_shift(ubyte x) {
		ubyte res;
		asm @trusted @nogc {
			mov AL, x;
			ror AL, 3;
			mov res, AL;
		}
		return res;
	}

	@safe private void inplace_shift_bits(ref ubyte[16] input) {
		foreach (i; 0..16) {
			input[i] = circular_shift(input[i]);
		}
	}

	@safe private void inplace_substitute(ref ubyte[16] input) {
		foreach (i; 0..16) {
			input[i] = sbox[input[i]];
		}
	}

	@safe private ubyte[16] block(ubyte[16] text) {
		ubyte[16] data = text.dup;
		foreach (i; 0..9) {
			inplace_shift(data);
			inplace_add_key(data);
			inplace_shift_bits(data);
			inplace_substitute(data);
		}
		return data;
	}

	@safe private ubyte[] encrypt(ubyte[] text) {
		import std.range : chunks;
		ubyte[] res = [];
		ubyte[16] travel = iv;
		foreach(ubyte[16] pblock; text.chunks(16)) {
			travel[] ^= pblock[];
			travel = block(travel);
			res ~= travel;
		}
		return res;
	}

	@safe string enc(string data) {
		import std.base64 : Base64;

		if(data.length % 16) {
			return "Iнвалiд длина строки :(";
		}
		
		char[] input = data.dup;
		ubyte[] plaintext = cast (ubyte[]) input;
		ubyte[] ciphertext = encrypt(plaintext);
		char[] enc = Base64.encode(ciphertext);
		return enc.idup;
	}

	@safe string dec(string data) {
		return "Простите, эта часть приложения еще не готова :(";
	}

	unittest {
		auto res = circular_shift(0b10101010);
		assert(res == 0b01010101);
	}
}

void main() {
	import std.range : take, repeat, iota;
	import std.array : array;
	import std.algorithm: map;

	ubyte[16] key = [141, 165, 7, 117, 32, 22, 56, 68, 108, 129, 14, 161, 87, 248, 27, 12];
	ubyte[256] sbox = 
		[5, 125, 71, 189, 67, 210, 212, 37, 185, 0, 80, 49, 227, 
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
		 8, 247, 102, 218, 140, 23, 192, 169, 201];
	ubyte[16] pbox = [3, 5, 0, 6, 9, 4, 11, 1, 12, 10, 14, 8, 2, 13, 7, 15];
	ubyte[16] iv = [140, 112, 141, 224, 143, 177, 188, 255, 186, 159, 220, 151, 176, 86, 52, 179];

    auto router = new URLRouter;
    router.registerRestInterface(new ConcretnoyePrilozheniye(sbox, pbox, key, iv));
	router.get("/", staticTemplate!"interface.dt");
	router.get("*", serveStaticFiles("public/"));

    auto settings = new HTTPServerSettings;
    settings.port = 8080;
	settings.bindAddresses = ["127.0.0.1", "0.0.0.0"];

    auto listener = listenHTTP(settings, router);
	scope (exit) { listener.stopListening(); }

	runApplication();
}
