import pytest
pytest.importorskip("click")

from flask_sqlalchemy.cli import db_create


def test_cli_create(clirunner, db, script_info, mocker):
    mock_execute = mocker.patch.object(
        db,
        "_execute_for_all_tables",
    )

    result = clirunner.invoke(db_create, obj=script_info)
    assert result.exit_code == 0
    mock_execute.assert_called_once_with(None, '__all__', 'create_all')
    assert "Database created successfully." in result.output
