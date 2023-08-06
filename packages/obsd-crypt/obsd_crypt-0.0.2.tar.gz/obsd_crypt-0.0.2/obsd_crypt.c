#include "obsd_crypt.h"

#include <pwd.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

bool obsd_checkpass(const char *password, const char *hash) {
	return crypt_checkpass(password, hash) == 0;
}

char *obsd_newhash(const char *password, int rounds) {
	char *hash;
	int err;
	char pref[12] = "bcrypt,";

	hash = (char *)calloc(1, _PASSWORD_LEN);
	if (!hash) {
		return NULL;
	}

	if(rounds > 31)
		rounds = 31;
	if(rounds < 4 && rounds >= 0)
		rounds = 4;

	if(rounds < 0)
		snprintf(pref + 7, 5, "%s", "a");
	else
		snprintf(pref + 7, 5, "%d", rounds);

	err = crypt_newhash(password, pref, hash, _PASSWORD_LEN);
	if (err == -1) {
		free(hash);
		return NULL;
	}
	return hash;
}
