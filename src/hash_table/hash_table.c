#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "hash_table.h"
#include "list_node.h"

/**
 * Returns the next power of two greater than or equal to x.
 * If x is already a power of two, it returns x.
 * If x is 0, it returns 1.
 *
 * @param x The input number.
 * @return The next power of two greater than or equal to x.
 */
static size_t next_power_of_two(size_t x)
{
    size_t p = 1;
    while (p < x)
        p <<= 1;
    return p;
}

/**
 * A simple mix function for hashing integers, based on MurmurHash3's finalizer.
 * This helps to ensure that keys that are close together (e.g., sequential integers) are well-distributed across the hash table.
 *
 * @param x The input integer to mix.
 * @return The mixed integer.
 */
static size_t hash_mix(size_t x)
{
    x ^= x >> 33;
    x *= 0xff51afd7ed558ccd;
    x ^= x >> 33;
    x *= 0xc4ceb9fe1a85ec53;
    x ^= x >> 33;
    return x;
}

/**
 * Computes the hash of a key for the given hash table, using the universal hashing scheme.
 *
 * @param ht The hash table for which to compute the hash.
 * @param key The key to hash.
 * @return The hash value for the key, which is an index into the hash table's
 */
size_t hash_key(HashTable *ht, key_type key)
{
    size_t x = (size_t)key; // safe
    x = hash_mix(x);
    size_t h = ht->a * x + ht->b;
    return h & (ht->capacity - 1); // capacity is a power of two, so this is fast mod
}

HashTable *ht_create(size_t expected_size)
{
    HashTable *ht = malloc(sizeof(*ht));
    if (!ht)
    {
        return NULL;
    }

    ht->capacity = next_power_of_two(expected_size) * 2;
    ht->size = 0;

    ht->buckets = calloc(ht->capacity, sizeof(ListNode *));
    if (!ht->buckets)
    {
        free(ht);
        return NULL;
    }

    srand((unsigned)time(NULL));
    ht->a = ((size_t)rand() << 32) ^ rand();
    ht->b = ((size_t)rand() << 32) ^ rand();

    return ht;
}

int ht_insert(HashTable *ht, key_type key, val_type value)
{
    if (!ht)
    {
        return -1;
    }

    if ((double)(ht->size + 1) / (double)ht->capacity > 0.75)
    {
        if (ht_resize(ht, ht->capacity * 2) != 0)
        {
            return -1;
        }
    }

    size_t h = hash_key(ht, key);
    ListNode *node = list_find(ht->buckets[h], key);
    if (node)
    {
        if (va_push(&node->values, value) != 0)
        {
            return -1;
        }
        return 0;
    }

    if (list_insert(&ht->buckets[h], key, value) != 0)
    {
        return -1;
    }
    ht->size++;
    return 0;
}

int ht_get(HashTable *ht, key_type key, val_type *values, size_t num_values, size_t *num_results)
{
    if (!ht || !values || !num_results)
    {
        return -1;
    }
    size_t h = hash_key(ht, key);
    ListNode *node = list_find(ht->buckets[h], key);
    if (node == NULL)
    {
        *num_results = 0;
        return 0;
    }

    size_t total_results = node->values.size;
    size_t copied_results = total_results;
    if (num_values < copied_results)
    {
        copied_results = num_values;
    }

    if (copied_results > 0)
    {
        memcpy(values, node->values.data, sizeof(val_type) * copied_results);
    }

    *num_results = total_results;
    return 0;
}

int ht_delete(HashTable *ht, key_type key)
{
    if (!ht)
    {
        return -1;
    }

    size_t h = hash_key(ht, key);
    if (list_delete(&ht->buckets[h], key) == 0)
    {
        ht->size--;
    }
    return 0;
}

// TODO: make void
int ht_free(HashTable *ht)
{
    if (!ht)
    {
        return -1;
    }

    if (ht->buckets)
    {
        for (size_t i = 0; i < ht->capacity; ++i)
        {
            list_free(ht->buckets[i]);
        }
        free(ht->buckets);
        ht->buckets = NULL;
    }
    free(ht);
    return 0;
}

int ht_resize(HashTable *ht, size_t new_capacity)
{
    if (ht == NULL || new_capacity == 0)
    {
        return -1;
    }

    /* ensure power of two */
    new_capacity = next_power_of_two(new_capacity);

    ListNode **new_buckets = calloc(new_capacity, sizeof(ListNode *));
    if (!new_buckets)
    {
        return -1;
    }

    size_t old_capacity = ht->capacity;
    ListNode **old_buckets = ht->buckets;

    /* switch to new buckets and capacity so hash_key uses new modulus */
    ht->buckets = new_buckets;
    ht->capacity = new_capacity;

    for (size_t i = 0; i < old_capacity; ++i)
    {
        ListNode *node = old_buckets[i];
        while (node != NULL)
        {
            ListNode *next = node->next;
            size_t h = hash_key(ht, node->key);
            node->next = ht->buckets[h];
            ht->buckets[h] = node;
            node = next;
        }
    }

    free(old_buckets);
    return 0;
}
