from io import StringIO

from src.reports import write_dict_to_csv


def test_write_dict_to_csv():
    f = StringIO()
    data = {"Header1": [1, 2], "Header2": [4, 3]}
    write_dict_to_csv(data, f)

    f.seek(0)
    text = f.read()
    assert text == "Header1,Header2\r\n1,4\r\n2,3\r\n"
