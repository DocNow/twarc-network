import io
import re
import csv
import json
import pydot

from twarc_network import network
from click.testing import CliRunner

runner = CliRunner()


def test_html():
    result = runner.invoke(network, ["test-data/tweets.jsonl"])
    assert result.exit_code == 0
    m = re.search(r"var graph = ({.*});.*var link = ", result.output, re.DOTALL)
    assert m
    graph = json.loads(m.group(1))
    assert len(graph["nodes"]) == 484
    assert len(graph["links"]) == 391


def test_json():
    result = runner.invoke(network, ["test-data/tweets.jsonl", "--format", "json"])
    assert result.exit_code == 0
    graph = json.loads(result.output)
    assert len(graph["nodes"]) == 484
    assert len(graph["links"]) == 391


def test_gexf():
    result = runner.invoke(network, ["test-data/tweets.jsonl", "--format", "gexf"])
    assert result.exit_code == 0


def test_gexf():
    result = runner.invoke(network, ["test-data/tweets.jsonl", "--format", "gml"])
    assert result.exit_code == 0


def test_dot():
    result = runner.invoke(network, ["test-data/tweets.jsonl", "--format", "dot"])
    assert result.exit_code == 0
    graphs = pydot.graph_from_dot_data(result.output)
    assert len(graphs) == 1
    graph = graphs[0]
    assert len(graph.get_node_list()) == 485
    assert len(graph.get_edge_list()) == 391


def test_csv():
    result = runner.invoke(network, ["test-data/tweets.jsonl", "--format", "csv"])
    assert result.exit_code == 0
    data = csv.reader(io.StringIO(result.output))
    count = 0
    for row in data:
        count += 1
    assert count == 391


def test_min_component():
    result = runner.invoke(
        network,
        ["test-data/tweets.jsonl", "--format", "json", "--min-component-size", "4"],
    )
    graph = json.loads(result.output)
    assert len(graph["nodes"]) == 285


def test_max_component():
    result = runner.invoke(
        network,
        ["test-data/tweets.jsonl", "--format", "json", "--max-component-size", "15"],
    )
    graph = json.loads(result.output)
    assert len(graph["nodes"]) == 313


def test_tweets():
    result = runner.invoke(
        network, ["test-data/tweets.jsonl", "--format", "json", "--nodes", "tweets"]
    )
    assert result.exit_code == 0
    graph = json.loads(result.output)
    assert len(graph["nodes"]) == 613


def test_hashtags():
    result = runner.invoke(
        network, ["test-data/tweets.jsonl", "--format", "json", "--nodes", "hashtags"]
    )
    assert result.exit_code == 0
    graph = json.loads(result.output)
    assert len(graph["nodes"]) == 383
