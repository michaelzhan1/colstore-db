#include <stdlib.h>
#include <stdio.h>

#include "hash_table.h"

int main(void)
{
  HashTable *ht = ht_create(10);

  int key = 0;
  int value = -1;
  ht_put(ht, key, value);

  size_t num_values = 1;
  val_type *values = malloc(sizeof(*values));
  size_t num_results = 0;
  ht_get(ht, key, values, num_values, &num_results);
  if (num_results > num_values)
  {
    values = realloc(values, num_results * sizeof(val_type));
    ht_get(ht, key, values, num_values, &num_results);
  }

  for (size_t i = 0; i < num_results; i++)
  {
    printf("value %zu is %d \n", i, values[i]);
  }
  free(values);

  ht_delete(ht, 0);
  ht_free(ht);
  return 0;
}
