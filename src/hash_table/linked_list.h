#ifndef LINKED_LIST_H
#define LINKED_LIST_H

#include "types.h"

typedef struct LinkedList
{
    key_type key;
    key_type value;
    struct LinkedList *next;
} LinkedList;

#endif