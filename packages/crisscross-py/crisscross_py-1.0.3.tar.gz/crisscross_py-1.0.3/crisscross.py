import redis
from redis.exceptions import RedisError
import elixir  # elixir_py
import os
import sys
from pathlib import Path
import argparse
import base58
import yaml

DEFAULT_TTL = 1000 * 60 * 60 * 24
DEFAULT_TIMEOUT = 1000 * 10


def decode(raw):
    return elixir.binary_to_term(raw)


def encode(raw):
    return elixir.term_to_binary(raw)


def read_var(t):
    if not t:
        return ""
    if t == "^defaultcluster":
        return base58.b58decode("2UPhq1AXgmhSd6etUcSQRPfm42mSREcjUixSgi9N8nU1YoC")
    elif t.startswith("*") and "#" in t:
        parts = t.split("#")
        base = parts[0].lstrip("*")
        with open(f"{base}", "r") as file:
            configuration = yaml.safe_load(file)
        return base58.b58decode(configuration[parts[1]])
    else:
        return base58.b58decode(t)


def print_get(m):
    if m:
        sys.stdout.buffer.write(next(iter(m.values())))


def print_ret(ret):
    if ret:
        print(base58.b58encode(ret).decode("utf8"))


class CrissCrossJobSub:
    def __init__(self, pubsub_conn):
        self.conn = pubsub_conn

    def subscribe_to_job(self, tree):
        self.conn.subscribe(tree)

    def listen(self):
        for ret in self.conn.listen():
            if ret["type"] == "message":
                tree = ret["channel"]
                data = decode(ret["data"])
                if len(data) == 3:
                    yield (tree, data[0], decode(data[1]), data[2])
                else:
                    raise Exception(data[0])


class CrissCrossStreamSub:
    def __init__(self, pubsub_conn):
        self.conn = pubsub_conn

    def subsribe_to_stream(self, stream_reference):
        self.conn.psubscribe(stream_reference)

    def listen(self):
        for ret in self.conn.listen():
            if ret["type"] == "pmessage":
                stream = ret["pattern"]
                data = decode(ret["data"])
                if len(data) == 2:
                    yield (stream, decode(data[0]), data[1])
                else:
                    raise Exception(data[0])


class CrissCross:
    def __init__(self, **kwargs):
        host = kwargs.get("host", os.getenv("HOST", "localhost"))
        port = kwargs.get("port", int(os.getenv("PORT", "11111")))
        username = os.getenv("CRISSCROSS_USERNAME", None)
        password = os.getenv("CRISSCROSS_PASSWORD", None)
        if username is not None:
            kwargs = dict(username=username, password=password)
        else:
            kwargs = {}

        self.conn = redis.Redis(host=host, port=port, **kwargs)

    def pubsub_streams(self):
        return CrissCrossStreamSub(self.conn.pubsub())

    def pubsub_jobs(self):
        return CrissCrossJobSub(self.conn.pubsub())

    def keypair(self):
        ret = self.conn.execute_command("KEYPAIR")
        return ret[0], ret[1], ret[2]

    def cluster(self):
        ret = self.conn.execute_command("CLUSTER")
        return ret[0], ret[1], ret[2], ret[3]

    def tunnel_open(self, cluster, name, auth_token, local_port, host, port):
        ret = self.conn.execute_command(
            "TUNNELOPEN", cluster, name, auth_token, str(local_port), host, str(port)
        )
        return ret == b"OK"

    def tunnel_close(self, local_port):
        ret = self.conn.execute_command("TUNNELCLOSE", str(local_port))
        return ret == b"OK"

    def tunnel_allow(self, token, cluster, private_key, auth_token, host, port):
        ret = self.conn.execute_command(
            "TUNNELALLOW", token, cluster, private_key, auth_token, host, str(port)
        )
        return ret == b"OK"

    def tunnel_disallow(self, cluster, host, port):
        ret = self.conn.execute_command("TUNNELDISALLOW", cluster, host, str(port))
        return ret == b"OK"

    def stream_start(self, tree):
        ref = self.conn.execute_command("STREAMSTART", tree)
        return ref

    def remote_stream_start(self, cluster, tree):
        ref = self.conn.execute_command("REMOTE", cluster, "1", "STREAMSTART", tree)
        return ref

    def stream_send(self, stream_ref, msg, argument, timeout=DEFAULT_TIMEOUT):
        ret = self.conn.execute_command(
            "STREAMSEND", stream_ref, msg, encode(argument), str(timeout)
        )
        return ret == b"OK"

    def job_get(self, tree, timeout=DEFAULT_TIMEOUT):
        [method, arg, ref] = self.conn.execute_command("JOBGET", tree, str(timeout))
        return method, decode(arg), ref

    def job_announce(self, cluster, tree, ttl=DEFAULT_TTL):
        return (
            self.conn.execute_command("JOBANNOUNCE", cluster, tree, str(ttl)) == b"OK"
        )

    def job_do(self, tree, method, argument, timeout=DEFAULT_TIMEOUT):
        rets = self.conn.execute_command(
            "JOBDO", tree, str(timeout), method, encode(argument)
        )
        ret = rets[0]
        if len(ret) == 2:
            return (decode(ret[0]), ret[1])
        else:
            raise Exception(ret[0])

    def remote_job_do(
        self, cluster, tree, method, argument, num=1, timeout=DEFAULT_TIMEOUT
    ):
        rets = self.conn.execute_command(
            "REMOTE",
            cluster,
            str(num),
            "JOBDO",
            tree,
            str(timeout),
            method,
            encode(argument),
        )
        ret = rets[0]
        if len(ret) == 2:
            return (decode(ret[0]), ret[1])
        else:
            print(ret)
            raise RedisError(ret)

    def job_local(self, name, ttl=DEFAULT_TIMEOUT):
        return self.conn.execute_command("JOBLOCAL", name, str(ttl)) == b"OK"

    def job_respond(self, ref, response, private_key, timeout=DEFAULT_TIMEOUT):
        return (
            self.conn.execute_command("JOBRESPOND", ref, encode(response), private_key)
            == b"OK"
        )

    def job_verify(self, tree, method, argument, response, signature, public_key):
        return (
            self.conn.execute_command(
                "JOBVERIFY",
                tree,
                method,
                encode(argument),
                encode(response),
                signature,
                public_key,
            )
            == 1
        )

    def push(self, cluster, value, ttl=DEFAULT_TTL):
        return self.conn.execute_command("PUSH", cluster, value, str(ttl)) == b"OK"

    def remote(self, cluster, num_conns, *args):
        return self.conn.execute_command("REMOTE", cluster, num_conns, *args)

    def remote_no_local(self, cluster, num_conns, *args):
        return self.conn.execute_command("REMOTENOLOCAL", cluster, num_conns, *args)

    def var_set(self, var, val):
        return self.conn.execute_command("VARSET", var, val)

    def var_get(self, var):
        return self.conn.execute_command("VARGET", var)

    def var_delete(self, var):
        return self.conn.execute_command("VARDELETE", var)

    def var_with(self, var, *args):
        return self.conn.execute_command("VARWITH", var, *args)

    def compact(self, tree, ttl=DEFAULT_TTL):
        [new_tree, new_size, old_size] = self.conn.execute_command(
            "COMPACT", tree, str(ttl)
        )
        return new_tree, new_size, old_size

    def bytes_written(self, tree):
        return self.conn.execute_command("BYTESWRITTEN", tree)

    def var_with_bytes_written(self, var):
        return self.conn.execute_command("VARWITH", var, "BYTESWRITTEN")

    def remote_bytes_written(self, cluster, tree, num=1, cache=True):
        s = "REMOTE" if cache else "REMOTENOLOCAL"
        return self.conn.execute_command(
            s, cluster, num, "BYTESWRITTEN", tree, num=1, cache=True
        )

    def var_with_remote_bytes_written(self, var, cluster, num=1, cache=True):
        s = "REMOTE" if cache else "REMOTENOLOCAL"
        return self.conn.execute_command(
            "VARWITH", var, s, cluster, num, "BYTESWRITTEN"
        )

    def put_multi(self, loc, kvs, ttl=DEFAULT_TTL):
        flat_ls = [encode(item) for tup in kvs for item in tup]
        return self.conn.execute_command("PUTMULTI", loc, str(ttl), *flat_ls)

    def put_multi_bin(self, loc, kvs, ttl=DEFAULT_TTL):
        flat_ls = [item for tup in kvs for item in tup]
        return self.conn.execute_command("PUTMULTIBIN", loc, str(ttl), *flat_ls)

    def delete_multi(self, loc, keys, ttl=DEFAULT_TTL):
        keys = [encode(item) for item in keys]
        return self.conn.execute_command("DELMULTI", loc, str(ttl), *keys)

    def delete_multi_bin(self, loc, keys, ttl=DEFAULT_TTL):
        return self.conn.execute_command("DELMULTIBIN", loc, str(ttl), *keys)

    def get_multi(self, loc, keys):
        keys = [encode(item) for item in keys]
        r = self.conn.execute_command("GETMULTI", loc, *keys)
        r = [decode(z) for z in r]
        return dict(zip(*[iter(r)] * 2))

    def get_multi_bin(self, loc, keys):
        r = self.conn.execute_command("GETMULTIBIN", loc, *keys)
        return dict(zip(*[iter(r)] * 2))

    def fetch(self, loc, key):
        key = encode(key)
        r = self.conn.execute_command("FETCH", loc, key)
        return decode(r)

    def fetch_bin(self, loc, key):
        return self.conn.execute_command("FETCHBIN", loc, key)

    def has_key(self, loc, key):
        key = encode(key)
        return self.conn.execute_command("HASKEY", loc, key) == 1

    def has_key_bin(self, loc, key):
        return self.conn.execute_command("HASKEYBIN", loc, key) == 1

    def sql(self, loc, *statements, ttl=DEFAULT_TTL):
        r = self.conn.execute_command("SQL", loc, str(ttl), *statements)
        return r[0], [decode(s) for s in r[1:]]

    def sql_read(self, loc, *statements):
        r = self.conn.execute_command("SQLREAD", loc, *statements)
        return r[0], [decode(s) for s in r[1:]]

    def remote_get_multi(self, cluster, loc, keys, num=1, cache=True):
        keys = [encode(item) for item in keys]
        s = "REMOTE" if cache else "REMOTENOLOCAL"
        r = self.conn.execute_command(s, cluster, num, "GETMULTI", loc, *keys)
        r = [decode(z) for z in r]
        return dict(zip(*[iter(r)] * 2))

    def remote_get_multi_bin(self, cluster, loc, keys, num=1, cache=True):
        s = "REMOTE" if cache else "REMOTENOLOCAL"
        r = self.conn.execute_command(s, cluster, num, "GETMULTIBIN", loc, *keys)
        return dict(zip(*[iter(r)] * 2))

    def remote_fetch(self, cluster, loc, key, num=1, cache=True):
        key = encode(key)
        s = "REMOTE" if cache else "REMOTENOLOCAL"
        r = self.conn.execute_command(s, cluster, num, "FETCH", loc, key)
        return decode(r)

    def remote_fetch_bin(self, cluster, loc, key, num=1, cache=True):
        s = "REMOTE" if cache else "REMOTENOLOCAL"
        return self.conn.execute_command(s, cluster, num, "FETCHBIN", loc, key)

    def remote_has_key(self, cluster, loc, key, num=1, cache=True):
        key = encode(key)
        s = "REMOTE" if cache else "REMOTENOLOCAL"
        return self.conn.execute_command(s, cluster, num, "HASKEY", loc, key) == 1

    def remote_has_key_bin(self, cluster, loc, key, num=1, cache=True):
        s = "REMOTE" if cache else "REMOTENOLOCAL"
        return self.conn.execute_command(s, cluster, num, "HASKEYBIN", loc, key) == 1

    def remote_sql(self, cluster, loc, *statements, num=1, cache=True, ttl=DEFAULT_TTL):
        s = "REMOTE" if cache else "REMOTENOLOCAL"
        r = self.conn.execute_command(
            s, cluster, num, "SQL", loc, str(ttl), *statements
        )
        return r[0], [decode(s) for s in r[1:]]

    def remote_sql_read(self, cluster, loc, *statements, num=1, cache=True):
        s = "REMOTE" if cache else "REMOTENOLOCAL"
        r = self.conn.execute_command(s, cluster, num, "SQLREAD", loc, *statements)
        return r[0], [decode(s) for s in r[1:]]

    def var_with_put_multi(self, var, kvs, ttl=DEFAULT_TTL):
        flat_ls = [encode(item) for tup in kvs for item in tup]
        return self.conn.execute_command("VARWITH", var, "PUTMULTI", str(ttl), *flat_ls)

    def var_with_put_multi_bin(self, var, kvs, ttl=DEFAULT_TTL):
        flat_ls = [item for tup in kvs for item in tup]
        return self.conn.execute_command(
            "VARWITH", var, "PUTMULTIBIN", str(ttl), *flat_ls
        )

    def var_with_delete_multi(self, loc, keys, ttl=DEFAULT_TTL):
        keys = [encode(item) for item in keys]
        return self.conn.execute_command("VARWITH", var, "DELMULTI", str(ttl), *keys)

    def var_with_delete_multi_bin(self, var, keys, ttl=DEFAULT_TTL):
        return self.conn.execute_command("VARWITH", var, "DELMULTIBIN", str(ttl), *keys)

    def var_with_get_multi(self, var, keys):
        keys = [encode(item) for item in keys]
        r = self.conn.execute_command("VARWITH", var, "GETMULTI", *keys)
        r = [decode(z) for z in r]
        return dict(zip(*[iter(r)] * 2))

    def var_with_get_multi_bin(self, var, keys):
        r = self.conn.execute_command("VARWITH", var, "GETMULTIBIN", *keys)
        return dict(zip(*[iter(r)] * 2))

    def var_with_fetch(self, var, key):
        key = encode(key)
        r = self.conn.execute_command("VARWITH", var, "FETCH", key)
        return decode(r)

    def var_with_fetch_bin(self, var, key):
        return self.conn.execute_command("VARWITH", var, "FETCHBIN", key)

    def var_with_has_key(self, var, key):
        key = encode(key)
        return self.conn.execute_command("VARWITH", var, "HASKEY", key) == 1

    def var_with_has_key_bin(self, var, key):
        return self.conn.execute_command("VARWITH", var, "HASKEYBIN", key) == 1

    def var_with_sql(self, var, *statements, ttl=DEFAULT_TTL):
        r = self.conn.execute_command("VARWITH", var, "SQL", str(ttl), *statements)
        return r[0], [decode(s) for s in r[1:]]

    def var_with_sql_read(self, var, *statements):
        r = self.conn.execute_command("VARWITH", var, "SQLREAD", *statements)
        return [decode(s) for s in r]

    def var_with_remote_get_multi(self, var, cluster, keys, num=1, cache=True):
        keys = [encode(item) for item in keys]
        s = "REMOTE" if cache else "REMOTENOLOCAL"
        r = self.conn.execute_command(
            "VARWITH", var, s, cluster, num, "GETMULTI", *keys
        )
        r = [decode(z) for z in r]
        return dict(zip(*[iter(r)] * 2))

    def var_with_remote_get_multi_bin(self, var, cluster, keys, num=1, cache=True):
        s = "REMOTE" if cache else "REMOTENOLOCAL"
        r = self.conn.execute_command(
            "VARWITH", var, s, cluster, num, "GETMULTIBIN", *keys
        )
        return dict(zip(*[iter(r)] * 2))

    def var_with_remote_fetch(self, var, cluster, key, num=1, cache=True):
        key = encode(key)
        s = "REMOTE" if cache else "REMOTENOLOCAL"
        r = self.conn.execute_command("VARWITH", var, s, cluster, num, "FETCH", key)
        return decode(r)

    def var_with_remote_fetch_bin(self, var, cluster, key, num=1, cache=True):
        s = "REMOTE" if cache else "REMOTENOLOCAL"
        return self.conn.execute_command(
            "VARWITH", var, s, cluster, num, "FETCHBIN", key
        )

    def var_with_remote_has_key(self, var, cluster, key, num=1, cache=True):
        key = encode(key)
        s = "REMOTE" if cache else "REMOTENOLOCAL"
        return (
            self.conn.execute_command("VARWITH", var, s, cluster, num, "HASKEY", key)
            == 1
        )

    def var_with_remote_has_key_bin(self, var, cluster, key, num=1, cache=True):
        s = "REMOTE" if cache else "REMOTENOLOCAL"
        return (
            self.conn.execute_command("VARWITH", var, s, cluster, num, "HASKEYBIN", key)
            == 1
        )

    def var_with_remote_sql(
        self, var, cluster, *statements, num=1, cache=True, ttl=DEFAULT_TTL
    ):
        s = "REMOTE" if cache else "REMOTENOLOCAL"
        r = self.conn.execute_command(
            "VARWITH", var, s, cluster, num, "SQL", str(ttl) * statements
        )
        return r[0], [decode(s) for s in r[1:]]

    def var_with_remote_sql_read(self, var, cluster, *statements, num=1, cache=True):
        s = "REMOTE" if cache else "REMOTENOLOCAL"
        r = self.conn.execute_command(
            "VARWITH", var, s, cluster, num, "SQLREAD", *statements
        )
        return r[0], [decode(s) for s in r[1:]]

    def announce(self, cluster, loc, ttl=DEFAULT_TTL):
        return self.conn.execute_command("ANNOUNCE", cluster, loc, str(ttl)) == b"OK"

    def has_announced(self, cluster, loc):
        return self.conn.execute_command("HASANNOUNCED", cluster, loc) == 1

    def pointer_set(self, cluster, private_key, val, ttl=DEFAULT_TTL):
        return self.conn.execute_command(
            "POINTERSET", cluster, private_key, val, str(ttl)
        )

    def pointer_lookup(self, cluster, name, generation=0):
        return self.conn.execute_command(
            "POINTERLOOKUP", cluster, name, str(generation)
        )

    def iter_start(self, loc):
        ret = self.conn.execute_command("ITERSTART", loc) == b"OK"
        if ret:
            while True:
                s = r.iter_next()
                if s is None:
                    break
                else:
                    yield s

    def var_with_iter_start(self, var):
        ret = self.conn.execute_command("VARWITH", var, "ITERSTART") == b"OK"
        if ret:
            while True:
                s = r.iter_next()
                if s is None:
                    break
                else:
                    yield s

    def remote_iter_start(self, cluster, loc, num=1, cache=True):
        s = "REMOTE" if cache else "REMOTENOLOCAL"
        ret = self.conn.execute_command(s, cluster, str(num), "ITERSTART", loc) == b"OK"
        if ret:
            while True:
                s = r.iter_next()
                if s is None:
                    break
                else:
                    yield s

    def var_with_remote_iter_start(self, var, cluster, num=1, cache=True):
        s = "REMOTE" if cache else "REMOTENOLOCAL"
        ret = (
            self.conn.execute_command("VARWITH", var, s, cluster, str(num), "ITERSTART")
            == b"OK"
        )
        if ret:
            while True:
                s = r.iter_next()
                if s is None:
                    break
                else:
                    yield s

    def iter_next(self):
        ret = self.conn.execute_command("ITERNEXT")
        if ret == b"DONE":
            return None
        return decode(ret[0]), decode(ret[1])

    def iter_stop(self):
        return self.conn.execute_command("ITERSTOP") == b"OK"

    def iter_start_opts(
        self, loc, min_key=None, max_key=None, inc_min=True, inc_max=True, reverse=False
    ):
        mink, maxk, imin, imax = self._make_min_max(min_key, max_key, inc_min, inc_max)
        rev = "true" if reverse else "false"
        ret = (
            self.conn.execute_command("ITERSTART", loc, mink, maxk, imin, imax, rev)
            == b"OK"
        )
        if ret:
            while True:
                s = r.iter_next()
                if s is None:
                    break
                else:
                    yield s

    def var_with_iter_start_opts(
        self, var, min_key=None, max_key=None, inc_min=True, inc_max=True, reverse=False
    ):
        mink, maxk, imin, imax = self._make_min_max(min_key, max_key, inc_min, inc_max)
        rev = "true" if reverse else "false"
        ret = (
            self.conn.execute_command(
                "VARWITH", var, "ITERSTART", mink, maxk, imin, imax, rev
            )
            == b"OK"
        )
        if ret:
            while True:
                s = r.iter_next()
                if s is None:
                    break
                else:
                    yield s

    def remote_iter_start_opts(
        self,
        cluster,
        loc,
        min_key=None,
        max_key=None,
        inc_min=True,
        inc_max=True,
        reverse=False,
        num=1,
        cache=True,
    ):
        mink, maxk, imin, imax = self._make_min_max(min_key, max_key, inc_min, inc_max)
        rev = "true" if reverse else "false"
        s = "REMOTE" if cache else "REMOTENOLOCAL"
        ret = (
            self.conn.execute_command(
                s, cluster, str(num), "ITERSTART", loc, mink, maxk, imin, imax, rev
            )
            == b"OK"
        )
        if ret:
            while True:
                s = r.iter_next()
                if s is None:
                    break
                else:
                    yield s

    def var_with_remote_iter_start_opts(
        self,
        var,
        cluster,
        min_key=None,
        max_key=None,
        inc_min=True,
        inc_max=True,
        reverse=False,
        num=1,
        cache=True,
    ):
        mink, maxk, imin, imax = self._make_min_max(min_key, max_key, inc_min, inc_max)
        rev = "true" if reverse else "false"
        s = "REMOTE" if cache else "REMOTENOLOCAL"
        ret = (
            self.conn.execute_command(
                "VARWITH",
                var,
                s,
                cluster,
                str(num),
                "ITERSTART",
                mink,
                maxk,
                imin,
                imax,
                rev,
            )
            == b"OK"
        )
        if ret:
            while True:
                s = r.iter_next()
                if s is None:
                    break
                else:
                    yield s

    def _make_min_max(self, min_key, max_key, inc_min, inc_max):
        minkey = ""
        imin = ""
        maxkey = ""
        imax = ""
        if min_key is not None:
            minkey = encode(min_key)
            imin = "true" if inc_min else "false"

        if max_key is not None:
            maxkey = encode(min_key)
            imax = "true" if inc_max else "false"

        return minkey, maxkey, imin, imax

    def upload(self, file_obj, chunk_size=1024 * 1024):
        loc = ""
        ix = 0
        while chunk := file_obj.read(chunk_size):
            loc = r.put_multi(loc, [(ix, chunk)])
            ix += len(chunk)
        return loc

    def upload_dir(self, tree, d, chunk_size=1024 * 1024):
        files = []
        p = Path(d)
        for i in p.glob("**/*"):
            if i.is_file():
                with open(i, "rb") as f:
                    loc = self.upload(f, chunk_size)
                    files.append((str(i), (elixir.Atom(b"embedded_tree"), loc, None)))
        return r.put_multi(tree, files)

    def download(self, tree, file_obj):
        it = self.iter_start_opts(tree, min_key=0)
        self._do_download(file_obj, it)

    def download_dir(self, tree, d):
        it = self.iter_start_opts(tree, min_key=0)
        files = self._dir_files(it)
        for fn, (_, loc, _) in files:
            it = self.iter_start_opts(loc, min_key=0)
            self._download_file_in_dir(d, fn, loc, it)

    def ls(self, tree):
        it = self.iter_start_opts(tree, min_key=0)
        return [k for k, _ in self._dir_files(it)]

    def var_with_download(self, var, file_obj):
        it = self.var_with_iter_start_opts(var, min_key=0)
        self._do_download(file_obj, it)

    def remote_download(self, cluster, loc, file_obj, num=1, cache=True):
        it = self.remote_iter_start_opts(cluster, loc, min_key=0, num=num, cahce=cache)
        self._do_download(file_obj, it)

    def var_with_remote_download(self, var, cluster, file_obj, num=1, cache=True):
        it = self.var_with_iter_start_opts(
            var, cluster, min_key=0, num=num, cahce=cache
        )
        self._do_download(file_obj, it)

    def var_with_download_dir(self, var, file_obj):
        it = self.var_with_iter_start_opts(var, min_key=0)
        files = self._dir_files(it)
        for fn, (_, loc, _) in files:
            it = self.iter_start_opts(loc, min_key=0)
            self._download_file_in_dir(d, fn, loc, it)

    def remote_download_dir(self, cluster, loc, dir, num=1, cache=True):
        it = self.remote_iter_start_opts(cluster, loc, min_key=0, num=num, cahce=cache)
        files = self._dir_files(it)
        for fn, (_, loc, _) in files:
            it = self.iter_start_opts(loc, min_key=0, num=num, cahce=cache)
            self._download_file_in_dir(d, fn, loc)

    def var_with_remote_download_dir(self, var, cluster, dir, num=1, cache=True):
        it = self.var_with_iter_start_opts(
            var, cluster, min_key=0, num=num, cahce=cache
        )
        files = self._dir_files(it)
        for fn, (_, loc, _) in files:
            it = self.iter_start_opts(loc, min_key=0, num=num, cahce=cache)
            self._download_file_in_dir(d, fn, it)

    def _dir_files(self, it):
        files = []
        for s in it:
            if isinstance(s[0], bytes):
                files.append((s[0], s[1]))
        return files

    def _do_download(self, file_obj, it):
        for s in it:
            if isinstance(s[0], int) and isinstance(s[1], bytes):
                file_obj.write(s[1])

    def _download_file_in_dir(self, d, fn, it):
        real_fn = os.path.join(d, fn.decode("utf8"))
        directory = os.path.dirname(real_fn)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(real_fn, "wb") as f:
            self._do_download(f, it)

    def remote_persist(self, cluster, loc, ttl=-1, num=1, cache=True):
        s = "REMOTE" if cache else "REMOTENOLOCAL"
        return (
            self.conn.execute_command(s, cluster, str(num), "PERSIST", loc, str(ttl))
            == b"OK"
        )

    def persist(self, loc, ttl=-1):
        return self.conn.execute_command("PERSIST", loc, str(ttl)) == b"OK"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    subparser = subparsers.add_parser("keypair")
    subparser = subparsers.add_parser("cluster")
    subparser = subparsers.add_parser("node_secret")

    subparser = subparsers.add_parser("download_dir")
    subparser.add_argument("tree")
    subparser.add_argument("dir")

    parser_upload = subparsers.add_parser("upload_dir")
    parser_upload.add_argument("--tree", default=None)
    parser_upload.add_argument("dir")

    parser_upload = subparsers.add_parser("upload")
    parser_upload.add_argument("file")

    subparser = subparsers.add_parser("download")
    subparser.add_argument("tree")
    subparser.add_argument("destination")

    subparser = subparsers.add_parser("cat")
    subparser.add_argument("tree")

    subparser = subparsers.add_parser("ls")
    subparser.add_argument("tree")

    subparser = subparsers.add_parser("push")
    subparser.add_argument("cluster")
    subparser.add_argument("value")
    subparser.add_argument("--ttl", type=int, default=DEFAULT_TTL)

    subparser = subparsers.add_parser("announce")
    subparser.add_argument("cluster")
    subparser.add_argument("tree")
    subparser.add_argument("--ttl", type=int, default=DEFAULT_TTL)

    subparser = subparsers.add_parser("pointer_set")
    subparser.add_argument("cluster")
    subparser.add_argument("private_key")
    subparser.add_argument("value")
    subparser.add_argument("--ttl", type=int, default=DEFAULT_TTL)

    subparser = subparsers.add_parser("pointer_lookup")
    subparser.add_argument("cluster")
    subparser.add_argument("name")
    subparser.add_argument("--generation", type=int, default=0)

    subparser = subparsers.add_parser("compact")
    subparser.add_argument("tree")
    subparser.add_argument("--ttl", type=int, default=DEFAULT_TTL)

    subparser = subparsers.add_parser("bytes_written")
    subparser.add_argument("tree")

    subparser = subparsers.add_parser("var_set")
    subparser.add_argument("cluster")
    subparser.add_argument("key")
    subparser.add_argument("value")

    subparser = subparsers.add_parser("var_get")
    subparser.add_argument("cluster")
    subparser.add_argument("key")

    subparser = subparsers.add_parser("var_delete")
    subparser.add_argument("cluster")
    subparser.add_argument("key")

    subparser = subparsers.add_parser("put")
    subparser.add_argument("tree")
    subparser.add_argument("key")
    subparser.add_argument("value")

    subparser = subparsers.add_parser("delete")
    subparser.add_argument("tree")
    subparser.add_argument("key")

    subparser = subparsers.add_parser("has_key")
    subparser.add_argument("tree")
    subparser.add_argument("key")

    subparser = subparsers.add_parser("get")
    subparser.add_argument("tree")
    subparser.add_argument("key")

    subparser = subparsers.add_parser("remote_bytes_written")
    subparser.add_argument("cluster")
    subparser.add_argument("tree")
    subparser.add_argument("--num", type=int, default=1)
    subparser.add_argument("--cache", type=bool, default=True)

    subparser = subparsers.add_parser("remote_has_key")
    subparser.add_argument("cluster")
    subparser.add_argument("tree")
    subparser.add_argument("key")
    subparser.add_argument("--num", type=int, default=1)
    subparser.add_argument("--cache", type=bool, default=True)

    subparser = subparsers.add_parser("remote_get")
    subparser.add_argument("cluster")
    subparser.add_argument("tree")
    subparser.add_argument("key")
    subparser.add_argument("--num", type=int, default=1)
    subparser.add_argument("--cache", type=bool, default=True)

    subparser = subparsers.add_parser("var_with_bytes_written")
    subparser.add_argument("cluster")
    subparser.add_argument("var")

    subparser = subparsers.add_parser("var_with_put")
    subparser.add_argument("var")
    subparser.add_argument("key")
    subparser.add_argument("value")

    subparser = subparsers.add_parser("var_with_delete")
    subparser.add_argument("var")
    subparser.add_argument("key")

    subparser = subparsers.add_parser("var_with_get")
    subparser.add_argument("var")
    subparser.add_argument("key")

    subparser = subparsers.add_parser("var_with_has_key")
    subparser.add_argument("var")
    subparser.add_argument("key")

    subparser = subparsers.add_parser("var_with_remote_get")
    subparser.add_argument("cluster")
    subparser.add_argument("var")
    subparser.add_argument("key")
    subparser.add_argument("--num", type=int, default=1)
    subparser.add_argument("--cache", type=bool, default=True)

    subparser = subparsers.add_parser("var_with_remote_has_key")
    subparser.add_argument("cluster")
    subparser.add_argument("var")
    subparser.add_argument("key")
    subparser.add_argument("--num", type=int, default=1)
    subparser.add_argument("--cache", type=bool, default=True)

    subparser = subparsers.add_parser("var_with_remote_bytes_written")
    subparser.add_argument("cluster")
    subparser.add_argument("var")
    subparser.add_argument("--num", type=int, default=1)
    subparser.add_argument("--cache", type=bool, default=True)

    subparser = subparsers.add_parser("persist")
    subparser.add_argument("tree")
    subparser.add_argument("--ttl", type=int, default=-1)

    subparser = subparsers.add_parser("remote_persist")
    subparser.add_argument("cluster")
    subparser.add_argument("tree")
    subparser.add_argument("--num", type=int, default=1)
    subparser.add_argument("--cache", type=bool, default=True)
    subparser.add_argument("--ttl", type=int, default=-1)

    args = parser.parse_args()

    r = CrissCross()

    if args.command == "upload_dir":
        ret = r.upload_dir(read_var(args.tree), args.dir)
        print_ret(ret)
    elif args.command == "download_dir":
        r.download_dir(read_var(args.tree), args.dir)
    elif args.command == "upload":
        with open(args.file, "rb") as f:
            ret = r.upload(f)
        print_ret(ret)
    elif args.command == "download":
        with open(args.destination, "wb") as f:
            r.download(read_var(args.tree), f)
    elif args.command == "cat":
        r.download(read_var(args.tree), sys.stdout.buffer)
    elif args.command == "ls":
        for f in r.ls(read_var(args.tree)):
            print(f.decode("utf8"))
    elif args.command == "announce":
        r.announce(read_var(args.cluster), read_var(args.tree), args.ttl)
    elif args.command == "has_announced":
        print(r.has_announced(read_var(args.cluster), read_var(args.tree)))
    elif args.command == "pointer_set":
        ret = r.pointer_set(
            read_var(args.cluster),
            read_var(args.private_key),
            read_var(args.value),
            args.ttl,
        )
        print_ret(ret)
    elif args.command == "pointer_lookup":
        ret = r.pointer_lookup(
            read_var(args.cluster), read_var(args.name), args.generation
        )
        print_ret(ret)
    elif args.command == "var_set":
        ret = r.var_set(args.key, read_var(args.value))
        print_ret(ret)
    elif args.command == "var_get":
        ret = r.var_get(read_var(args.key))
        print_ret(ret)
    elif args.command == "var_delete":
        ret = r.var_delete(read_var(args.key))
    elif args.command == "put":
        ret = r.put_multi_bin(read_var(args.tree), [(args.key, args.value)])
        print_ret(ret)
    elif args.command == "delete":
        ret = r.delete_multi_bin(read_var(args.tree), [args.key])
        print_ret(ret)
    elif args.command == "get":
        print_get(r.get_multi_bin(read_var(args.tree), [args.key]))
    elif args.command == "has_key":
        print(r.has_key_bin(read_var(args.tree), args.key))
    elif args.command == "remote_get":
        print_get(
            r.remote_get_multi_bin(
                read_var(args.cluster),
                read_var(args.tree),
                [args.key],
                num=args.num,
                cache=args.cache,
            )
        )
    elif args.command == "remote_has_key":
        print(
            r.remote_has_key_bin(
                read_var(args.cluster),
                read_var(args.tree),
                args.key,
                num=args.num,
                cache=args.cache,
            )
        )
    elif args.command == "var_with_put":
        r.var_with_put_bin(args.var, [(args.key, args.value)])
    elif args.command == "var_with_delete":
        r.var_with_delete_multi_bin(args.var, [args.key])
    elif args.command == "var_with_get":
        print_get(r.var_with_get_multi_bin(args.var, [args.key]))
    elif args.command == "var_with_has_key":
        print(r.var_with_has_key_bin(args.var, args.key))
    elif args.command == "var_with_remote_get":
        print_get(
            r.var_with_remote_get_multi_bin(
                args.var,
                read_var(args.cluster),
                [args.key],
                num=args.num,
                cache=args.cache,
            )
        )
    elif args.command == "var_with_remote_has_key":
        print(
            r.var_with_remote_has_key_bin(
                args.var, args.key, num=args.num, cache=args.cache
            )
        )
    elif args.command == "compact":
        ret = r.compact(read_var(args.tree), args.ttl)
        print(f"NewHash: {base58.b58encode(ret[0]).decode('utf8')}")
        print(f"NewSize: {ret[1]} bytes")
        print(f"OldSize: {ret[2]} bytes")

    elif args.command == "bytes_written":
        print(r.bytes_written(read_var(args.tree)))

    elif args.command == "var_with_bytes_written":
        print(r.var_with_bytes_written(read_var(args.var)))

    elif args.command == "remote_bytes_written":
        print(
            r.remote_bytes_written(
                read_var(args.cluster), args.tree, num=args.num, cache=args.cache
            )
        )
    elif args.command == "var_with_remote_bytes_written":
        print(r.var_with_remote_bytes_written(args.var, num=args.num, cache=args.cache))

    elif args.command == "keypair":
        ret = r.keypair()
        print(f"Name:       {base58.b58encode(ret[0]).decode('utf8')}")
        print(f"PublicKey:  {base58.b58encode(ret[1]).decode('utf8')}")
        print(f"PrivateKey: {base58.b58encode(ret[2]).decode('utf8')}")
    elif args.command == "cluster":
        ret = r.cluster()
        print(f"Name:       {base58.b58encode(ret[0]).decode('utf8')}")
        print(f"Cypher:     {base58.b58encode(ret[1]).decode('utf8')}")
        print(f"PublicKey:  {base58.b58encode(ret[2]).decode('utf8')}")
        print(f"PrivateKey: {base58.b58encode(ret[3]).decode('utf8')}")
        print(f"MaxTTL:     {DEFAULT_TTL}")
    elif args.command == "node_secret":
        ret = r.keypair()
        print(base58.b58encode(ret[2]).decode("utf8"))
    elif args.command == "push":
        print(
            r.push(
                read_var(args.cluster),
                read_var(args.value),
                ttl=args.ttl,
            )
        )
    elif args.command == "persist":
        print_get(r.persist(read_var(args.tree), ttl=args.ttl))

    elif args.command == "remote_persist":
        print_get(
            r.remote_persist(
                read_var(args.cluster),
                read_var(args.tree),
                ttl=args.ttl,
                num=args.num,
                cache=args.cache,
            )
        )
