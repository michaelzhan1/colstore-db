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

  HashTable* ht=NULL;
  int num_tests = 20;
  int failure = ht_init(&ht, num_tests);
  assert(!failure);

  int seed = 1;
  srand(seed);
  key_type keys[num_tests];
  val_type values[num_tests];

  printf("Testing putting and getting from the hash table.\n");
  printf("Inserting %d key-value pairs.\n", num_tests);
  for (int i = 0; i < num_tests; i += 1) {
    keys[i] = rand();
    values[i] = rand();
    failure = put(ht, keys[i], values[i]);
    assert(!failure);
    printf("\t(%d -> %d) \n", keys[i], values[i]);
  }

  int num_values = 1;
  int results[num_values];
  int num_results = 0;

  for (int i = 0; i < num_tests; i += 1) {
    key_type target_key = keys[i];
    failure = get(ht, target_key, results, num_values, &num_results);
    assert(!failure);
    if (results[0] != values[i]) {
      printf("Test failed with key %d. Got value %d. Expected value %d.\n", target_key, results[0], values[i]);
      return 1;
    } 
  }

  printf("Passed tests for putting and getting.\n");
  printf("Now testing erasing.\n");

  for (int i = 0; i < num_tests; i += 1) {
    key_type target_key = keys[i];
    failure = ht_delete(ht, target_key);
    assert(!failure);
    failure = get(ht, target_key, results, num_values, &num_results);  
    assert(!failure);
    if (num_results != 0) {
      printf("Test failed with key %d. Expected it to be erased, but got %d matches.\n", target_key, num_results);
      return 1;
    } 
  }
  failure = ht_free(ht);
  assert(!failure);
  printf("Passed tests for erasing.\n");
  printf("All tests have been successfully passed.\n");
  return 0;
}
