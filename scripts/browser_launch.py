#!/usr/bin/env python3
"""Browser launch helper shared by the rendering scripts.

Playwright does not ship a Chromium build for every platform it still runs on:
macOS 12 stopped receiving one as of the 1.6x line, so ``install chromium``
fails there with "Playwright does not support chromium on mac12". Falling back
to an installed Chrome or Edge channel keeps rendered mode usable on those
hosts, and both channels speak the CDP protocol the accessibility capture uses.

The module deliberately imports playwright lazily: the scripts that depend on
it treat playwright as an optional native dependency and must stay importable
(and report a useful error) when it is absent.
"""

from __future__ import annotations

from typing import Any

BROWSER_CHANNELS = ("chrome", "msedge")


def launch_browser(playwright: Any) -> tuple[Any, str]:
    """Launch a headless browser, preferring the bundled Chromium build.

    Returns ``(browser, engine)`` where ``engine`` names what actually rendered
    the page: ``playwright-chromium``, ``system-chrome`` or ``system-msedge``.
    The bundled launch is attempted first so behaviour is unchanged on hosts
    that do have a Chromium build; the channel fallback only runs when that
    launch raises.
    """
    from playwright.sync_api import Error as PlaywrightError

    try:
        return playwright.chromium.launch(headless=True), "playwright-chromium"
    except PlaywrightError as bundled_error:
        for channel in BROWSER_CHANNELS:
            try:
                browser = playwright.chromium.launch(channel=channel, headless=True)
            except PlaywrightError:
                continue
            return browser, f"system-{channel}"
        raise bundled_error
