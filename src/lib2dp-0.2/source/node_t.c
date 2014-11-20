/* 2DPathfinder -- library for pathfinding in 2D maps
 * node_t.c
 * Copyright (c) 2005 Alessandro Presta <alessandro.presta@gmail.com>
 * Released under the GNU Lesser General Public License */

#include "../include/node_t.h"

void nCopy(node_t *source, node_t *dest)
{
	dest->pos = source->pos;
	dest->f = source->f;
	dest->g = source->g;
} 

int nCompare(node_t *node1, node_t *node2)
{
	int result;
	result = node1->f - node2->f;
	return result;
} 
