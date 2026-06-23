from plotnine import theme, theme_gray


def test_strip_placement_themeable_default_and_set():
    assert theme_gray().getp("strip_placement") == "inside"
    assert theme(strip_placement="outside").getp("strip_placement") == (
        "outside"
    )
