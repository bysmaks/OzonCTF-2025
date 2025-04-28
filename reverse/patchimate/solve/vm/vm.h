#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

enum
{
  ef_free, /* `ef_free' MUST be zero!  */
  ef_us,
  ef_on,
  ef_at,
  ef_cxa
};

struct exit_function {
    /* `flavour' should be of type of the `enum' above but since we need
       this element in an atomic operation we have to use `long int'.  */
  long int flavor;
  union 
  {
    void (*at) (void);
    struct {
      void (*fn) (int status, void *arg);
      void *arg;
    } on;
    struct {
      void (*fn) (void *arg, int status);
      void *arg;
      void *dso_handle;
  }    cxa;

  } func;
};

typedef struct exit_function_list {
    struct exit_function_list *next;
    size_t idx;
    struct exit_function fns[32];
} exit_function_list;

void* get_libc_base();

void* get_ld_base();

exit_function_list * get_exit_func_entry();

uint64_t get_decoded_xorx();


exit_function_list* alloc_new_function();

void add_to_list(exit_function_list* list,void* addr,void* arg);

void overwrite_entry(exit_function_list* entry,void* addr,void* arg);
