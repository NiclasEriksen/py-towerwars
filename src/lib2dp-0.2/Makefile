all: lib2dp demo genmap

lib2dp: 
	$(MAKE) -C source lib2dp.a

demo: 
	$(MAKE) -C source demo.o
	$(MAKE) -C source lib2dp.a
	cc -O3 -Wall -o bin/demo source/demo.o -Llib -l2dp
	
genmap:
	$(MAKE) -C source genmap.o
	cc -O3 -Wall -o bin/genmap source/genmap.o

clean:
	$(MAKE) -C source clean
