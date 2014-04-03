
#include <stdio.h>
#include <stdint.h>
#include <string.h>

#include "hexdump.c"

extern void data_pkg(const uint8_t *data, uint8_t *out);
int main()
{
	uint8_t data[64];
	uint8_t out[88];

	data_pkg(data, out);

	hexdump(out, 88);
	return 0;
}
