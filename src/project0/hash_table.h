#ifndef HASH_TABLE_H
#define HASH_TABLE_H

#include "types.h"

typedef struct HashTable {
// define the components of the hash table here (e.g. the array, bookkeeping for number of elements, etc)
} HashTable;

int allocate(HashTable** ht, int size);
int put(HashTable* ht, key_type key, val_type value);
int get(HashTable* ht, key_type key, val_type *values, int num_values, int* num_results);
int erase(HashTable* ht, key_type key);
int deallocate(HashTable* ht);

#endif
