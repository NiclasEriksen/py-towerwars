/* 2DPathfinder -- library for pathfinding in 2D maps
 * demo.c
 * Copyright (c) 2005 Alessandro Presta <alessandro.presta@gmail.com>
 * Released under the GNU Lesser General Public License */

#include "../include/pathfinder_t.h"
#include <stdio.h>
#include <stdlib.h>

map_t map;
short *cells;
int x_limit, y_limit;
FILE *input, *output;

int main()
{
	int ix, iy;
	pathfinder_t *pf;
	list_t *path;
	int c;
	char a;
	int cost;
	int result;
	int st_x, st_y, tar_x, tar_y, st, tar;
	list_iterator_t lit;
	printf("2D Pathfinder demonstration by Alessandro Presta\n");
	printf("Loading...\n");
	input = fopen("map.txt", "r");
	fscanf(input, "%d %d", &x_limit, &y_limit);
	cells = malloc(x_limit*y_limit*sizeof(short));
	for (iy = 0; iy < y_limit; iy++) {
		fscanf(input, "%c", &a);
		for (ix = 0; ix < x_limit; ix++) {
			fscanf(input, "%c", &a);
			cells[POS(ix, iy, x_limit)] = a - 48;
		}
	}
	fclose(input);
	pf = pfAlloc(x_limit*y_limit, x_limit*y_limit);
	map.x_limit = x_limit;
	map.y_limit = y_limit;
	st_x = st_y = 0;
	tar_x = x_limit-1; tar_y = y_limit-1;
	st = POS(st_x, st_y, x_limit);
	tar = POS(tar_x, tar_y, x_limit);
	map.cells = cells;
	pfSetMap(pf, &map);
	path = lAlloc();
	printf("Ready. Enter any key...\n");
	scanf("%d", &c);
	printf("Pathfinding...\n");
	result = pfFindPath(pf, st, tar, path, &cost);
	printf("Finished.\n");
	printf("Result: ");
	if (result == SOLVED) {
		printf("Solved\n");
		printf("Cost: %d\n", cost);
		printf("Writing path...\n");
		output = fopen("map.txt", "w");
		fprintf(output, "%d %d\n", x_limit, y_limit);
		for (lit = path->front; lit != 0; lit = lit->next)
			cells[lit->val] = 5;
		cells[st] = 3;
		cells[tar] = 4;
		for (iy = 0; iy < y_limit; ++iy) { 
			for (ix = 0; ix < x_limit; ++ix) { 
				if (cells[POS(ix, iy, x_limit)] == 1)
					fprintf(output, "%c", '1');
				else if  (cells[POS(ix, iy, x_limit)] == 0)
					fprintf(output, "%c", '0'); 
				else if (cells[POS(ix, iy, x_limit)] == 5)
					fprintf(output, "%c", 'x');   
				else if (cells[POS(ix, iy, x_limit)] == 3)
					fprintf(output, "%c", 'S');      
				else if (cells[POS(ix, iy, x_limit)] == 4)
					fprintf(output, "%c", 'T');
			}
			fprintf(output, "\n");
		}
		fclose(output);
	}
	else
		printf("No solution\n");
	printf("Enter any key...\n");
	scanf("%d", &c);
	free(cells);	
	free(path);
	pfFree(pf);
	return 0;
} 
