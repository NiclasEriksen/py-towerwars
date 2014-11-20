#include <math.h>
#include <stdlib.h>
#include <stdio.h>

static inline float InvSqrt (float x) {
    float xhalf = 0.5f*x;
    int i = *(int*)&x;
    i = 0x5f3759df - (i>>1);
    x = *(float*)&i;
	/* run two iterations of newton's method for 
	   increased accuracy */
    x = x*(1.5f - xhalf*x*x);
    x = x*(1.5f - xhalf*x*x);
    return x;
}

main(int argc, char *argv[]) 
{
	int i;
	float v = 2.0;
	printf("running 10M iterations of InvSqrt\n");
	
	for (i = 0; i < 10000000; i++) {
		v += InvSqrt(v);
		v += InvSqrt(v);
		v += InvSqrt(v);
		v += InvSqrt(v);
		v += InvSqrt(v);
		v += InvSqrt(v);
		v += InvSqrt(v);
		v += InvSqrt(v);
		v += InvSqrt(v);
		v += InvSqrt(v);
	}
	printf("%f\n", v);
}
