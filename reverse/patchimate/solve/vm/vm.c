#include "vm.h"
#include <stdint.h>
#include <string.h>

#define ROR(a, n) (((a) >> (n)) | ((a) << (64 - (n))))
#define ROL(a, n) (((a) << (n)) | ((a) >> (64 - (n))))

uint64_t idx = 31;

uint64_t xorx = 0;

void *get_libc_base() { return &exit - 0x00000000047b90; }

void *get_ld_base() {
  long long libc_base = (long long)get_libc_base();
  long long *ld_leak = (long long *)(libc_base + 0x0000202df0);
  return (void *)(*ld_leak) - 0x37a78;
}

uint64_t get_decoded_xorx() {
  if (xorx != 0)
    return xorx;
  long long *func = (long long *)get_exit_func_entry();
  func += 3;
  uint64_t func_ptr = *func;
  long long dl_fini = (long long)get_ld_base();
  dl_fini += 0x5380;
  uint64_t result = ROR(func_ptr, 0x11);
  xorx = result ^ dl_fini;
  return result ^ dl_fini;
}

exit_function_list *get_exit_func_entry() {
  void *libc_base = get_libc_base();
  return libc_base + 0x204fc0;
}

exit_function_list *alloc_new_function() {
  exit_function_list *new = malloc(sizeof(exit_function_list));
  memset(new, 0, sizeof(exit_function_list));
  return new;
}

void add_to_list(exit_function_list *base, void *addr, void *arg) {
  exit_function_list *curr = base;
  while (curr->next != NULL) {
    curr = curr->next;
  }
  curr->next = alloc_new_function();
  long long new_func = ROL((long long)addr ^ get_decoded_xorx(), 0x11);
  curr->next->fns[0].func.cxa.fn = (void (*)(void *, int))new_func;
  curr->next->fns[0].flavor = ef_cxa;
  curr->next->fns[0].func.cxa.arg = arg;
}

void overwrite_entry(exit_function_list *entry, void *addr, void *arg) {
  long long new_func =
      ROL(((long long)addr + 0x200100) ^ get_decoded_xorx(), 0x11);
  entry->fns[idx].func.cxa.fn = (void (*)(void *, int))new_func;
  entry->fns[idx].flavor = ef_cxa;
  entry->fns[idx].func.cxa.arg = arg;

  if (idx == 31)
    entry->idx = idx + 1;
  idx--;
}
