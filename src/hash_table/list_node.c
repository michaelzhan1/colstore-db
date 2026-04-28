#include <stdlib.h>

#include "list_node.h"

ListNode *listnode_create(key_type key, key_type value)
{
    ListNode *node = malloc(sizeof(*node));
    if (node == NULL)
    {
        return NULL;
    }
    node->key = key;
    node->next = NULL;

    if (va_init(&node->values, 0) != 0)
    {
        free(node);
        return NULL;
    }
    if (va_push(&node->values, value) != 0)
    {
        va_free(&node->values);
        free(node);
        return NULL;
    }

    return node;
}

void listnode_free(ListNode *node)
{
    if (node) {
        va_free(&node->values);
        free(node);
    }
}

void list_free(ListNode *head)
{
    ListNode *curr = head;
    while (curr != NULL)
    {
        ListNode *next = curr->next;
        listnode_free(curr);
        curr = next;
    }
}

int list_insert(ListNode **head, key_type key, key_type value)
{
    ListNode *curr = *head;
    while (curr != NULL)
    {
        if (curr->key == key)
        {
            if (va_push(&curr->values, value) != 0)
            {
                return -1;
            }
            return 0;
        }
        curr = curr->next;
    }
    ListNode *new_node = listnode_create(key, value);
    if (new_node == NULL)
    {
        return -1;
    }
    new_node->next = *head;
    *head = new_node;
    return 0;
}

int list_delete(ListNode **head, key_type key)
{
    ListNode *curr = *head;
    ListNode *prev = NULL;
    while (curr != NULL)
    {
        if (curr->key == key)
        {
            if (prev == NULL)
            {
                *head = curr->next;
            }
            else
            {
                prev->next = curr->next;
            }
            listnode_free(curr);
            return 0;
        }
        prev = curr;
        curr = curr->next;
    }
    return -1;
}

ListNode *list_find(ListNode *head, key_type key)
{
    ListNode *curr = head;
    while (curr != NULL)
    {
        if (curr->key == key)
        {
            return curr;
        }
        curr = curr->next;
    }
    return NULL;
}
