from movies_on_my_radar.__main__ import main


def test_main_displays_startup_message(capsys) -> None:
    main()

    captured = capsys.readouterr()

    assert captured.out == "Hello, world!\n"
