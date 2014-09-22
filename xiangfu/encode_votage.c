#include <stdio.h>
#include <stdint.h>

static inline uint8_t rev8(uint8_t d)
{
	int i;
	uint8_t out = 0;

	/* (from left to right) */
	for (i = 0; i < 8; i++)
		if (d & (1 << i))
		out |= (1 << (7 - i));

	return out;
}

static inline uint32_t encode_voltage(uint32_t v)
{
	return rev8((0x78 - v / 125) << 1 | 1) << 8;
}

static inline uint32_t decode_voltage(uint32_t v)
{
	return (0x78 - (rev8(v >> 8) >> 1)) * 125;
}

int main(int argc, char **argv)
{
	int val;

	sscanf(argv[1], "%d", &val);
	printf("Votage: %04x\n", encode_voltage(val));

	return 0;
}
