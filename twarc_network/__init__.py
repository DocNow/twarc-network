import io
import json
import time
import click
import pydot
import networkx
import itertools

from pathlib import Path
from networkx import nx_pydot

from twarc import ensure_flattened


@click.command()
@click.option(
    "--format",
    type=click.Choice(
        ["html", "json", "gexf", "dot", "csv", "gml"], case_sensitive=False
    ),
    default="html",
    help="Output format for the network",
)
@click.option(
    "--nodes",
    type=click.Choice(["users", "tweets", "hashtags"]),
    default="users",
    help="What type of nodes to use in the network",
)
@click.option("--min-subgraph-size", type=int, help="Minimum subgraph size to include")
@click.option("--max-subgraph-size", type=int, help="Maximum subgraph size to include")
@click.argument("infile", type=click.File("r"), default="-")
@click.argument("outfile", type=click.File("w"), default="-")
def network(format, nodes, infile, outfile, min_subgraph_size, max_subgraph_size):
    """
    Generates a network graph of tweets as GEXF, GML, DOT, JSON, HTML, CSV.
    """

    # unfortunately it's not possible to use connected_component_subgraphs
    # with directed graphs, so if the user wants to limit subgraph size
    # we will need to use a regular graph and not a directed graph

    if min_subgraph_size or max_subgraph_size:
        g = get_graph(infile, nodes, digraph=False)
    else:
        g = get_graph(infile, nodes, digraph=True)

    # if the user wants to limit subgraph min/max sizes
    if min_subgraph_size or max_subgraph_size:
        g_copy = g.copy()
        for components in networkx.connected_components(g):
            sg = g.subgraph(components)
            # for sg in networkx.connected_component_subgraphs(G):
            if min_subgraph_size and len(sg) < min_subgraph_size:
                g_copy.remove_nodes_from(sg.nodes())
            elif max_subgraph_size and len(sg) > max_subgraph_size:
                g_copy.remove_nodes_from(sg.nodes())
        g = g_copy

    if format == "gexf":
        outfile.write(nxstr(networkx.write_gexf, g))

    elif format == "gml":
        outfile.write(nxstr(networkx.write_gml, g))

    elif format == "dot":
        nx_pydot.write_dot(g, outfile)

    elif format == "json":
        json.dump(to_json(g), outfile, indent=2)

    elif format == "csv":
        outfile.write(nxstr(networkx.write_edgelist, g, delimiter=","))

    elif format == "html":
        graph_data = json.dumps(to_json(g), indent=2)
        html_file = Path(__file__).parent / "index.html"
        html = html_file.open().read()
        html = html.replace("__GRAPH_DATA__", graph_data)
        outfile.write(html)


def get_graph(infile, nodes_type, digraph=True):
    if digraph:
        g = networkx.DiGraph()
    else:
        g = networkx.Graph()

    for line in infile:
        for t in ensure_flattened(json.loads(line)):

            from_id = t["id"]

            from_user = t["author"]["username"]
            from_user_id = t["author"]["id"]

            to_user = None
            to_id = None
            edge_type = None

            created_at_date = time.strftime(
                "%d/%m/%Y %H:%M:%S",
                time.strptime(t["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            )

            # get referenced tweets but ignore ones that have been deleted and
            # have no author stanza
            refs = filter(lambda r: "author" in r, t.get("referenced_tweets", []))

            if nodes_type == "users":
                for ref in refs:
                    to_user = ref["author"]["username"]
                    edge_type = get_edge_type(ref)
                    add(
                        g,
                        nodes_type,
                        from_user,
                        from_id,
                        to_user,
                        None,
                        edge_type,
                        created_at_date,
                    )

            elif nodes_type == "tweets":
                for ref in refs:
                    to_id = ref["id"]
                    to_user = ref["author"]["username"]
                    edge_type = get_edge_type(ref)
                    add(
                        g,
                        nodes_type,
                        from_user,
                        from_id,
                        to_user,
                        to_id,
                        edge_type,
                        created_at_date,
                    )

            elif nodes_type == "hashtags":

                # some tweets apparently lack an entities stanza?
                if "entities" not in t:
                    continue

                hashtags = map(lambda h: h["tag"], t["entities"].get("hashtags", []))
                # list of all possible hashtag pairs
                hashtag_pairs = itertools.combinations(hashtags, 2)
                for ht1, ht2 in hashtag_pairs:
                    add(
                        g,
                        nodes_type,
                        "#" + ht1,
                        None,
                        "#" + ht2,
                        None,
                        "hashtag",
                        created_at_date,
                    )

            else:
                raise Exception(f"Unkown node type: {nodes_type}")

    return g


def add(g, nodes_type, from_user, from_id, to_user, to_id, edge_type, created_at=None):

    # storing start_date will allow for timestamps for gephi timeline, where nodes
    # will appear on screen at their start date and stay on forever after

    if nodes_type in ["users", "hashtags"] and to_user:
        g.add_node(from_user, screen_name=from_user, start_date=created_at)
        g.add_node(to_user, screen_name=to_user, start_date=created_at)

        if g.has_edge(from_user, to_user):
            weight = g[from_user][to_user]["weight"] + 1
        else:
            weight = 1
        g.add_edge(from_user, to_user, type=edge_type, weight=weight)

    elif nodes_type == "tweets" and to_id:
        g.add_node(from_id, screen_name=from_user)
        if to_user:
            g.add_node(to_id, screen_name=to_user)
        else:
            g.add_node(to_id)
        g.add_edge(from_id, to_id, type=edge_type)


def to_json(g):
    j = {"nodes": [], "links": []}
    for node_id, node_attrs in g.nodes(True):
        j["nodes"].append(
            {
                "id": node_id,
                "type": node_attrs.get("type"),
                "screen_name": node_attrs.get("screen_name"),
            }
        )
    for source, target, attrs in g.edges(data=True):
        j["links"].append(
            {"source": source, "target": target, "type": attrs.get("type")}
        )
    return j


def get_edge_type(ref):
    if ref["type"] == "retweeted":
        return "retweet"
    elif ref["type"] == "replied_to":
        return "reply"
    elif ref["type"] == "quoted":
        return "quote"
    else:
        raise Exception(f'unknown reference type: {ref["type"]}')


def nxstr(f, *args, **kwargs):
    # networkx output functions want to write to a file as bytes
    # but click.File is expecting a string. This function takes the
    # networkx function and parameters and writes the bytes to a
    # BytesIO object to return it as a string.
    out = io.BytesIO()
    args = args + (out,)
    f(*args, **kwargs)
    return out.getvalue().decode("utf-8")
