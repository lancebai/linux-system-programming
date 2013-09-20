//headers
#include <stdio.h>
#include <stdlib.h>
//macro
#define dump_var_addr(x) printf("address of [%28s] is %16p\n", #x, &x)

//global
int global_var = 0;
int global_var_no_init;
static int global_static_var = 0;
static int global_static_var_no_init;

void main()
{
  int local_var = 0;
  static static_local_var = 0;
  void *vptr_heap = malloc(sizeof(int));
  dump_var_addr(local_var);
  dump_var_addr(static_local_var);
  dump_var_addr(global_static_var);
  dump_var_addr(global_var);
  dump_var_addr(main);
  dump_var_addr(global_var_no_init);
  dump_var_addr(global_static_var_no_init);
  dump_var_addr(*vptr_heap); // well, this will cause warnings.

  free(vptr_heap);
}
