/* 2DPathfinder -- library for pathfinding in 2D maps
 * list_t.c
 * Copyright (c) 2005 Alessandro Presta <alessandro.presta@gmail.com>
 * Released under the GNU Lesser General Public License */

#include "../include/list_t.h"
#include <stdlib.h>

list_t* lAlloc()
{
	list_t *list;
	list = malloc(sizeof(list_t));
	list->front = 0;
	list->back = 0;
	return list;
}

void lFree(list_t *list)
{
	lelem_t *next;
	for ( ; list->front != 0; list->front = next) {
		next = list->front->next;
		free(list->front);
	}
	free(list);
}

void lPushFront(list_t *list, int val)
{
	lelem_t *newel;
	newel = malloc(sizeof(lelem_t));
	newel->val = val;
	newel->next = list->front;
	list->front = newel;
	if (newel->next == 0)
		list->back = newel;
}

void lPushBack(list_t *list, int val)
{
	lelem_t *newel;
	newel = malloc(sizeof(lelem_t));
	newel->val = val;
	newel->next = 0;
	if (list->front == 0) {
		list->front = newel;
		list->back = newel;
		return;
	}
	list->back->next = newel;
	list->back = newel;
}	

void lPopFront(list_t *list)
{
	lelem_t *delel;
	delel = list->front;
	if (delel == 0)
		return;
	list->front = delel->next;
	free(delel);	
}

void lPopBack(list_t *list)
{
	lelem_t *delel, *parent;
	if (list->back == 0)
		return;
	delel = list->back;	
	parent = list->front;
	while (parent->next != 0 && parent->next != delel) 
		parent = parent->next;
	parent->next = 0;
	list->back = parent;
	free(delel);
}

int lGetFront(list_t *list)
{
	if (list->front != 0)
		return list->front->val;	
	return -1;
}

int lGetBack(list_t *list)
{
	if (list->back != 0)
		return list->back->val;
	return -1;
}
	
void lClear(list_t *list)
{
	lelem_t *next;
	for ( ; list->front != 0; list->front = next) {
		next = list->front->next;
		free(list->front);
	}
}
