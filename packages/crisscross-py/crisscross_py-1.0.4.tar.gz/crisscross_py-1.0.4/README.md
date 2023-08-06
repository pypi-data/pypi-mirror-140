# crisscross_py
Python Client for CrissCross Network

## CrissCross - Like IPFS... but with Redis Protocol, a SQL Layer, privacy and distribution as well as file downloads

CrissCross is a new way to share immutable structures. Build a tree, get a hash and distribute it in your own private cluster. Connect with any language that has a redis client.

# This package

Client to access a Node on the CrissCross network: [https://github.com/SoCal-Software-Labs/CrissCross](https://github.com/SoCal-Software-Labs/CrissCross)

# Usage

Follow the instructions on how to setup a CrissCross node: [https://github.com/SoCal-Software-Labs/CrissCross](https://github.com/SoCal-Software-Labs/CrissCross)

Install the client:

```bash
pip install crisscross-py
```

# Tour

With CrissCross, you insert values into a hash and get a new hash back. To start a new tree, insert into an empty hash:

#### Bash

```bash 
$ MYVAR=$(crisscross put "" "hello" "world")
# In the bash you get the Base58 Representation
$ echo $MYVAR
E555NKZfKRoUc5F62desomHFaQRz6tinAmehCbymudhv
$ crisscross get $MYVAR "hello"
world
```

#### Python

You can access the tree programmatically with Python (or any Redis client):

```python 
>>> client = CrissCross()
>>> location = client.put_multi("", [("hello", "world")])
# In the python client you manipulate the raw hash bytes, not the Base58 Representation
>>> location
b"\xc22\xdcz'\x8c\xa0\xc9}Y;\xbe\x1bD4<G6@?\x95\xc1k\x05{\x18\xc4\xc9\xbb\xba\xa65"
>>> base58.b58encode(location)
b'E555NKZfKRoUc5F62desomHFaQRz6tinAmehCbymudhv'
>>> client.get_multi(location, ["hello"])
{b"hello": b"world"}
``````
With python you can store arbitrary data... tuples, lists, dictionaries, booleans, integers, floats and atoms. Not just binary text:

```python 
>>> location = client.put_multi("", [(("wow", 1.2), {1: (True, None)})])
>>> client.get_multi(location, [("wow", 1.2)])
{1: (True, None)}
``````

## Updates

Update a tree by referencing the hash of its previous state:

#### Python

```python 
>> new_location = client.put_multi(location, [("cool", 12345)])
b"HfTbW1XjXdT8RbQ7CMJnD2P73RHe3PJvSiPAFNj6Zzhp"
>> client.get(new_location, "cool")
12345
``````

#### Bash

```bash 
$ crisscross put $MYVAR "hello2" "world2"
47ZGfGj7V3M4HLUirhWWXD7sxD2sciro5YwSBnLinXXp
```

## Clone and Share Trees

Once you have a hash, you can share it on the network and others can clone it from you:

```bash
# On one machine
$ crisscross announce ^defaultcluster 47ZGfGj7V3M4HLUirhWWXD7sxD2sciro5YwSBnLinXXp
47ZGfGj7V3M4HLUirhWWXD7sxD2sciro5YwSBnLinXXp
```

```bash
# On other machine query the tree without fully downloading it
$ crisscross remote_get ^defaultcluster 47ZGfGj7V3M4HLUirhWWXD7sxD2sciro5YwSBnLinXXp "hello2"
"world2"
# They can clone the tree to get a local copy
$ crisscross remote_clone ^defaultcluster 47ZGfGj7V3M4HLUirhWWXD7sxD2sciro5YwSBnLinXXp
True
$ crisscross get 47ZGfGj7V3M4HLUirhWWXD7sxD2sciro5YwSBnLinXXp "hello"
"world"
```
## SQL Engine

From Python or Redis you can access the SQL engine. Currently its rather limited (no ALTER TABLE staments and no INDEX support). Those things are supported by the engine ([GlueSQL](https://github.com/gluesql/gluesql)) however are not currently connected to the storage layer and need to be hooked up.


```python
>> client = CrissCross()
>>> location, ret = client.sql("", "CREATE TABLE MyCrissCrossTable (id INTEGER);")
>>> print(ret) # Get the result of the execution
[(Atom(b'ok'), b'Create')]
>>> location2, _ = client.sql(location, "INSERT INTO MyCrissCrossTable VALUES (100);")
>>> location3, _ = client.sql(location2, "INSERT INTO MyCrissCrossTable VALUES (200);")
>>> loc, ret = client.sql(location3, "SELECT * FROM MyCrissCrossTable WHERE id > 100;")
>>> print(ret[0][1])
{b'Select': {b'labels': [b'id'], b'rows': [[{b'I64': 200}]]}}
```
Execute many statements at once:

```python
>>> location, sqlreturns = client.sql("", "CREATE TABLE MyCrissCrossTable (id INTEGER);", "INSERT INTO MyCrissCrossTable VALUES (100);", "INSERT INTO MyCrissCrossTable VALUES (200);", "SELECT * FROM MyCrissCrossTable WHERE id > 100;")
>>> print(sqlreturns)
[(Atom(b'ok'), b'Create'), (Atom(b'ok'), {b'Insert': 1}), (Atom(b'ok'), {b'Insert': 1}), (Atom(b'ok'), {b'Select': {b'labels': [b'id'], b'rows': [[{b'I64': 200}]]}})]
```


## Jobs

Build a job server.

#### Server

```python
tree, public, priv = client.keypair()
client.job_announce(read_var("^defaultcluster"), tree)
while True:
    method, arg, ref = r.job_get(tree)
    arg = arg + 1
    client.job_respond(ref, arg, tree)
```

#### Client
```python
resp = client.remote_job_do(read_var("^defaultcluster"), tree, "method", 42)
print(resp)
print(client.job_verify(tree, "method", 42, resp[0], resp[1], public))
```