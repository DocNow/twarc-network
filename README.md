# twarc-network 

<img style="float: left; height: 300px;" src="https://raw.githubusercontent.com/docnow/twarc-network/main/images/d3.png" />

twarc-network builds a reply, quote and retweet network from a file of
tweets that you've collected using twarc. It will write out the network as
a [gexf], [dot], json or html file. It uses [networkx] for the graph
model, [pydotplus] for dot output, and [d3] for the html presentation. 

If you know CSS you can look at the generated HTML file and modify the style to
suit your needs. If you come up with a more pleasing representation please send
a pull request. Exporting as a GEXF or GML file will allow you to import the
data into Gephi or Cytoscape for further analysis and visualization.

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

If you would rather have the network oriented around nodes that are tweets
instead of users:

    twarc2 network tweets.jsonl --nodes tweets network.html

If you would rather have the network oriented around nodes that are
hashtags:

    twarc2 network tweets.jsonl --nodes hashtags > network.html

## Subgraph Sizes

Depending on the data you are analyzing it can be helpful to remove subgraphs in
the graph that are smaller than some number. For example if you don't want to
visualize networks where two nodes are only connected to each other and not
anyone else you can:

    twarc2 network tweets.jsonl tweets.html --min-subgraph-size 3

It's less common but you can also remove nodes that are part of too large
subgraphs. For example if you wanted to remove any clusters of nodes that were
larger than 10:

    twarc2 network tweets.jsonl tweets.html --maxsubgraph-size 10

[gexf]: https://gephi.org/gexf/format/
[dot]: https://en.wikipedia.org/wiki/DOT_%28graph_description_language%29
[d3]: https://d3js.org/
[networkx]: https://networkx.org/
[twarc]: https://github.com/docnow/twarc
[gml]: https://en.wikipedia.org/wiki/Graph_Modelling_Language
