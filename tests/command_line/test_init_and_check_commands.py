from notes_to_budget.command_line.main import main
from notes_to_budget.configuration.data_folder import DATA_FOLDER_ENVIRONMENT_VARIABLE


def test_init_creates_a_data_folder_and_says_so_in_bulgarian(tmp_path, capsys):
    new_folder = tmp_path / "my-budget"

    exit_code = main(["init", str(new_folder), "--language", "bg"])

    printed = capsys.readouterr().out
    assert exit_code == 0
    assert (new_folder / "config" / "categories.yaml").is_file()
    assert (new_folder / "Записки").is_dir()
    assert "Папката с твоите данни е създадена" in printed
    assert "Следващи стъпки" in printed


def test_init_uses_english_unless_told_otherwise(tmp_path, capsys):
    exit_code = main(["init", str(tmp_path / "my-budget")])

    assert exit_code == 0
    assert (tmp_path / "my-budget" / "notes").is_dir()
    assert "Created your data folder" in capsys.readouterr().out


def test_init_refuses_to_overwrite_existing_settings(tmp_path, capsys):
    main(["init", str(tmp_path), "--language", "bg"])
    capsys.readouterr()

    exit_code = main(["init", str(tmp_path), "--language", "bg"])

    printed = capsys.readouterr()
    assert exit_code == 1
    assert "вече има настройки" in printed.err
    assert printed.out == ""


def test_check_describes_valid_settings_in_their_own_language(tmp_path, capsys):
    main(["init", str(tmp_path), "--language", "bg"])
    capsys.readouterr()

    exit_code = main(["check", "--data-folder", str(tmp_path)])

    printed = capsys.readouterr().out
    assert exit_code == 0
    assert "са наред" in printed
    assert "Категории за разходи: 23 в 6 групи" in printed
    assert "Р  Онлайн портфейл  (сверява се с наличностите в записките)" in printed
    assert "КР  Кредитна карта  (не се сверява)" in printed


def test_check_finds_the_data_folder_through_the_environment(tmp_path, capsys, monkeypatch):
    main(["init", str(tmp_path), "--language", "en"])
    capsys.readouterr()
    monkeypatch.setenv(DATA_FOLDER_ENVIRONMENT_VARIABLE, str(tmp_path))

    exit_code = main(["check"])

    assert exit_code == 0
    assert "are valid" in capsys.readouterr().out


def test_check_reports_a_problem_in_the_language_of_the_settings(tmp_path, capsys):
    main(["init", str(tmp_path), "--language", "bg"])
    capsys.readouterr()
    categories_file = tmp_path / "config" / "categories.yaml"
    broken_categories = categories_file.read_text(encoding="utf-8").replace(
        "fallback_category: Други", "fallback_category: Разни"
    )
    categories_file.write_text(broken_categories, encoding="utf-8")

    exit_code = main(["check", "--data-folder", str(tmp_path)])

    printed = capsys.readouterr()
    assert exit_code == 1
    assert "'fallback_category' е 'Разни'" in printed.err
    assert "categories.yaml" in printed.err


def test_check_without_a_data_folder_explains_what_to_do(capsys, monkeypatch):
    monkeypatch.delenv(DATA_FOLDER_ENVIRONMENT_VARIABLE, raising=False)

    exit_code = main(["check"])

    printed = capsys.readouterr()
    assert exit_code == 1
    assert "--data-folder" in printed.err
