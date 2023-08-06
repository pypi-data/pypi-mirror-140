import os
from crisscross import read_var, CrissCross

token = os.getenv("TUNNEL_TOKEN")
name = read_var("*./keys/my_var.yaml#Name")
cluster = read_var("^defaultcluster")
if os.getenv("READ"):
    writer = CrissCross(host=host, port=port, **kwargs)

    writer.tunnel_close(7777)  # Close any previously opened ports
    writer.tunnel_open(cluster, name, 7777, "www.httpbin.org", 80)

else:
    writer = CrissCross(host=host, port=port, **kwargs)
    writer.job_announce(cluster, name)
    writer.tunnel_allow(token, cluster, name, "www.httpbin.org", 80)
