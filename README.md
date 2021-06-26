# twarc-network 

twarc-network builds a reply, quote and retweet network from a file of
tweets that you've collected using twarc. It will write out the network as
a [gexf], [dot], json or html file. It uses [networkx] for the graph
model, [pydotplus] for dot output, and [d3] for the html presentation.

To install you will need to:

    pip3 install twarc-network

You will need to collect some data with [twarc]:

    twarc2 search blacklivesmatter > tweets.jsonl

Then you can create the default HTML visualization:

    twarc2 network tweets.jsonl network.html

or dot:

    twarc2 tweets.jsonl --format dot network.dot

or gexf:

    twarc2 network tweets.jsonl --format gexf network.gexf

or json:

    twarc2 network tweets.jsonl --format json network.json

If you would rather have the network oriented around nodes that are tweets
instead of users:

    twarc2 network tweets.jsonl --nodes tweets network.html

If you would rather have the network oriented around nodes that are
hashtags:

    twarc2 network tweets.jsonl --nodes hashtags > network.html

[gexf]: https://gephi.org/gexf/format/
[dot]: https://en.wikipedia.org/wiki/DOT_%28graph_description_language%29
[d3]: https://d3js.org/
[networkx]: https://networkx.org/
[twarc]: https://github.com/docnow/twarc
