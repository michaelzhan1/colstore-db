#ifndef VALUE_ARRAY_H
#define VALUE_ARRAY_H

#include <stdlib.h>

#include "types.h"

typedef struct ValueArray
{
    val_type *data;
    size_t size;
    size_t capacity;
} ValueArray;

/**
 * Initializes a ValueArray with the given initial capacity. The size of the array is set to 0.
 * 
 * @param arr Pointer to the ValueArray to initialize.
 * @param initial_capacity The initial capacity of the ValueArray.
 */
int va_init(ValueArray *arr, size_t initial_capacity);

/**
 * Frees the memory allocated for the ValueArray. After calling this function, the ValueArray should not be used unless it is re-initialized.
 * 
 * @param arr Pointer to the ValueArray to free.
 */
void va_free(ValueArray *arr);

/**
 * Push a value to the end of the ValueArray.
 * Will resize if necessary. Returns 0 on success and -1 on failure (e.g., if memory allocation fails).
 * 
 * @param array Pointer to the ValueArray to which the value will be added.
 * @param value The value to add to the ValueArray.
 * @return 0 on success, -1 on failure.
 */
int va_push(ValueArray *array, val_type value);

#endif
