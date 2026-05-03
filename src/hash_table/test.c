#include <time.h>
#include <stdlib.h>
#include <stdio.h>
#include <assert.h>

#include "hash_table.h"

// This code is designed to test the correctness of your implementation. 
// You do not need to significantly change it. 
// Compile and run it in the command line by typing: 
// make test; ./test

int main(void) {
  size_t num_tests = 20;

  HashTable *ht = ht_create(20);
  assert(ht != NULL);

  int seed = 1;
  srand(seed);
  key_type keys[num_tests];
  val_type values[num_tests];

  printf("Testing putting and getting from the hash table.\n");
  printf("Inserting %zu key-value pairs.\n", num_tests);
  for (size_t i = 0; i < num_tests; i += 1) {
    keys[i] = rand();
    values[i] = rand();
    int failure = ht_put(ht, keys[i], values[i]);
    assert(!failure);
    printf("\t(%d -> %d) \n", keys[i], values[i]);
  }

  size_t num_values = 1;
  int results[num_values];
  size_t num_results = 0;

  for (size_t i = 0; i < num_tests; i += 1) {
    key_type target_key = keys[i];
    int failure = ht_get(ht, target_key, results, num_values, &num_results);
    assert(!failure);
    if (results[0] != values[i]) {
      printf("Test failed with key %d. Got value %d. Expected value %d.\n", target_key, results[0], values[i]);
      return 1;
    } 
  }

  printf("Passed tests for putting and getting.\n");
  printf("Now testing erasing.\n");

  for (size_t i = 0; i < num_tests; i += 1) {
    key_type target_key = keys[i];
    int failure = ht_delete(ht, target_key);
    assert(!failure);
    failure = ht_get(ht, target_key, results, num_values, &num_results);  
    assert(!failure);
    if (num_results != 0) {
      printf("Test failed with key %d. Expected it to be erased, but got %zu matches.\n", target_key, num_results);
      return 1;
    } 
  }
  int failure = ht_free(ht);
  assert(!failure);
  printf("Passed tests for erasing.\n");
  printf("All tests have been successfully passed.\n");
  return 0;
}
