#ifndef HASH_TABLE_H
#define HASH_TABLE_H

#include <stdlib.h>

#include "list_node.h"
#include "types.h"

typedef struct HashTable
{
    ListNode **buckets;
    size_t capacity;
    size_t size;

    size_t a;
    size_t b;
} HashTable;

/**
 * Create a new hash table with given initial size (number of buckets).
 * Returns a pointer to the new hash table, or NULL on failure.
 * 
 * Hash table capacity will be a power of two larger than the expected size.
 * 
 * @param expected_size The estimate of number of entries in the hashtable.
 * @return A pointer to the newly created hash table, or NULL if creation fails.
 */
HashTable *ht_create(size_t expected_size);

/**
 * Inserts a new key-value pair into the hash table.
 * If the key exists, the value is added to the list of values for the key.
 * Resizes the hash table if the load factor exceeds 0.75.
 * 
 * @param ht The hash table to insert into.
 * @param key The key to insert.
 * @param value The value to associate with the key.
 * @return 0 on success, -1 on failure
 */
int ht_insert(HashTable *ht, key_type key, val_type value);

/**
 * Retrieves values associated with a given key from the hash table.
 * Copies up to num_values values into the provided values array.
 * Sets num_results to the total number of values associated with the key.
 * 
 * @param ht The hash table to query.
 * @param key The key to look up.
 * @param values The array to copy results into.
 * @param num_values The maximum number of values to copy into the values array.
 * @param num_results Output parameter to store the total number of values associated with the key.
 * @return 0 on success, -1 on failure
 */
int ht_get(HashTable *ht, key_type key, val_type *values, size_t num_values, size_t *num_results);

/**
 * Deletes all key-value pairs with the given key from the hash table.
 * Returns 0 on success, -1 if the hash table pointer is NULL.
 * 
 * @param ht The hash table to delete from.
 * @param key The key to delete.
 * @return 0 on success, -1 if ht is NULL
 */
int ht_delete(HashTable *ht, key_type key);

/**
 * Frees all memory occupied by the hash table.
 * Returns 0 on success, -1 if the hash table pointer is NULL.
 * 
 * @param ht The hash table to free.
 * @return 0 on success, -1 if ht is NULL
 */
int ht_free(HashTable *ht);

/**
 * Resizes the hash table to a new capacity.
 * The new capacity will be adjusted to the next power of two.
 * Returns 0 on success, -1 on failure (e.g., if ht is NULL or new_capacity is 0).
 * 
 * @param ht The hash table to resize.
 * @param new_capacity The desired new capacity (number of buckets) for the hash table.
 * @return 0 on success, -1 on failure
 */
int ht_resize(HashTable *ht, size_t new_capacity);

#endif
