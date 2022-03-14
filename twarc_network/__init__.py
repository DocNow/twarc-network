import io
import json
import time
import click
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
@click.option(
    "--edges",
    type=click.Choice(["retweet", "reply", "quote", "mention"]),
    multiple=True,
    default=["retweet", "reply", "quote", "mention"],
    help="What type of edges to use in the network",
)
@click.option("--min-component-size", type=int, help="Minimum weakly connected component size to include")
@click.option("--max-component-size", type=int, help="Maximum weakly connected component size to include")
@click.argument("infile", type=click.File("r"), default="-")
@click.argument("outfile", type=click.File("w"), default="-")
def network(format, nodes, edges, infile, outfile, min_component_size, max_component_size):
    """
    Generates a network graph of tweets as GEXF, GML, DOT, JSON, HTML, CSV.
    """

    g = get_graph(infile, nodes, edges)

    # if the user wants to limit component min/max sizes
    if min_component_size or max_component_size:
        g_copy = g.copy()
        for components in networkx.weakly_connected_components(g):
            sg = g.subgraph(components)
            if min_component_size and len(sg) < min_component_size:
                g_copy.remove_nodes_from(sg.nodes())
            elif max_component_size and len(sg) > max_component_size:
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


def get_graph(infile, nodes_type, edge_types):
    g = networkx.DiGraph()

    for line in infile:
        for t in ensure_flattened(json.loads(line)):

            from_id = t["id"]

            from_user = t["author"]["username"]
            from_user_id = t["author"]["id"]

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
                    to_user_id = ref["author"]["id"]
                    edge_type = get_edge_type(ref)
                    if edge_type in edge_types:
                        add_user_edge(
                            g,
                            from_user,
                            from_user_id,
                            to_user,
                            to_user_id,
                            edge_type,
                            created_at_date,
                            edge_types,
                        )
                if "mention" in edge_types:
                    mentions = t.get("entities", dict()).get("mentions", [])
                    if is_first_mention_a_retweet(t):
                        mentions = mentions[1:]
                    for mention in mentions:
                        to_user = mention["username"]
                        to_user_id = mention["id"]
                        add_user_edge(
                            g,
                            from_user,
                            from_user_id,
                            to_user,
                            to_user_id,
                            "mention",
                            created_at_date,
                            edge_types,
                        )

            elif nodes_type == "tweets":
                for ref in refs:
                    to_id = ref["id"]
                    to_user = ref["author"]["username"]
                    to_user_id = ref["author"]["id"]
                    edge_type = get_edge_type(ref)
                    if edge_type in edge_types:
                        add_tweet_edge(
                            g,
                            from_user,
                            from_user_id,
                            from_id,
                            to_user,
                            to_user_id,
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
                    add_hashtag_edge(
                        g,
                        "#" + ht1,
                        "#" + ht2,
                        created_at_date,
                    )

            else:
                raise Exception(f"Unkown node type: {nodes_type}")

    return g


def add_user_edge(g, from_user, from_user_id, to_user, to_user_id, edge_type,
                  created_at, edge_types):

    # storing start_date will allow for timestamps for gephi timeline, where nodes
    # will appear on screen at their start date and stay on forever after

    g.add_node(
        from_user,
        screen_name=from_user,
        user_id=from_user_id,
        start_date=created_at,
    )
    g.add_node(
        to_user,
        screen_name=to_user,
        user_id=to_user_id,
        start_date=created_at,
    )

    if g.has_edge(from_user, to_user):
        weights = g[from_user][to_user]
    else:
        g.add_edge(from_user, to_user)
        weights = {t: 0 for t in ("weight", ) + edge_types}
    weights["weight"]  += 1
    weights[edge_type] += 1
    g[from_user][to_user].update(weights)


def add_tweet_edge(g, from_user, from_user_id, from_id, to_user, to_user_id,
                   to_id, edge_type, created_at):
    g.add_node(
        from_id,
        screen_name=from_user,
        user_id=from_user_id,
        start_date=created_at,
    )
    g.add_node(
        to_id,
        screen_name=to_user,
        user_id=to_user_id,
        start_date=created_at,
    )

    g.add_edge(from_id, to_id, type=edge_type)


def add_hashtag_edge(g, from_hashtag, to_hashtag, created_at):
    g.add_node(from_hashtag, start_date=created_at)
    g.add_node(to_hashtag, start_date=created_at)

    if g.has_edge(from_hashtag, to_hashtag):
        weight = g[from_hashtag][to_hashtag]["weight"] + 1
    else:
        weight = 1
    g.add_edge(from_hashtag, to_hashtag, weight=weight)


def to_json(g):
    j = {"nodes": [], "links": []}
    for node_id, attrs in g.nodes(data=True):
        node = {"id": node_id}
        node.update(attrs)
        j["nodes"].append(node)
    for source, target, attrs in g.edges(data=True):
        link = {"source": source, "target": target}
        link.update(attrs)
        j["links"].append(link)
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


def is_first_mention_a_retweet(tweet):
    if "referenced_tweets" not in tweet:
        return False
    if get_edge_type(tweet["referenced_tweets"][0]) != "retweet":
        return False

    if "entities" not in tweet or "mentions" not in tweet["entities"]:
        return False
    if tweet["entities"]["mentions"][0]["start"] != 3:
        return False

    return True


def nxstr(f, *args, **kwargs):
    # networkx output functions want to write to a file as bytes
    # but click.File is expecting a string. This function takes the
    # networkx function and parameters and writes the bytes to a
    # BytesIO object to return it as a string.
    out = io.BytesIO()
    args = args + (out,)
    f(*args, **kwargs)
    return out.getvalue().decode("utf-8")
