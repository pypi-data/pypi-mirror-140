# cachetools-utils

Classes to add key prefix and stats to
[cachetools](https://pypi.org/project/cachetools/) classes and use
[redis](https://redis.io/) and
[memcached](https://memcached.org/) as storage backends,
and other utils.


## Caching

Caching is a key component of any significant Web or REST backend so as to avoid
performance issues when accessing the storage tier, in term of throughput,
latency and resource usage.

In order to reduce latency, most time should be lost in network accesses,
so reducing the number of trips is a key strategy. This suggests combining
data transfers where possible through higher-level queries, both at the
HTTP level and at the database level.

- write operations need to be sent to storage.

  Depending on transaction requirements, i.e. whether rare some data loss is
  admissible, various strategies can be applied, such as updating in parallel
  the cache and the final storage.

- read operations can be cached, at the price of possibly having inconsistency
  data shown to users.

  LFU/LRU cache strategies mean that inconsistent data can be kept in cache
  for indefinite time, which is annoying. A TLL expiration on top of that
  makes such discrepancies bounded in time, so that after some time the data
  shown are eventually up to date.

  Invalidating data from the cache requires a detailed knowledge of internal
  cache operations and are not very easy to manage at the application level,
  so devops should want to avoid this path if possible.

- data model

  Denormalizing the data model may help.

  Having an application-oriented view of the model (eg JSON objects rather than
  attributes and tables) can help performance, at the price of losing some of
  the consistency warranties provided by a database.
  The best of both word may be achieved, to some extent, by storing JSON
  data into a database such as [Postgres](https://postgresql.org/).

- multi-level caching

  Depending on the access pattern, it may or may not be useful to put
  such a strategy in place.

Basically the application should aim at maximizing throughput for the available
resources whilst keeping the latency under control, eg 90% of queries under
some limit.


## Module Documentation

This module provide the following cache wrappers suitable to use with
`cachetools`:

- Some classes provide actual storage or API to actual storage.
  For this purpose a cache is basically a key-value store, aka a dictionary,
  possibly with some constraints on keys (type, size) and values (size,
  serialization).

- Other classes add features on top of these, such as using a prefix so that
  a storage can be shared without collisions or keeping usage and efficiency
  statistics.

### PrefixedCache

Add a key prefix to an underlying cache to avoid key collisions.

```Python
import CacheToolsUtils as ctu

ct_base = cachetools.TTLCache(maxsize=1048576, ttl=600)
foo_cache = ctu.PrefixedCache(ct_base, "foo.")
bla_cache = ctu.PrefixedCache(ct_base, "bla.")

@cachetools.cached(cache=foo_cache)
def foo(…):
    return …

@cachetools.cached(cache=bla_cache)
def bla(…):
    return …
```

### StatsCache

Keep stats, cache hit rate shown with `hits()`.

```Python
scache = StatsCache(cache)
```

### TwoLevelCache

Two-level cache, for instance a local in-memory cachetools cache for the first
level, and a larger shared `redis` or `memcached` distributed cache for the
second level.
Whether such setting can bring performance benefits is an open question.

```Python
cache = TwoLevelCache(TTLCache(…), RedisCache(…))
```

There should be some consistency between the two level configurations
so that it make sense. For instance, having two TTL-ed stores would
suggest that the secondary has a longer TTL than the primary.

### MemCached

Basic wrapper, possibly with JSON key encoding.

```Python
import pymemcache as pmc

mc_base = pmc.Client(server="localhost", serde=ctu.JsonSerde())
cache = ctu.MemCached(mc_base)

@cachetools.cached(cache=cache)
def poc(…):
```

### PrefixedMemCached

Wrapper with a prefix.

```Python
pcache = ctu.PrefixedMemCached(mc_base, prefix="pic.")
```

### StatsMemCached

Wrapper with stats actually taken from the MemCached server.

```Python
scache = ctu.StatsMemCached(pcache)
```

### RedisCache

TTL'ed Redis wrapper, default ttl is 10 minutes.

```Python
import redis

rd_base = redis.Redis(host="localhost")
cache = ctu.RedisCache(rd_base, ttl=60)
```

### PrefixedRedisCache

Wrapper with a prefix *and* a ttl.

```Python
pcache = ctu.PrefixedRedisCache(rd_base, "pac.", ttl=3600)
```

### StatsRedisCache

Wrapper with stats (call `hits()`) *and* a ttl.
Stats are actually taken from the Redis server.

```Python
scache = ctu.StatsRedisCache(pcache)
```

### cacheMethods and cacheFunctions

This utility function create a prefixed cache around methods of an object
or functions in the global scope.
First parameter is the actual cache, second parameter is the object or scope,
third parameter is a dictionary mapping method names to prefixes.

```Python
ctu.cacheMethods(cache, obj, {"get_data": "1.", "get_some": "2."})
ctu.cacheFunctions(cache, globals(), {"some_func": "f."})
```


## Install

Install with `pip`:

```Shell
pip install CacheToolsUtils
```

See above for example usage.


## License

This code is public domain.


## Versions

### 2.0 on 2022-02-24

Add `cacheMethods` and `cacheFunctions`.
Improve documentation.
100% coverage test.

### 1.1.0 on 2022-01-30

Improve documentation.
Add `TwoLevelCache`.
Add 100% coverage test.

### 1.0.0 on 2022-01-29

Add `set`, `get` and `delete` forwarding to `RedisCache`, so that redis
classes can be stacked.

### 0.9.0 on 2022-01-29

Initial version extracted from another project.


## TODO

- improve documentation further.
- add a `close`?
- rename `hits`  `hit_rate`?
- add other efficiency statistics?
