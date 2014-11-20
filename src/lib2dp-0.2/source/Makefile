CFLAGS += -O3 -Wall

all: node_t.o list_t.o heap_t.o map_t.o pathfinder_t.o demo.o genmap.o lib2dp.a

node_t.o: node_t.c

list_t.o: list_t.c

heap_t.o: heap_t.c

map_t.o: map_t.c

pathfinder_t.o: pathfinder_t.c

demo.o: demo.c

genmap.o: genmap.c

lib2dp.a: node_t.o list_t.o heap_t.o map_t.o pathfinder_t.o
	ar r ../lib/lib2dp.a node_t.o list_t.o heap_t.o map_t.o pathfinder_t.o

clean:
	rm *.o
