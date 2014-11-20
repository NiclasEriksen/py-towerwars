/* 2DPathfinder -- library for pathfinding in 2D maps
 * heap_t.c
 * Copyright (c) 2005 Alessandro Presta <alessandro.presta@gmail.com>
 * Released under the GNU Lesser General Public License */

#include "../include/heap_t.h"
#include <stdlib.h>
#include <memory.h>

heap_t* hAlloc(int initial_cache, int max_nodes)
{
	heap_t *heap;
	heap = malloc(sizeof(heap_t));
	if (heap) {
		heap->nodes = malloc(initial_cache*sizeof(node_t));
		heap->flags = malloc(max_nodes*sizeof(short));
		if (heap->nodes && heap->flags) {
			heap->size = initial_cache;
			memset(heap->flags, 0, max_nodes*sizeof(short));
		}  
		else
			heap->size = 0;
		heap->elems = 0;
		heap->total_nodes = max_nodes;
	}
	else
		heap = 0;
	return heap;
} 

void hFree(heap_t *heap)
{
	free(heap->nodes);
	free(heap->flags);
	free(heap);
} 

void hInsert(heap_t *heap, node_t *node)
{
	if (heap->elems+1 >= heap->size) {
		heap->nodes = realloc(heap->nodes, (heap->size+DEFAULT_HEAP_REALLOC_ADDEND)*sizeof(node_t));
		heap->size += DEFAULT_HEAP_REALLOC_ADDEND;
	}
	nCopy(node, &(heap->nodes[heap->elems++]));
	heap->flags[node->pos] = 1;
	hSendUp(heap, heap->elems-1);
}

void hPop(heap_t *heap)
{
	heap->flags[heap->nodes[0].pos] = 0;
	nCopy(&(heap->nodes[heap->elems-1]), &(heap->nodes[0]));
	--heap->elems;
	hSendDown(heap, 0);
} 

node_t* hGetMin(heap_t *heap)
{
	node_t *min = &(heap->nodes[0]);
	return min;
}

void hSendUp(heap_t *heap, int node_id)
{
	int father_id;
	father_id = FATHER(node_id);
	if (father_id >= 0) {
		if (nCompare(&(heap->nodes[node_id]), &(heap->nodes[father_id])) < 0) {
			SWAP(node_id, father_id);
			hSendUp(heap, father_id);
		} 
	} 
} 

void hSendDown(heap_t *heap, int node_id)
{
	int min_son_id;
	if (2*node_id+1 < heap->elems) {
		min_son_id = MIN_SON(node_id);
		if (nCompare(&(heap->nodes[node_id]), &(heap->nodes[min_son_id])) > 0) {
			SWAP(node_id, min_son_id);
			hSendDown(heap, min_son_id);
		}
	} 
} 

void hReset(heap_t *heap)
{
	heap->elems = 0;
	memset(heap->flags, 0, heap->total_nodes*sizeof(short));
}

node_t* hFind(heap_t *heap, int pos)
{
	int i;
	for (i = 0; i < heap->size; ++i)
		if (heap->nodes[i].pos == pos)
			return &(heap->nodes[i]);
	return 0;
}
