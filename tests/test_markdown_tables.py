from scripts.check_markdown_tables import check_tables


def test_unescaped_caption_breaks_six_column_table():
    text = '|镜头|时间|画面|声音|字幕|素材|\n|---|---|---|---|---|---|\n|S03|2–4|放物|静音|Keys ✓ | Card ✓ | Water □|待拍|'
    assert check_tables(text) == [{"line": 3, "expected": 6, "actual": 8}]
    fixed = text.replace('Keys ✓ | Card ✓ | Water □', r'Keys ✓ \| Card ✓ \| Water □')
    assert check_tables(fixed) == []
    assert 'Water □' in fixed and '待拍' in fixed


def test_plain_tables_fences_and_backslash_parity():
    assert check_tables('a | b\n--- | ---\nx | y\n\n```text\n|a|b|\n|---|---|\n|x|y|z|\n```') == []
    assert check_tables('|a|b|\n|---|---|\n|x\\\\|y|z|') == [
        {"line": 3, "expected": 2, "actual": 3}]
    assert check_tables('|a|b|\n|---|---|---|') == [
        {"line": 1, "expected": 3, "actual": 2}]
