import os
from crisscross import read_var, CrissCross


tree = read_var("*./keys/my_var.yaml#Name")
cluster = read_var("^defaultcluster")
if os.getenv("READ"):
    reader = CrissCross(host=host, port=port, **kwargs)
    writer = CrissCross(host=host, port=port, **kwargs)

    stream_ref = writer.remote_stream_start(cluster, tree)

    pubsub = reader.pubsub_streams()
    pubsub.subsribe_to_stream(stream_ref)
    listener = pubsub.listen()

    writer.stream_send(stream_ref, "hello", ("world", 2))
    writer.stream_send(stream_ref, "hello", ("world", 2))
    for response in listener:
        print(response)
        writer.stream_send(stream_ref, "hello", ("world", 2))
else:
    reader = CrissCross(host=host, port=port, **kwargs)
    writer = CrissCross(host=host, port=port, **kwargs)
    writer.job_announce(cluster, tree)
    pubsub = reader.pubsub_jobs()
    pubsub.subscribe_to_job(tree)

    for (tree, method, argument, ref) in pubsub.listen():
        print((tree, method, argument))
        writer.job_respond(ref, "pingpong", tree)
