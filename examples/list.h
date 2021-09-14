#ifndef LIST_H
#define LIST_H

typedef enum { false, true } bool;

typedef struct Node {
	struct Node* next;
	struct Node* prev;
	int data;
}Node;

typedef struct List {
	struct Node* head;
	struct Node* tail;
}List;

bool isEmpty(struct List*);
struct Node* makeNode(const int);
void makeList(struct List*);
void push_back(struct List*, const int);
int pop_back(struct List*);
void push_front(struct List*, const int);
int pop_front(struct List* list);
void delete_list(struct List*);
void print_list(struct List*);

#endif /*LIST_H*/