# -*- coding: utf-8 -*-
import contextlib
import sys

__all__ = [
    "set_reporter",
    "get_reporter",
    "Reporter",
]
this = sys.modules[__name__]
this._reporter = None


def set_reporter(reporter, *args, **kwargs):
    if isinstance(reporter, Reporter):
        this._reporter = reporter
    else:
        this._reporter = reporter(*args, **kwargs)


def get_reporter():
    if this._reporter is None:
        this._reporter = Reporter()
    return this._reporter


class ProgressBar(object):
    def __init__(self, reporter, label, max_size, data):
        self.reporter = reporter
        self.label = label
        self.max_size = max_size
        self.data = data

    def start(self):
        self.reporter.start_progress(self.label, self.max_size, self.data)

    def update(self, chunk_size=0, data=None):
        if data is not None:
            self.data = data
        self.reporter.update_progress(self.label, chunk_size, self.data)

    def end(self):
        self.reporter.end_progress(self.label, self.data)


class Reporter(object):

    ProgressBar = ProgressBar

    def start_resolve(self, requirements):
        """Called when a Resolver.resolve is called with some requirements."""

    def find_requirement(self, requirement):
        """Called just before attempting to resolve a requirement."""

    def resolve_requirement(self, requirement, module_spec):
        """Called when a a requirement is resolved."""

    def end_resolve(self, resolved, unresolved):
        """Called when Resolver.resolve is done."""

    def start_localize(self, module_specs):
        """Called when Localizer.localize is called with a list of specs."""

    def localize_module(self, module_spec, module):
        """Called when a module is localized."""

    def end_localize(self, localized):
        """Called when Localizer.localize is done."""

    def start_progress(self, label, max_size, data):
        """Called when a download is started."""

    def update_progress(self, label, chunk_size, data):
        """Called each time a chunk is downloaded."""

    def end_progress(self, label, data):
        """Called when a download is finished."""

    @contextlib.contextmanager
    def progress_bar(self, label, max_size, data=None):
        bar = self.ProgressBar(self, label, max_size, data)
        try:
            bar.start()
            yield bar
        finally:
            bar.end()
