#include <stdlib.h>
#include <stdio.h>
#include "list.h"


bool isEmpty(struct List* list)
{
	if (list->head == NULL)
		return true;
	return false;
}

struct Node* makeNode(const int value)
{
	struct Node* node = (struct Node*)malloc(sizeof(struct Node*));
	node->data = value;
	node->next = NULL;
	node->prev = NULL;
	return node;
}

void push_back(struct List* list, const int value)
{
	if (isEmpty(list))
	{
		list->head = makeNode(value);
		list->tail = list->head;
	}
	else
	{
		struct Node* q = makeNode(value);
		q->prev = list->tail;
		list->tail->next = q;
		list->tail = q;
	}
}

int pop_back(struct List* list)
{
	if (!isEmpty(list))
	{
	    int res;
		if (list->tail->prev != NULL)
		{
			Node* q = list->tail;
			list->tail = list->tail->prev;
			res = q->data;
			free(q);
			list->tail->next = NULL;
		}
		else
		{
			res = list->head->data;
		    free(list->head);
			list->head = NULL;
			list->tail = NULL;
		}
		return res;
	}
	return 0;
}

void push_front(struct List* list, const int value)
{
	if (isEmpty(list))
	{
		list->head = makeNode(value);
		list->tail = list->head;
	}
	else
	{
		Node* q = makeNode(value);
		q->next = list->head;
		list->head->prev = q;
		list->head = q;
	}
}

int pop_front(struct List* list)
{
	if (!isEmpty(list)) {
        int res;
	    Node *q = list->head;
        list->head = list->head->next;
        res = q->data;
        free(q);
        if (list->head != NULL)
            list->head->prev = NULL;
        else
            list->tail = NULL;
        return res;
	}
	return 0;
}

void delete_list(struct List* list)
{
	Node* q = list->head;
	while (q != NULL)
	{
		Node* _tmp = q;
		q = q->next;
		free(_tmp);
	}
}

void print_list(struct List* list)
{
	Node* current = list->head;
	while (current != NULL)
	{
		printf("%i", current->data);
		current = current->next;
	}
}