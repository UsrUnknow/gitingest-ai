import pytest
from gitingest.utils.tokens import count_tokens, truncate_content, estimate_context_tokens

@pytest.mark.parametrize("text,expected", [
    ("Hello world", 2),
    ("Bonjour le monde", 3),
    ("", 0),
])
def test_count_tokens(text, expected):
    assert count_tokens(text, encoding_name="cl100k_base") == expected

def test_truncate_content_end():
    text = "A B C D E F G"
    # 7 tokens, on tronque à 4
    truncated = truncate_content(text, 4, strategy="end", encoding_name="cl100k_base")
    assert count_tokens(truncated, encoding_name="cl100k_base") == 4
    assert truncated.startswith("A B C D")

def test_truncate_content_start():
    text = "A B C D E F G"
    truncated = truncate_content(text, 4, strategy="start", encoding_name="cl100k_base")
    assert count_tokens(truncated, encoding_name="cl100k_base") == 4
    assert truncated.endswith("E F G")

def test_truncate_content_middle():
    text = "A B C D E F G"
    truncated = truncate_content(text, 4, strategy="middle", encoding_name="cl100k_base")
    assert count_tokens(truncated, encoding_name="cl100k_base") == 4
    # Doit contenir le début et la fin
    assert truncated.startswith("A B") and truncated.endswith("F G")

def test_estimate_context_tokens():
    texts = ["A B C", "D E F"]
    total = estimate_context_tokens(texts, encoding_name="cl100k_base")
    assert total == 6 