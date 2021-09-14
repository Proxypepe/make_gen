#include <stdio.h>
#include <assert.h>
#include "list.h"



int main()
{
    struct List root;
    push_back(&root, 10);
    assert(pop_front(&root)== 10);
    push_back(&root, 20);
    push_back(&root, 30);
    assert(pop_front(&root)== 20);
    push_back(&root, 40);
    push_front(&root, 50);
    assert(pop_back(&root) == 40);
    print_list(&root);
    delete_list(&root);
    return 0;
}