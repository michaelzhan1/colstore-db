#include <stdio.h>
#include <stdlib.h>

#include "hash_table.h"

int main(void)
{
  HashTable *ht = ht_create(10);

  ht_put(ht, 0, -1);
  ht_put(ht, 0, -2);

  size_t num_values = 1;
  val_type *values = malloc(sizeof(*values));
  size_t num_results = 0;
  ht_get(ht, 0, values, num_values, &num_results);
  if (num_results > num_values)
  {
    values = realloc(values, num_results * sizeof(val_type));
    ht_get(ht, 0, values, num_results, &num_results);
  }

  for (size_t i = 0; i < num_results; i++)
  {
    printf("value %zu is %d \n", i, values[i]);
  }
  
  ht_delete(ht, 0);
  ht_get(ht, 0, values, num_values, &num_results);
  printf("num_results is %zu \n", num_results);
  
  free(values);
  ht_free(ht);
  return 0;
}
