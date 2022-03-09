# twarc-network 

<img height=300 src="https://raw.githubusercontent.com/docnow/twarc-network/main/images/d3.png" />

[![Build Status](https://github.com/docnow/twarc-network/workflows/tests/badge.svg)](https://github.com/DocNow/twarc-network/actions/workflows/main.yml)

*twarc-network* builds a reply, quote, retweet and mention network from a file of tweets
that you've collected using twarc. It will write out the network as a [gexf],
[gml], [dot], json, csv or html file. It uses [networkx] for the graph model,
[pydot] for dot output, and [d3] for the html presentation. 

If you know CSS you can hack at the generated HTML file to modify the style to
suit your needs. If you come up with a more pleasing representation please send
a pull request! Exporting as a gexf, gml or dot file will allow you to import
the data into tools like [Gephi], [Cytoscape] and [GraphViz] for further
analysis and visualization.

## Install

To install you will need to:

    pip3 install twarc-network

## Collect Data

First you will need to collect some data with [twarc]:

    twarc2 search blacklivesmatter > tweets.jsonl

## Output Formats

Once you've got some data you can create the default D3 HTML visualization:

    twarc2 network tweets.jsonl network.html

or [dot]:

    twarc2 tweets.jsonl --format dot network.dot

or [gexf]:

    twarc2 network tweets.jsonl --format gexf network.gexf

or [gml]:

    twarc2 network tweets.jsonl --format gml network.gml

or json:

    twarc2 network tweets.jsonl --format json network.json

or CSV edge list:

    twarc2 network tweets.jsonl --format csv network.csv

## Changing the Nodes

Tweets can be connected together as replies, quotes and retweets. If you would
like to see the network oriented around nodes that are tweets instead of users
you can:

    twarc2 network tweets.jsonl --nodes tweets network.html

Hashtags can can be connected when they are used together in a tweet. So you
can visualize a network where nodes are hashtags:

    twarc2 network tweets.jsonl --nodes hashtags > network.html

## Changing the Edges

By default, when user and tweet graphs are built,
all types of interactions are used as edges:
Retweet, reply or quote in the case of tweets;
retweet, reply, quote or mention in the case of users.
But you can also limit the types considered.
For example, if you only want retweet edges, you can:

    twarc2 network tweets.jsonl tweets.html --edges retweet

Or if you only want replies and quotes, you can:

    twarc2 network tweets.jsonl tweets.html --edges reply --edges quote

## Component Sizes

Depending on the data you are analyzing it can be helpful to remove weakly connected components in
the graph that are smaller than some number. For example if you don't want to
visualize networks where two nodes are only connected to each other and not
anyone else you can:

    twarc2 network tweets.jsonl tweets.html --min-component-size 3

It's less common but you can also remove nodes that are part of too large
subgraphs. For example if you wanted to remove any components that were
larger than 10:

    twarc2 network tweets.jsonl tweets.html --max-component-size 10

## Attributes

The possible node attributes are the following:
- `screen_name`:
  When the node is a user, its username.
  When the node is a tweet, the username of its author.
- `user_id`:
  When the node is a user, its id.
  When the node is a tweet, the id of its author.
- `start_date`:
  The date of the first interaction that made the node appear in the graph.
  For example, if the node is a retweet, it is its date of creation.
  Or if the node is an original tweet,
  it is the date of the first retweet, reply or quote.
  The format is `dd/mm/yyyy hh:mm:ss`.

The possible edge attributes are the following:
- `type`: When the nodes are tweets, one of the following values:
  `retweet`, `reply` or `quote`.
- `retweet`: When the nodes are users,
  the number of retweets the source has made to the target.
- `reply`: When the nodes are users,
  the number of replies the source has made to the target.
- `quote`: When the nodes are users,
  the number of quotes the source has made to the target.
- `mention`: When the nodes are users,
  the number of mentions the source has made to the target.
- `weight`:
  When the nodes are users, the sum of `retweet`, `reply`, `quote` and `mention`.
  When the nodes are hashtags,
  the number of tweets that contained both hashtags.

[gexf]: https://gephi.org/gexf/format/
[dot]: https://en.wikipedia.org/wiki/DOT_%28graph_description_language%29
[d3]: https://d3js.org/
[networkx]: https://networkx.org/
[twarc]: https://github.com/docnow/twarc
[gml]: https://en.wikipedia.org/wiki/Graph_Modelling_Language
[pydot]: https://pypi.org/project/pydot/
[Gephi]: https://gephi.org/
[Cytoscape]: https://cytoscape.org/
[GraphViz]: https://graphviz.org/
