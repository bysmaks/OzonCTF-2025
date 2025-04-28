#include "./vm/vm.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void *table[100] = {0};
char buffer[500] = {0};

void gadjet(void *buffer);

void set_table(void *libc) {
  table[0] = libc + 0x00000000086f70 - 0x200000;   // gets
  table[1] = libc + 0x000000000b3090 - 0x200000;   // strcmp
  table[2] = libc + 0x00000000087ad0 - 0x200000;   // puts
  table[3] = libc + 0x0000000000183302 - 0x200000; // ror 0x95
  table[4] = libc + 0x0000000000181e34 - 0x200000; // ror 0x89
  table[5] = libc + 0x000000000015dbf3 - 0x200000; // ror 0x85
  table[6] = libc + 0x000000000003abe0 - 0x200000; // ror 0x84
  table[7] = libc + 0x000000000011c006 - 0x200000; // ror 0x88
  table[8] = libc + 0x000000000010f89b - 0x200000; // ror 0x8e
  table[9] = &gadjet - 0x200100;
}

void gadjet(void *buffer) {
  int res = strcmp(buffer, buffer + 0x50);
  if (res == 0)
    puts(buffer + 0x100);
  else
    puts(buffer + 0x150);
};

int main() {
  unsigned char flag[] = {58,  167, 129, 3,   48,  196, 250, 188,
                          129, 87,  95,  141, 161, 55,  250, 39,
                          51,  217, 153, 57,  169, 51,  0};
  void *libc = get_libc_base();
  memcpy(buffer + 0x50, flag, strlen(flag));
  memcpy(buffer + 0x100, "Correct flag u win", strlen("Correct flag u win"));
  memcpy(buffer + 0x150, "Ha-ha u loooose", strlen("Ha-ha u loooose"));
  set_table(libc);
  uint64_t xorx = get_decoded_xorx();
  exit_function_list *entry = get_exit_func_entry();
  overwrite_entry(entry, table[0], buffer);
  for (int i = 0; i < strlen(flag); i++) {
    overwrite_entry(entry, table[3 + i % 6], buffer + i);
  }
  overwrite_entry(entry, table[9], buffer);
  exit(5);
}
