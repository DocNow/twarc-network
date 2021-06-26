from twarc_ids import ids
from click.testing import CliRunner

runner = CliRunner()

def test_v1():
    result = runner.invoke(newtork, ['test-data/tweets.jsonl'])
    assert result.exit_code == 0
    assert result.output == '1366587408960147459\n'
