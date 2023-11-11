import project as wrp
from datetime import datetime


def test_reabable_time():
    s = datetime(2023, 1, 1)
    e = datetime(2023, 1, 2)
    assert wrp.get_readable_time(e - s) == "1 hr, 0 sec, 0 µs"


def test_file_name():
    assert wrp.get_file_name("test.csv").endswith(".csv")


def test_urls():
    assert wrp.get_urls(["https://www.example.com", "https://www.example1.com"]) == [
        "https://www.example.com",
        "https://www.example1.com",
    ]


def test_flag_true():
    wrp.get_flag("y") == True


def test_flag_false():
    wrp.get_flag("n") == False
