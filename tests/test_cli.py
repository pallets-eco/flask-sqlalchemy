import pytest
pytest.importorskip("click")

from flask_sqlalchemy.cli import db_create, db_drop, db_binds


def test_cli_create(clirunner, db, script_info, mocker):
    mock_execute = mocker.patch.object(
        db,
        "_execute_for_all_tables",
    )

    result = clirunner.invoke(db_create, obj=script_info)
    assert result.exit_code == 0
    mock_execute.assert_called_once_with(None, '__all__', 'create_all')
    assert "Database created successfully." in result.output


def test_cli_drop(clirunner, db, script_info, mocker):
    mock_execute = mocker.patch.object(
        db,
        "_execute_for_all_tables",
    )

    result = clirunner.invoke(db_drop, input="y", obj=script_info)
    assert result.exit_code == 0
    assert result.output.startswith(
        "This will destroy all the data in your database. "
        "Do you want to continue? [y/N]:"
    )
    mock_execute.assert_called_once_with(None, '__all__', 'drop_all')
    assert "Database dropped successfully." in result.output


def test_cli_drop_abort(clirunner, db, script_info, mocker):
    mock_execute = mocker.patch.object(
        db,
        "_execute_for_all_tables",
    )

    result = clirunner.invoke(db_drop, input="n", obj=script_info)
    assert result.exit_code == 1
    assert result.output.startswith(
        "This will destroy all the data in your database. "
        "Do you want to continue? [y/N]:"
    )
    assert not mock_execute.called
    assert "Database dropped successfully." not in result.output


def test_cli_binds(clirunner, script_info, Todo):
    result = clirunner.invoke(db_binds, obj=script_info)
    assert result.exit_code == 0
    assert "todos -> sqlite:///:memory:" in result.output


def test_cli_binds_empty_db(clirunner, db, script_info):
    result = clirunner.invoke(db_binds, obj=script_info)
    assert result.exit_code == 1
    assert "Error: No database tables found." in result.output
