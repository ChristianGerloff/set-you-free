from src.pages.main import join_string_in_list


def test_join_string_in_list():
    expected = "This is a test"
    list_to_test = ["This", "is", "a", "test"]
    assert join_string_in_list(list_to_test) == expected
