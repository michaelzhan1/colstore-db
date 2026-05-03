#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>

#include "hash_table.h"

int main(void)
{
  size_t num_tests = 50000000; // 50,000,000

  HashTable *ht = ht_create(num_tests);
  assert(ht != NULL);

  int seed = 2;
  srand(seed);
  printf("Performing stress test. Inserting %zu keys.\n", num_tests);

  struct timeval stop, start;
  gettimeofday(&start, NULL);

  for (size_t i = 0; i < num_tests; i++)
  {
    int key = rand();
    int val = rand();
    int failure = ht_put(ht, key, val);
    assert(!failure);
  }

  gettimeofday(&stop, NULL);
  double secs = (double)(stop.tv_usec - start.tv_usec) / 1000000 + (double)(stop.tv_sec - start.tv_sec);
  printf("%zu insertions took %f seconds\n", num_tests, secs);

  int failure = ht_free(ht);
  assert(!failure);

  return 0;
}
