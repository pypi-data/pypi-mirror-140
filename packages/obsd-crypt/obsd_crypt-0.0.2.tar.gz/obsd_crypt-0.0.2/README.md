# OpenBSD crypt

Python 3 wrapper for OpenBSDs [crypt_checkpass(3)](https://man.openbsd.org/crypt_checkpass.3) and [crypt_newhash(3)](https://man.openbsd.org/crypt_newhash.3)

## Usage

```
$ python3
Python 3.8.12 (default, Sep 26 2021, 13:12:50)
[Clang 11.1.0 ] on openbsd7
Type "help", "copyright", "credits" or "license" for more information.
>>> from obsd_crypt import crypt_checkpass, crypt_newhash
>>> pass_hash = crypt_newhash("password")
>>> print(pass_hash)
$2b$10$RoAK6.GPdcXZId.cmFhmG.5YbXmANB/FyvzIbxj8uCKQWqRubiwee
>>> crypt_checkpass("password", pass_hash)
True
```

## Functions

### `crypt_checkpass(password: str, hash: str) -> bool`

Check a password against a given hash.

If both the hash and the password are the empty string, authentication is a success. Otherwise, the password is hashed and compared to the provided hash. If the hash is empty, authentication will always fail, but a default amount of work is performed to simulate the hashing operation. A successful match returns True and a failure returns False.

### `crypt_newhash(password: str, rounds: int = -1) -> str`
 
Return a new hash for a password.

The provided password is randomly salted and hashed and returned as a string using the bcrypt algorith. The number of rounds  can be any integer between 4 and 31, inclusive. If the number of rounds is not given or is negative, an appropriate number of rounds is automatically selected based on system performance.
