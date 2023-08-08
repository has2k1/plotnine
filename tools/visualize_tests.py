#!/usr/bin/env python
#
# This builds a html page of all images from the image comparison tests
# and opens that page in the browser.
#
#   $ python tools/visualize_tests.py
#

import argparse
from collections import defaultdict
from pathlib import Path

html_template = """<html><head><style media="screen" type="text/css">
img{{
  width:100%;
  max-width:800px;
}}

td, th {{
    text-align: center;
}}

td {{
    font-size: small;
}}

thead tr {{
    background-color: #B39C7D;
    font-weight: bold;
}}

tbody tr:nth-child(odd) {{
    background-color: #fff5cf;
}}

tbody tr:nth-child(even) {{
    background-color:  #dbcdad;
}}

tbody tr td img{{
    background-color:  #FFFFFF;
}}

</style>
</head><body>
{failed}
{new}
{body}
</body></html>
"""

subdir_template = """<h2>{subdir}</h2><table>
<thead><td>name</td><td>actual</td><td>expected</td><td>diff</td></thead>
{rows}
</table>
"""

failed_template = """<h2>Only Failed</h2><table>
<thead><td>name</td><td>actual</td><td>expected</td><td>diff</td></thead>
{rows}
</table>
"""

new_template = """<h2>New Tests</h2><table>
<thead><td>name</td><td>actual</td><td>expected</td><td>diff</td></thead>
{rows}
</table>
"""

row_template = """
<tr>
    <td>{0}{1}</td>
    <td><a href="{2}"><img src="{2}"></a></td>
    <td><a href="{3}"><img src="{3}"></a></td>
    <td>{4}</td>
</tr>
"""

linked_image_template = '<a href="{0}"><img src="{0}"></a>'
IMAGE_DIR = Path("tests/result_images").resolve()
expected_suffix = "-expected"
failed_suffix = "-failed-diff"


def make_row(actual, expected, failed):
    _actual = f'<a href="{actual}"><img src="{actual}">'
    _expected = f'<a href="{expected}"><img src="{expected}">'
    _failed = "--"

    if failed:
        _failed = f'<a href="{failed}">diff</a>'
        status = "failed"
    elif not expected:
        status = "new"
        _expected = ""
        _failed = ""
    else:
        status = "passed"

    return f"""
<tr>
    <td>{actual.name}<br />({status})</td>
    <td>{_actual}</td>
    <td>{_expected}</td>
    <td>{_failed}</td>
</tr>
"""


def get_test_images():
    subdirs = (name for name in IMAGE_DIR.iterdir() if name.is_dir())
    for subdir in sorted(subdirs):
        for file in subdir.iterdir():
            cflag = (
                file.is_dir()
                or file.suffix != ".png"
                or file.stem.endswith(failed_suffix)
                or file.stem.endswith(expected_suffix)
            )
            if cflag:
                continue

            expected = file.with_stem(f"{file.stem}{expected_suffix}")
            failed = file.with_stem(f"{file.stem}{failed_suffix}")
            if not expected.exists():
                expected = None
            if not failed.exists():
                failed = None

            yield (subdir, file, expected, failed)


def run(show_browser=True):
    failed_rows = []
    new_rows = []
    body_sections = []
    subdir_d = defaultdict(list)

    for subdir, actual, expected, failed in get_test_images():
        row = make_row(actual, expected, failed)
        if failed:
            failed_rows.append(row)
        elif not expected:
            new_rows.append(row)
        else:
            subdir_d[subdir].append(row)

    for subdir, rows in subdir_d.items():
        body_sections.append(
            subdir_template.format(subdir=subdir, rows="\n".join(rows))
        )

    failed = ""
    new = ""
    if failed_rows:
        failed = failed_template.format(rows="\n".join(failed_rows))
    if new_rows:
        new = new_template.format(rows="\n".join(new_rows))

    body = "".join(body_sections)
    html = html_template.format(failed=failed, new=new, body=body)
    index = IMAGE_DIR / "index.html"
    with index.open("w") as f:
        f.write(html)

    show_message = not show_browser
    if show_browser:
        try:
            import webbrowser

            webbrowser.open(f"{index}")
        except Exception:
            show_message = True

    if show_message:
        print(f"open {index.resolve()} in a browser for a visual comparison.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't show browser after creating index page.",
    )
    args = parser.parse_args()
    run(show_browser=not args.no_browser)
