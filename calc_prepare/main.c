
#include <stdio.h>
#include <stdint.h>
#include <string.h>

#include "sha2.h"

extern void sha256_init(sha256_ctx *ctx, uint8_t *buf);
extern void sha256_update(sha256_ctx *ctx, const unsigned char *message,
			  unsigned int len);
extern void sha256_final(sha256_ctx *ctx, unsigned char *digest);
int main()
{
	sha256_ctx ctx;
	unsigned char digest[32];
	unsigned char buf[64];

	sha256_init(&ctx, buf);

	memcpy(digest + 0, buf + 32 + 8, 4);
	memcpy(digest + 4, buf + 32 + 4, 4);
	memcpy(digest + 8, buf + 32 + 0, 4);

	sha256_update(&ctx, digest, 12);
	sha256_final(&ctx, digest);


	return 0;
}
