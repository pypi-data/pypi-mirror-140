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

### `crypt_newhash`

```
string crypt_newhash(string password, int rounds = -1)
```

- If rounds is not supplied or is set to a negative integer, it automatically detects the appropriate number of rounds to use.
- Returns `None` on failure.

### `crypt_checkpass`

```
bool crypt_checkpass(string password, string pass_hash)
```

- Returns `True` if `pass_hash` is a valid hash of `password`, or it returns `False`.
