#include <stdlib.h>

#include "value_array.h"

int va_init(ValueArray *arr, size_t initial_capacity)
{
    arr->size = 0;
    arr->capacity = initial_capacity;

    if (initial_capacity == 0)
    {
        arr->data = NULL;
    }
    else
    {
        arr->data = malloc(initial_capacity * sizeof(val_type));
        if (arr->data == NULL)
        {
            arr->capacity = 0;
            return -1;
        }
    }
    return 0;
}

void va_free(ValueArray *arr)
{
    if (arr)
    {
        free(arr->data);
        arr->data = NULL;
        arr->size = 0;
        arr->capacity = 0;
    }
}

int va_resize(ValueArray *arr, size_t new_capacity)
{
    if (new_capacity < arr->size)
    {
        return -1;
    }

    // realloc handles freeing of previous memory
    val_type *new_data = realloc(arr->data, new_capacity * sizeof(val_type));
    if (new_data == NULL)
    {
        return -1;
    }
    arr->data = new_data;
    arr->capacity = new_capacity;
    return 0;
}

int va_push(ValueArray *arr, val_type value)
{
    if (arr->size >= arr->capacity)
    {
        size_t new_cap = arr->capacity == 0 ? 4 : arr->capacity * 2;
        if (va_resize(arr, new_cap) != 0)
        {
            return -1;
        }
    }
    arr->data[arr->size++] = value;
    return 0;
}
