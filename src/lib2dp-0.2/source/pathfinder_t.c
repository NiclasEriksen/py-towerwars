/* 2DPathfinder -- library for pathfinding in 2D maps
 * pathfinder_t.c
 * Copyright (c) 2005 Alessandro Presta <alessandro.presta@gmail.com>
 * Released under the GNU Lesser General Public License */

#include "../include/pathfinder_t.h"
#include <stdlib.h>
#include <memory.h>

pathfinder_t* pfAlloc(int initial_cache, int max_nodes)
{
	pathfinder_t *pathfinder;
	pathfinder = malloc(sizeof(pathfinder_t));
	if (pathfinder) {
		pathfinder->open_list = hAlloc(initial_cache, max_nodes);
		pathfinder->closed_list = malloc(max_nodes*sizeof(short));
		pathfinder->parent = malloc(max_nodes*sizeof(int));
		if (pathfinder->open_list && pathfinder->closed_list && pathfinder->parent) 
			memset(pathfinder->closed_list, 0, max_nodes*sizeof(short));   
		pathfinder->total_nodes = max_nodes;
	} 
	else
		pathfinder = 0;
	return pathfinder;
} 

void pfFree(pathfinder_t *pathfinder)
{
	hFree(pathfinder->open_list); 
	free(pathfinder->closed_list);
	free(pathfinder->parent);
	free(pathfinder);
} 

void pfSetMap(pathfinder_t *pathfinder, map_t *map)
{
	pathfinder->map = map;
} 

int pfFindPath(pathfinder_t *pathfinder, int start_pos, int target_pos, list_t *path, int *cost)
{
	node_t start_node;
	node_t current_node;
	node_t *min_node_ptr;
	int adjacent_pos;
	int adjacent_x, adjacent_y;
	node_t *adjacent_node_ptr;
	int ix, iy;
	int current_step_pos;
	node_t *target_node_ptr;
	int step = 0;
	if (start_pos == target_pos) {
		*cost = 0;
		return SOLVED;
	} 
	if (pathfinder->map->cells[start_pos] != 0 || pathfinder->map->cells[target_pos] != 0 || start_pos < 0 || target_pos < 0 || start_pos >= POSITION_LIMIT || target_pos >= POSITION_LIMIT)
		return NO_SOLUTION;
	start_node.pos = start_pos;
	SET_PARENT(start_pos, NO_PARENT);
	start_node.f = Diagonal(start_pos, target_pos, pathfinder->map->x_limit);
	start_node.g = 0;
	PUSH_OPEN(start_node);
	while (OPEN_COUNT > 0) {
		min_node_ptr = GET_MIN_OPEN();
		nCopy(min_node_ptr, &current_node);
		POP_OPEN();
		PUSH_CLOSED(current_node.pos);
		for (ix = -1; ix <= 1; ++ix)
			for (iy = -1; iy <= 1; ++iy) {
			adjacent_x = X(current_node.pos, pathfinder->map->x_limit)+ix;
			adjacent_y = Y(current_node.pos, pathfinder->map->x_limit)+iy;
			adjacent_pos = POS(adjacent_x, adjacent_y, pathfinder->map->x_limit);
			if ((ix || iy) && IS_VALID(adjacent_x, adjacent_y) && !IS_CLOSED(adjacent_pos) && IS_FREE(adjacent_pos)) {
			  step = Diagonal(current_node.pos, adjacent_pos, pathfinder->map->x_limit);
				if (IS_OPEN(adjacent_pos)) {
					adjacent_node_ptr = OPEN_NODE(adjacent_pos);
					if (adjacent_node_ptr->g > current_node.g + step) {
						adjacent_node_ptr->g = current_node.g + step;
						adjacent_node_ptr->f = adjacent_node_ptr->g + step;
						SET_PARENT(adjacent_pos, current_node.pos);
					}  
				}  
				else {
					adjacent_node_ptr = malloc(sizeof(node_t));
					adjacent_node_ptr->pos = adjacent_pos;
					adjacent_node_ptr->g = current_node.g + step;
					adjacent_node_ptr->f = adjacent_node_ptr->g + step;
					SET_PARENT(adjacent_pos, current_node.pos);
					PUSH_OPEN(*adjacent_node_ptr);
					free(adjacent_node_ptr);
				}  
				if (adjacent_pos == target_pos)
					goto RETURN_SOLVED;  
			}  
			}
	}  
	/* RETURN_NO_SOLUTION: */
	pfReset(pathfinder);
	return NO_SOLUTION;
RETURN_SOLVED:
		lPushFront(path, target_pos);
  current_step_pos = GET_PARENT(target_pos);
  while (current_step_pos != NO_PARENT) {
	  lPushFront(path, current_step_pos);
	  current_step_pos = GET_PARENT(current_step_pos);
  }   
  target_node_ptr = OPEN_NODE(target_pos);
  *cost = target_node_ptr->g;  	
  pfReset(pathfinder);
  return SOLVED;
} 

void pfReset(pathfinder_t *pathfinder)
{
	memset(pathfinder->closed_list, 0, pathfinder->total_nodes*sizeof(short));
	hReset(pathfinder->open_list); 
} 
