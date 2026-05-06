#!/usr/bin/env python
#
# Build an HTML page that summarises image-comparison test results, then
# open it in a browser:
#
#   $ python tools/visualize_tests.py
#

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

IMAGE_DIR = Path("tests/result_images").resolve()
EXPECTED_SUFFIX = "-expected"
FAILED_SUFFIX = "-failed-diff"
RESULT_PREFIX = "tests/result_images"
BASELINE_PREFIX = "tests/baseline_images"


@dataclass(frozen=True)
class TestImage:
    """A single image-comparison test result"""

    subdir: str
    name: str
    actual_rel: str
    expected_rel: str | None
    failed_rel: str | None

    @property
    def status(self) -> str:
        if self.failed_rel:
            return "failed"
        if self.expected_rel is None:
            return "new"
        return "passed"

    @property
    def label(self) -> str:
        return f"{self.subdir}/{self.name}.png"

    @property
    def filename(self) -> str:
        return f"{self.name}.png"

    @property
    def anchor(self) -> str:
        return f"{self.subdir}--{self.name}"


def get_test_images() -> Iterator[TestImage]:
    """
    Yield one TestImage per test, sorted by (subdir, name)
    """
    subdirs = sorted(d for d in IMAGE_DIR.iterdir() if d.is_dir())
    for subdir in subdirs:
        for png in sorted(subdir.glob("*.png")):
            stem = png.stem
            if stem.endswith((EXPECTED_SUFFIX, FAILED_SUFFIX)):
                continue

            expected = subdir / f"{stem}{EXPECTED_SUFFIX}.png"
            failed = subdir / f"{stem}{FAILED_SUFFIX}.png"

            yield TestImage(
                subdir=subdir.name,
                name=stem,
                actual_rel=f"{subdir.name}/{png.name}",
                expected_rel=(
                    f"{subdir.name}/{expected.name}"
                    if expected.exists()
                    else None
                ),
                failed_rel=(
                    f"{subdir.name}/{failed.name}" if failed.exists() else None
                ),
            )


CSS = """
:root {
  color-scheme: light dark;
  --bg: #fafbfc;
  --fg: #3a4047;
  --muted: #8b939d;
  --border: #e1e4e8;
  --topbar-bg: rgba(250, 251, 252, 0.85);
  --chip-bg: #f1f3f5;
  --chip-fg: #3a4047;
  --chip-active-bg: #5a6470;
  --chip-active-fg: #ffffff;
  --green: #2da44e;
  --green-soft: #e6f6ec;
  --red: #d8404a;
  --red-soft: #fbecee;
  --amber: #b08400;
  --amber-soft: #fcf3d4;
  --link: #2c7be5;
  --img-bg: #ffffff;
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #1c2128;
    --fg: #c9d1d9;
    --muted: #8b949e;
    --border: #373e47;
    --topbar-bg: rgba(28, 33, 40, 0.85);
    --chip-bg: #2d333b;
    --chip-fg: #c9d1d9;
    --chip-active-bg: #adbac7;
    --chip-active-fg: #22272e;
    --green: #57ab5a;
    --green-soft: #1b3325;
    --red: #e5534b;
    --red-soft: #3b1d22;
    --amber: #c69026;
    --amber-soft: #3a2c10;
    --link: #6cb6ff;
    --img-bg: #ffffff;
  }
}

:root[data-theme="dark"] {
  --bg: #1c2128;
  --fg: #c9d1d9;
  --muted: #8b949e;
  --border: #373e47;
  --topbar-bg: rgba(28, 33, 40, 0.85);
  --chip-bg: #2d333b;
  --chip-fg: #c9d1d9;
  --chip-active-bg: #adbac7;
  --chip-active-fg: #22272e;
  --green: #57ab5a;
  --green-soft: #1b3325;
  --red: #e5534b;
  --red-soft: #3b1d22;
  --amber: #c69026;
  --amber-soft: #3a2c10;
  --link: #6cb6ff;
  --img-bg: #ffffff;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
               system-ui, sans-serif;
  font-size: 14px;
  background: var(--bg);
  color: var(--fg);
}

a { color: var(--link); }

.topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  background: var(--topbar-bg);
  -webkit-backdrop-filter: blur(10px);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border);
  padding: 12px 20px;
}

.topbar h1 {
  margin: 0;
  font-size: 18px;
  white-space: nowrap;
}

.topbar-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.topbar-row + .topbar-row {
  margin-top: 8px;
}

.chips {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.chip {
  border: 1px solid var(--border);
  background: var(--chip-bg);
  color: var(--chip-fg);
  padding: 4px 10px;
  border-radius: 999px;
  font: inherit;
  cursor: pointer;
}

.chip .count {
  margin-left: 4px;
  font-variant-numeric: tabular-nums;
  opacity: 0.85;
}

.chip[data-filter="all"].active {
  background: var(--chip-active-bg);
  color: var(--chip-active-fg);
}

.chip[data-filter="failed"] { color: var(--red); }
.chip[data-filter="failed"].active {
  background: var(--red-soft);
  color: var(--red);
  border-color: var(--red);
}

.chip[data-filter="new"] { color: var(--amber); }
.chip[data-filter="new"].active {
  background: var(--amber-soft);
  color: var(--amber);
  border-color: var(--amber);
}

.chip[data-filter="passed"] { color: var(--green); }
.chip[data-filter="passed"].active {
  background: var(--green-soft);
  color: var(--green);
  border-color: var(--green);
}

.chip.zero {
  color: var(--green);
  border-color: var(--green);
  background: var(--green-soft);
}

.search {
  flex: 1;
  min-width: 220px;
  padding: 6px 10px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--bg);
  color: var(--fg);
  font: inherit;
}

.theme-toggle {
  padding: 6px 10px;
  border: 1px solid var(--border);
  background: var(--chip-bg);
  color: var(--chip-fg);
  border-radius: 6px;
  font: inherit;
  font-size: 12px;
  cursor: pointer;
  min-width: 84px;
}

.theme-toggle:hover { border-color: var(--fg); }

.approve-actions {
  display: flex;
  gap: 6px;
  align-items: center;
  flex-wrap: wrap;
}

.approve-actions button {
  padding: 4px 10px;
  border: 1px solid var(--border);
  background: var(--chip-bg);
  color: var(--chip-fg);
  border-radius: 6px;
  font: inherit;
  cursor: pointer;
}

.approve-actions button:hover { border-color: var(--fg); }

.approve-actions .selected-count {
  margin-left: auto;
  color: var(--muted);
}

#cmd {
  display: block;
  width: 100%;
  min-height: 4em;
  max-height: 200px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco,
               Consolas, monospace;
  font-size: 12px;
  padding: 8px;
  margin-top: 8px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--bg);
  color: var(--fg);
  resize: vertical;
  white-space: pre;
}

main {
  padding: 20px;
}

.test-row {
  display: grid;
  grid-template-columns: minmax(220px, 280px) 1fr;
  gap: 16px;
  align-items: start;
  padding: 16px 0;
  border-bottom: 1px solid var(--border);
}

.test-row.hidden { display: none; }

.meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.meta .name {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco,
               Consolas, monospace;
  font-size: 13px;
  color: inherit;
  text-decoration: none;
  word-break: break-all;
}
.meta .name:hover { text-decoration: underline; }

.status-badge {
  align-self: flex-start;
  padding: 1px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.status-badge.failed { background: var(--red-soft); color: var(--red); }
.status-badge.new    { background: var(--amber-soft); color: var(--amber); }
.status-badge.passed { background: var(--green-soft); color: var(--green); }

.approve-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--muted);
  cursor: pointer;
  user-select: none;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.view-buttons {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.view-buttons button {
  padding: 3px 8px;
  border: 1px solid var(--border);
  background: var(--chip-bg);
  color: var(--chip-fg);
  border-radius: 6px;
  font: inherit;
  font-size: 12px;
  cursor: pointer;
}

.view-buttons button.active {
  background: var(--chip-active-bg);
  color: var(--chip-active-fg);
  border-color: var(--chip-active-bg);
}

.images {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.images figure {
  margin: 0;
  flex: 1 1 320px;
  min-width: 220px;
  max-width: 440px;
}

.images figcaption {
  font-size: 11px;
  color: var(--muted);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.images img {
  width: 100%;
  display: block;
  background: var(--img-bg);
  border: 1px solid var(--border);
  border-radius: 4px;
}

.test-row.view-side .images-slider,
.test-row.view-side .images-flip,
.test-row.view-slider .images-side,
.test-row.view-slider .images-flip,
.test-row.view-flip   .images-side,
.test-row.view-flip   .images-slider {
  display: none;
}

.images-slider figure,
.images-flip figure {
  flex: 1 1 320px;
  min-width: 220px;
  max-width: 440px;
}

.slider-wrap {
  position: relative;
  display: block;
  user-select: none;
  touch-action: none;
  cursor: ew-resize;
}

.slider-wrap img {
  width: 100%;
  display: block;
  background: var(--img-bg);
  border: 1px solid var(--border);
  border-radius: 4px;
  pointer-events: none;
  -webkit-user-drag: none;
  user-select: none;
}

.slider-wrap .slider-top {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  clip-path: inset(0 0 0 50%);
}

.slider-handle {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  width: 2px;
  background: var(--link);
  pointer-events: none;
  transform: translateX(-1px);
}

.slider-handle::after {
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  width: 18px;
  height: 18px;
  background: var(--link);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 0 2px var(--bg);
}

.flip-area {
  cursor: pointer;
}

.images-flip .flip-hint {
  text-transform: none;
  letter-spacing: 0;
  font-size: 11px;
  font-weight: 400;
  opacity: 0.7;
}

.flip-area img {
  width: 100%;
  display: block;
  background: var(--img-bg);
  border: 1px solid var(--border);
  border-radius: 4px;
}

.empty {
  padding: 40px;
  text-align: center;
  color: var(--muted);
}
"""

JS = """
(function () {
  const rows = Array.from(document.querySelectorAll('.test-row'));
  const chips = Array.from(document.querySelectorAll('.chip'));
  const search = document.getElementById('search');
  const cmd = document.getElementById('cmd');
  const selectedCount = document.getElementById('selected-count');
  const copyBtn = document.getElementById('copy-btn');
  const selAllFailed = document.getElementById('sel-all-failed');
  const selAllNew = document.getElementById('sel-all-new');
  const clearAll = document.getElementById('clear-all');

  let activeFilter = 'all';
  let activeQuery = '';

  function applyFilter() {
    for (const row of rows) {
      const status = row.dataset.status;
      const name = row.dataset.name;
      const statusOk =
        activeFilter === 'all' || activeFilter === status;
      const queryOk = !activeQuery || name.includes(activeQuery);
      row.classList.toggle('hidden', !(statusOk && queryOk));
    }
  }

  for (const chip of chips) {
    chip.addEventListener('click', () => {
      activeFilter = chip.dataset.filter;
      for (const c of chips) {
        c.classList.toggle('active', c === chip);
      }
      applyFilter();
    });
  }

  search.addEventListener('input', () => {
    activeQuery = search.value.trim().toLowerCase();
    applyFilter();
  });

  function checkedRows() {
    return rows.filter((r) => {
      const cb = r.querySelector('input.approve-cb');
      return cb && cb.checked;
    });
  }

  function buildCmd() {
    const checked = checkedRows();
    selectedCount.textContent =
      checked.length === 0
        ? 'No tests selected'
        : checked.length + ' selected';
    if (checked.length === 0) {
      cmd.value = '';
      return;
    }
    const subdirs = new Set();
    const lines = [];
    for (const r of checked) {
      const sub = r.dataset.subdir;
      const file = r.dataset.file;
      subdirs.add(sub);
      lines.push(
        '\\\\cp tests/result_images/' + sub + '/' + file +
        ' tests/baseline_images/' + sub + '/' + file
      );
    }
    const mkdirs = Array.from(subdirs)
      .sort()
      .map((s) => 'tests/baseline_images/' + s)
      .join(' ');
    cmd.value = 'mkdir -p ' + mkdirs + '\\n' + lines.join('\\n');
  }

  for (const cb of document.querySelectorAll('input.approve-cb')) {
    cb.addEventListener('change', buildCmd);
  }

  selAllFailed.addEventListener('click', () => {
    for (const r of rows) {
      const cb = r.querySelector('input.approve-cb');
      if (cb && r.dataset.status === 'failed') cb.checked = true;
    }
    buildCmd();
  });
  selAllNew.addEventListener('click', () => {
    for (const r of rows) {
      const cb = r.querySelector('input.approve-cb');
      if (cb && r.dataset.status === 'new') cb.checked = true;
    }
    buildCmd();
  });
  clearAll.addEventListener('click', () => {
    for (const r of rows) {
      const cb = r.querySelector('input.approve-cb');
      if (cb) cb.checked = false;
    }
    buildCmd();
  });

  copyBtn.addEventListener('click', async () => {
    if (cmd.value === '') {
      cmd.focus();
      return;
    }
    cmd.focus();
    cmd.select();
    let copied = false;
    if (navigator.clipboard && navigator.clipboard.writeText) {
      try {
        await navigator.clipboard.writeText(cmd.value);
        copied = true;
      } catch (err) {
        copied = false;
      }
    }
    if (!copied) {
      try { copied = document.execCommand('copy'); }
      catch (err) { copied = false; }
    }
    const original = copyBtn.textContent;
    copyBtn.textContent = copied ? 'Copied!' : 'Press Ctrl/Cmd-C';
    setTimeout(() => { copyBtn.textContent = original; }, 1500);
  });

  // Per-row view-mode tabs and slider/flip wiring (failed rows only)
  for (const row of rows) {
    if (row.dataset.status !== 'failed') continue;

    const buttons = row.querySelectorAll('.view-buttons button');
    for (const btn of buttons) {
      btn.addEventListener('click', () => {
        const view = btn.dataset.view;
        for (const b of buttons) {
          b.classList.toggle('active', b === btn);
        }
        row.classList.remove('view-side', 'view-slider', 'view-flip');
        row.classList.add('view-' + view);
      });
    }

    const wrap = row.querySelector('.slider-wrap');
    if (wrap) {
      const top = wrap.querySelector('.slider-top');
      const handle = wrap.querySelector('.slider-handle');
      let dragging = false;
      const setPos = (clientX) => {
        const rect = wrap.getBoundingClientRect();
        const x = (clientX - rect.left) / rect.width;
        const pct = Math.max(0, Math.min(1, x)) * 100;
        top.style.clipPath = 'inset(0 0 0 ' + pct + '%)';
        handle.style.left = pct + '%';
      };
      wrap.addEventListener('pointerdown', (e) => {
        e.preventDefault();
        dragging = true;
        try { wrap.setPointerCapture(e.pointerId); }
        catch (err) {}
        setPos(e.clientX);
      });
      wrap.addEventListener('pointermove', (e) => {
        if (dragging) setPos(e.clientX);
      });
      const stop = (e) => {
        dragging = false;
        try { wrap.releasePointerCapture(e.pointerId); }
        catch (err) {}
      };
      wrap.addEventListener('pointerup', stop);
      wrap.addEventListener('pointercancel', stop);
    }

    const flip = row.querySelector('.flip-area');
    if (flip) {
      const img = flip.querySelector('img');
      const state = row.querySelector('.images-flip .flip-state');
      const actual = flip.dataset.actual;
      const expected = flip.dataset.expected;
      let showing = 'actual';
      const update = () => {
        img.src = showing === 'actual' ? actual : expected;
        if (state) state.textContent = showing;
      };
      flip.addEventListener('click', () => {
        showing = showing === 'actual' ? 'expected' : 'actual';
        update();
      });
      update();
    }
  }

  // Theme toggle (Auto / Light / Dark), persisted in localStorage.
  const themeBtn = document.getElementById('theme-toggle');
  const themeKey = 'plotnine-vt-theme';
  const themes = ['auto', 'light', 'dark'];
  const labels = { auto: '◐ Auto', light: '☀ Light', dark: '☾ Dark' };
  let themeIdx = Math.max(
    0,
    themes.indexOf(localStorage.getItem(themeKey) || 'auto')
  );

  function applyTheme() {
    const t = themes[themeIdx];
    if (t === 'auto') {
      document.documentElement.removeAttribute('data-theme');
    } else {
      document.documentElement.setAttribute('data-theme', t);
    }
    themeBtn.textContent = labels[t];
  }
  themeBtn.addEventListener('click', () => {
    themeIdx = (themeIdx + 1) % themes.length;
    localStorage.setItem(themeKey, themes[themeIdx]);
    applyTheme();
  });
  applyTheme();

  // Set initial chip-zero highlight on load.
  function highlightZeroChips() {
    for (const chip of chips) {
      const f = chip.dataset.filter;
      if (f === 'failed' || f === 'new') {
        const countEl = chip.querySelector('.count');
        const n = countEl ? parseInt(countEl.textContent, 10) : 0;
        chip.classList.toggle('zero', n === 0);
      }
    }
  }

  highlightZeroChips();
  buildCmd();
})();
"""

HTML_TEMPLATE = """\
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>plotnine test results</title>
<style>{css}</style>
</head>
<body>
<header class="topbar">
  <div class="topbar-row">
    <h1>plotnine test results</h1>
    <div class="chips">
      <button class="chip active" data-filter="all">All\
        <span class="count">{total}</span></button>
      <button class="chip" data-filter="failed">Failed\
        <span class="count">{failed}</span></button>
      <button class="chip" data-filter="new">New\
        <span class="count">{new_count}</span></button>
      <button class="chip" data-filter="passed">Passed\
        <span class="count">{passed}</span></button>
    </div>
    <input type="search" id="search" class="search"
           placeholder="filter by name…" autocomplete="off">
    <button id="theme-toggle" class="theme-toggle" type="button"
            title="Cycle theme: Auto → Light → Dark"></button>
  </div>
  <div class="topbar-row approve-actions">
    <button id="sel-all-failed" type="button">Select all failed</button>
    <button id="sel-all-new" type="button">Select all new</button>
    <button id="clear-all" type="button">Clear</button>
    <button id="copy-btn" type="button">Copy</button>
    <span class="selected-count" id="selected-count">No tests selected</span>
  </div>
  <textarea id="cmd" readonly
            placeholder="Check approve boxes below to build a cp command."\
            ></textarea>
</header>
<main>
{rows}
</main>
<script>{js}</script>
</body>
</html>
"""


def _img_cell(caption: str, src: str) -> str:
    return (
        f"<figure><figcaption>{caption}</figcaption>"
        f'<a href="{src}"><img src="{src}" loading="lazy" alt=""></a>'
        f"</figure>"
    )


def _failed_content(test: TestImage) -> str:
    actual = test.actual_rel
    expected = test.expected_rel or ""
    failed = test.failed_rel or ""
    side = (
        '<div class="images images-side">'
        + _img_cell("actual", actual)
        + (_img_cell("expected", expected) if expected else "")
        + (_img_cell("diff", failed) if failed else "")
        + "</div>"
    )
    if expected:
        slider = (
            '<div class="images images-slider">'
            "<figure>"
            "<figcaption>actual ↔ expected</figcaption>"
            '<div class="slider-wrap">'
            f'<img class="slider-base" src="{expected}" '
            'alt="expected" draggable="false">'
            f'<img class="slider-top" src="{actual}" '
            'alt="actual" draggable="false">'
            '<div class="slider-handle"></div>'
            "</div>"
            "</figure>"
            + (_img_cell("diff", failed) if failed else "")
            + "</div>"
        )
        flip = (
            '<div class="images images-flip">'
            "<figure>"
            '<figcaption class="flip-label">'
            '<span class="flip-state">actual</span>'
            '<span class="flip-hint"> — click to flip</span>'
            "</figcaption>"
            f'<div class="flip-area" data-actual="{actual}" '
            f'data-expected="{expected}">'
            '<img alt="">'
            "</div>"
            "</figure>"
            + (_img_cell("diff", failed) if failed else "")
            + "</div>"
        )
        tabs = (
            '<div class="view-buttons">'
            '<button data-view="side" class="active" type="button">'
            "Side-by-side</button>"
            '<button data-view="slider" type="button">Slider</button>'
            '<button data-view="flip" type="button">Flip</button>'
            "</div>"
        )
    else:
        slider = ""
        flip = ""
        tabs = ""
    return '<div class="content">' + tabs + side + slider + flip + "</div>"


def _new_content(test: TestImage) -> str:
    return (
        '<div class="content"><div class="images images-side">'
        + _img_cell("actual", test.actual_rel)
        + "</div></div>"
    )


def _passed_content(test: TestImage) -> str:
    parts = [_img_cell("actual", test.actual_rel)]
    if test.expected_rel:
        parts.append(_img_cell("expected", test.expected_rel))
    return (
        '<div class="content"><div class="images images-side">'
        + "".join(parts)
        + "</div></div>"
    )


def render_row(test: TestImage) -> str:
    """
    Build the HTML for a single test row
    """
    name_link = f'<a class="name" href="#{test.anchor}">{test.label}</a>'
    badge = f'<span class="status-badge {test.status}">{test.status}</span>'
    parts = [name_link, badge]
    if test.status in ("failed", "new"):
        parts.append(
            '<label class="approve-label">'
            '<input class="approve-cb" type="checkbox"> approve'
            "</label>"
        )
    meta = '<div class="meta">' + "".join(parts) + "</div>"

    if test.status == "failed":
        content = _failed_content(test)
    elif test.status == "new":
        content = _new_content(test)
    else:
        content = _passed_content(test)

    classes = ["test-row"]
    if test.status == "failed":
        classes.append("view-side")
    return (
        f'<div id="{test.anchor}" class="{" ".join(classes)}" '
        f'data-status="{test.status}" '
        f'data-name="{test.label.lower()}" '
        f'data-subdir="{test.subdir}" '
        f'data-file="{test.filename}">' + meta + content + "</div>"
    )


def render_html(tests: list[TestImage]) -> str:
    """
    Render the full HTML page
    """
    status_order = {"failed": 0, "new": 1, "passed": 2}
    ordered = sorted(
        tests, key=lambda t: (status_order[t.status], t.subdir, t.name)
    )
    counts = {"failed": 0, "new": 0, "passed": 0}
    for t in ordered:
        counts[t.status] += 1
    rows = "\n".join(render_row(t) for t in ordered)
    if not ordered:
        rows = '<div class="empty">No test images found.</div>'
    return HTML_TEMPLATE.format(
        css=CSS,
        js=JS,
        rows=rows,
        total=len(ordered),
        failed=counts["failed"],
        new_count=counts["new"],
        passed=counts["passed"],
    )


def run(show_browser: bool = True) -> None:
    tests = list(get_test_images())
    html = render_html(tests)
    index = IMAGE_DIR / "index.html"
    index.write_text(html, encoding="utf-8")

    show_message = not show_browser
    if show_browser:
        try:
            import webbrowser

            webbrowser.open(index.as_uri())
        except OSError:
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
