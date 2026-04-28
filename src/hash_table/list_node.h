#ifndef LINKED_LIST_H
#define LINKED_LIST_H

#include "types.h"
#include "value_array.h"

typedef struct ListNode
{
    key_type key;
    ValueArray values;
    struct ListNode *next;
} ListNode;

/**
 * Creates a new list node with the given key and value.
 * Returns a pointer to the newly created node, or NULL if memory allocation fails.
 *
 * @param key The key to be stored in the node.
 * @param value The value to be stored in the node.
 * @return A pointer to the newly created ListNode, or NULL on failure.
 */
ListNode *listnode_create(key_type key, key_type value);

/**
 * Frees the memory allocated for a list node.
 *
 * @param node A pointer to the ListNode to be freed.
 */
void listnode_free(ListNode *node);

/**
 * Frees the memory allocated for an entire linked list.
 *
 * @param head A pointer to the head of the linked list to be freed.
 */
void list_free(ListNode *head);

/**
 * Inserts a new node with the given key and value into the linked list.
 * If a node with the same key already exists, its value is appended.
 *
 * @param head A pointer to the pointer to the head of the linked list.
 * @param key The key to be inserted or updated.
 * @param value The value to be associated with the key.
 * @return 0 on success, or -1 if memory allocation fails.
 */
int list_insert(ListNode **head, key_type key, key_type value);

/**
 * Deletes a node with a given key from the linked list.
 * This effectively removes all values associated with the key.
 *
 * @param head A pointer to the pointer to the head of the linked list.
 * @param key The key of the node to be deleted.
 * @return 0 if the node was successfully deleted, or -1 if the node was not found.
 */
int list_delete(ListNode **head, key_type key);

/**
 * Finds the node with the specified key in the linked list.
 * Returns a pointer to the node if found, or NULL if the node is not found.
 *
 * @param head A pointer to the head of the linked list.
 * @param key The key of the node to be found.
 * @return A pointer to the ListNode with the specified key, or NULL if not found
 */
ListNode *list_find(ListNode *head, key_type key);

#endif
