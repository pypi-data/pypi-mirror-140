#ifndef obsd_crypt_h_
#define obsd_crypt_h_

#include <stdbool.h>

bool obsd_checkpass(const char *password, const char *hash);

char *obsd_newhash(const char *password, int rounds);

#endif // obsd_crypt_h_
