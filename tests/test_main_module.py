from main import main


def test_main_prints_expected_message(capsys):
    main()
    captured = capsys.readouterr()
    assert "Hello from container-crash-detection-system!" in captured.out
