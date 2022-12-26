"""mcve"""
from difflib import unified_diff


def test_me() -> None:
    """mcve"""
    result = list(unified_diff("abc", "ab"))
    expected = ["--- \n", "+++ \n", "@@ -1,3 +1,2 @@\n", " a", " b", "-c"]
    assert result == expected
