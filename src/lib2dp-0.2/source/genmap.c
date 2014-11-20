/* 2DPathfinder -- library for pathfinding in 2D maps
 * genmap.c
 * Copyright (c) 2005 Alessandro Presta <alessandro.presta@gmail.com>
 * Released under the GNU Lesser General Public License */

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int ix, iy;
int x_limit, y_limit;

int main(int argc, char *argv[])
{
	FILE *mapfile;
	mapfile = fopen("map.txt", "w");
	x_limit = atoi(argv[1]);
	y_limit = atoi(argv[2]);
	fprintf(mapfile, "%d %d\n", x_limit, y_limit);
	srand(time(NULL));
	for (iy = 0; iy < y_limit; ++iy) {
		for (ix = 0; ix < x_limit; ++ix) {
			if ((ix == 0 && iy == 0) || (ix == x_limit-1 && iy == y_limit-1))
				fprintf(mapfile, "%d", 0);
			else if (rand()%100 > 65)
				fprintf(mapfile, "%d", 1);
			else
				fprintf(mapfile, "%d", 0);
		}
		fprintf(mapfile, "\n"); 
	}
	fclose(mapfile);
	return 0;
}
