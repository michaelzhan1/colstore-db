#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "hash_table_oa.h"
#include "value_array.h"

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
 * First hash function for double hashing.
 *
 * @param x The input integer to mix.
 * @return The mixed integer.
 */
static size_t hash1(size_t x)
{
    x ^= x >> 33;
    x *= 0xff51afd7ed558ccd;
    x ^= x >> 33;
    x *= 0xc4ceb9fe1a85ec53;
    x ^= x >> 33;
    return x;
}

/**
 * Second hash function for double hashing, must be non-zero and odd.
 *
 * @param x The input integer to mix.
 * @return The mixed integer, guaranteed to be odd and non-zero.
 */
static size_t hash2(size_t x)
{
    x ^= x >> 33;
    x *= 0xff51afd7ed558ccd;
    x ^= x >> 33;
    return (x << 1) | 1; // force odd, never 0
}

HashTable *ht_create(size_t expected_size)
{
    HashTable *ht = malloc(sizeof(*ht));
    if (!ht)
    {
        return NULL;
    }

    // initialize hashtable fields
    ht->capacity = next_power_of_two(expected_size) * 2;
    ht->size = 0;
    ht->arr = calloc(ht->capacity, sizeof(Entry)); // defaults to zero initializations
    if (!ht->arr)
    {
        free(ht);
        return NULL;
    }

    return ht;
}

void ht_free(HashTable *ht)
{
    if (ht)
    {
        if (ht->arr)
        {
            for (size_t i = 0; i < ht->capacity; ++i)
            {
                if (ht->arr[i].state == OCCUPIED)
                {
                    va_free(&ht->arr[i].values);
                }
                ht->arr[i].state = EMPTY;
            }
            free(ht->arr);
        }
        free(ht);
    }
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
