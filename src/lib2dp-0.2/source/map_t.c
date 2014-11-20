/* 2DPathfinder -- library for pathfinding in 2D maps
 * map_t.c
 * Copyright (c) 2005 Alessandro Presta <alessandro.presta@gmail.com>
 * Released under the GNU Lesser General Public License */

#include "../include/map_t.h"
#include <stdlib.h>
#include <limits.h>

int Diagonal(int pos1, int pos2, int x_limit)
{
	int x1, y1, x2, y2;
	int d, s;
	x1 = X(pos1, x_limit);
	y1 = Y(pos1, x_limit);
	x2 = X(pos2, x_limit);
	y2 = Y(pos2, x_limit);
	d = min(abs(x1-x2), abs(y1-y2));
	s = abs(x1-x2) + abs(y1-y2);
	return 14 * d + 10 * (s-2*d);
} 
