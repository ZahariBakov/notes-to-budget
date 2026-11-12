import pytest

from notes_to_budget import __version__
from notes_to_budget.command_line.main import main


def test_version_option_prints_the_program_name_and_version(capsys):
    with pytest.raises(SystemExit) as program_exit:
        main(["--version"])

    assert program_exit.value.code == 0
    assert capsys.readouterr().out.strip() == f"notes-to-budget {__version__}"


def test_running_without_arguments_shows_help_and_succeeds(capsys):
    exit_code = main([])

    assert exit_code == 0
    assert "notes-to-budget" in capsys.readouterr().out
