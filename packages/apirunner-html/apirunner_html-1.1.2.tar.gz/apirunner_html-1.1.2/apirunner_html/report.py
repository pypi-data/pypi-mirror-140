import datetime
import json
import os
import re
import warnings
from base64 import b64decode, b64encode
from html import escape
from os.path import isfile

import pytest
from py.xml import html, raw
from apirunner_html import runner

try:
    from ansi2html import Ansi2HTMLConverter, style

    ANSI = True
except ImportError:
    ANSI = False
from . import extras


def pytest_addoption(parser):
    group = parser.getgroup('terminal reporting')
    group.addoption('--pytest_report', action='store', dest='pytest_report', metavar='path', default=None,
                    help='create html report file at given path.')
    group.addoption('--pytest_title', action='store', dest='pytest_title', metavar='path', default="Report",
                    help='given title for report.')
    group.addoption('--pytest_desc', action='store', dest='pytest_desc', metavar='path', default="",
                    help='given desc for report..')
    group.addoption('--pytest_theme', action='store', dest='pytest_theme', metavar='path', default=None,
                    help='given theme for report.')
    group.addoption('--pytest_stylesheet', action='store', dest='pytest_stylesheet', metavar='path', default=None,
                    help='given css file path for report.')
    group.addoption('--pytest_template', action='store', dest='pytest_template', metavar='path', default=None,
                    help='given html file path for report.')
    group.addoption('--pytest_javascript', action='store', dest='pytest_javascript', metavar='path', default=None,
                    help='given js file path for report.')


def pytest_configure(config):
    htmlpath = config.getoption('pytest_report')
    if htmlpath:
        if not hasattr(config, 'slaveinput'):
            # prevent opening htmlpath on slave nodes (xdist)
            config._html = HTMLReport(htmlpath, config)
            config.pluginmanager.register(config._html)


def pytest_unconfigure(config):
    html = getattr(config, '_html', None)
    if html:
        del config._html
        config.pluginmanager.unregister(html)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        fixture_extras = getattr(item.config, "extras", [])
        plugin_extras = getattr(report, "extra", [])
        report.extra = fixture_extras + plugin_extras
        report.nodeid = report.nodeid.encode("utf-8").decode("unicode_escape")


@pytest.fixture
def extra(pytestconfig):
    """Add details to the HTML reports."""
    pytestconfig.extras = []
    yield pytestconfig.extras
    del pytestconfig.extras[:]


def data_uri(content, mime_type="text/plain", charset="utf-8"):
    data = b64encode(content.encode(charset)).decode("ascii")
    return f"data:{mime_type};charset={charset};base64,{data}"


class TestResult:
    def __init__(self, outcome, report, config):
        self.test_id = report.nodeid
        self.time = getattr(report, "duration", 0.0)
        self.outcome = outcome
        self.report = report
        self.config = config
        self.logfile = ""
        self.links_html = []
        self.self_contained = config.getoption("self_contained_html")
        self.additional_html = []
        self.row_table = self.row_extra = None
        test_index = hasattr(report, "rerun") and report.rerun + 1 or 0

        for extra_index, extra in enumerate(getattr(report, "extra", [])):
            self.append_extra_html(extra, extra_index, test_index)

        self.append_log_html(report, self.additional_html)

        cells = [
            html.td(self.outcome, class_="col-result"),
            html.td(self.test_id, class_="col-name"),
            html.td(f"{self.time:.2f}", class_="col-duration"),
            html.td(self.links_html, class_="col-links"),
        ]

        self.config.hook.pytest_html_results_table_row(report=report, cells=cells)
        self.config.hook.pytest_html_results_table_html(report=report, data=self.additional_html)

        if len(cells) > 0:
            self.row_table = html.tr(cells)
            self.row_extra = html.div(self.additional_html)

    def append_extra_html(self, extra, extra_index, test_index):
        href = None
        if extra.get("format") == extras.FORMAT_IMAGE:
            self._append_image(extra, extra_index, test_index)

        elif extra.get("format") == extras.FORMAT_HTML:
            self.additional_html.append((raw(extra.get("content"))))

        elif extra.get("format") == extras.FORMAT_JSON:
            content = json.dumps(extra.get("content"))
            if self.self_contained:
                href = data_uri(content, mime_type=extra.get("mime_type"))
            else:
                href = self.create_asset(
                    content, extra_index, test_index, extra.get("extension")
                )

        elif extra.get("format") == extras.FORMAT_TEXT:
            content = extra.get("content")
            if isinstance(content, bytes):
                content = content.decode("utf-8")
            if self.self_contained:
                href = data_uri(content)
            else:
                href = self.create_asset(
                    content, extra_index, test_index, extra.get("extension")
                )

        elif extra.get("format") == extras.FORMAT_URL:
            href = extra.get("content")

        elif extra.get("format") == extras.FORMAT_VIDEO:
            self._append_video(extra, extra_index, test_index)

        if href is not None:
            self.links_html.append(
                html.a(
                    extra.get("name"),
                    class_=extra.get("format"),
                    href=href,
                    target="_blank",
                )
            )
            self.links_html.append(" ")

    def create_asset(self, content, extra_index, test_index, file_extension, mode="w"):
        # 255 is the common max filename length on various filesystems
        asset_file_name = "{}_{}_{}.{}".format(
            re.sub(r"[^\w\.]", "_", self.test_id),
            str(extra_index),
            str(test_index),
            file_extension,
        )[-255:]
        asset_path = os.path.join(os.path.dirname(self.logfile), "assets", asset_file_name)

        if not os.path.exists(os.path.dirname(asset_path)):
            os.makedirs(os.path.dirname(asset_path))

        relative_path = f"assets/{asset_file_name}"

        kwargs = {"encoding": "utf-8"} if "b" not in mode else {}
        with open(asset_path, mode, **kwargs) as f:
            f.write(content)
        return relative_path

    def append_log_html(self, report, additional_html):
        # ****修改删减断言失败的异常日志信息
        log = html.div(class_="log")
        if report.longrepr:
            log.append(html.br())
        else:
            log.append(html.br())

        for section in report.sections:
            header, content = map(escape, section)
            log.append(f" {header:-^80} ")
            log.append(html.br())
            if ANSI:
                converter = Ansi2HTMLConverter(inline=False, escaped=False)
                content = converter.convert(content, full=False)
            log.append(raw(content))

        if len(log) == 0:
            log = html.div(class_="empty log")
            log.append("No log output captured.")
        self.logfile = ""
        additional_html.append(log)

    def _make_media_html_div(
            self, extra, extra_index, test_index, base_extra_string, base_extra_class
    ):
        content = extra.get("content")
        try:
            is_uri_or_path = content.startswith(("file", "http")) or isfile(content)
        except ValueError:
            # On Windows, os.path.isfile throws this exception when
            # passed a b64 encoded image.
            is_uri_or_path = False
        if is_uri_or_path:
            if self.self_contained:
                warnings.warn(
                    "Self-contained HTML report "
                    "includes link to external "
                    f"resource: {content}"
                )

            html_div = html.a(
                raw(base_extra_string.format(extra.get("content"))), href=content
            )
        elif self.self_contained:
            src = f"data:{extra.get('mime_type')};base64,{content}"
            html_div = raw(base_extra_string.format(src))
        else:
            content = b64decode(content.encode("utf-8"))
            href = src = self.create_asset(
                content, extra_index, test_index, extra.get("extension"), "wb"
            )
            html_div = html.a(class_=base_extra_class, target="_blank", href=href)
        return html_div

    def _append_image(self, extra, extra_index, test_index):
        image_base = '<img src="{}"/>'
        html_div = self._make_media_html_div(
            extra, extra_index, test_index, image_base, "image"
        )
        self.additional_html.append(html.div(html_div, class_="image"))

    def _append_video(self, extra, extra_index, test_index):
        video_base = '<video controls><source src="{}" type="video/mp4"></video>'
        html_div = self._make_media_html_div(
            extra, extra_index, test_index, video_base, "video"
        )
        self.additional_html.append(html.div(html_div, class_="video"))

    def output(self, cid, tid):
        if self.outcome.startswith('X'):
            status = 'fail'
            status_code = 1
        elif self.outcome == "Passed":
            status = 'pass'
            status_code = 0
        elif self.outcome == "Failed":
            status = 'fail'
            status_code = 1
        elif self.outcome == "Error":
            status = 'error'
            status_code = 2
        elif self.outcome == "Skipped":
            status = 'skip'
            status_code = 3
        else:
            status = 'pass'
            status_code = 0

        output = "%s\r\n%s" % (self.outcome, self.report.longrepr)

        return {
            "has_output": output and True or False,
            "tid": "test%s.%s.%s" % (status, cid, tid),
            "desc": self.test_id.split("::")[0] + "[" + self.test_id.split("[")[-1],
            "output": output,
            "status": status,
            "status_code": status_code
        }


class HTMLReport(object):

    def __init__(self, html_file, config):
        html_file = os.path.expanduser(os.path.expandvars(html_file))
        self.html_file = os.path.abspath(html_file)
        self.results = []

        self.errors = self.failed = 0
        self.passed = self.skipped = 0
        self.xfailed = self.xpassed = 0
        has_rerun = config.pluginmanager.hasplugin('rerunfailures')
        self.rerun = 0 if has_rerun else None
        self.config = config

    def _appendrow(self, outcome, report, config):
        result = TestResult(outcome, report, config)
        self.results.append(result)

    def append_passed(self, report):
        if report.when == 'call':
            if hasattr(report, "wasxfail"):
                # pytest < 3.0 marked xpasses as failures
                self.xpassed += 1
                self._appendrow('XPassed', report, self.config)
            else:
                self.passed += 1
                self._appendrow('Passed', report, self.config)

    def append_failed(self, report):
        if getattr(report, 'when', None) == "call":
            if hasattr(report, "wasxfail"):
                self.xfailed += 1
                self._appendrow('XFailed', report, self.config)
            else:
                message = report.longrepr.reprcrash.message
                if message.startswith('assert') or 'Failure' in message:  # assert Error
                    self.failed += 1
                    self._appendrow('Failed', report, self.config)
                else:
                    self.errors += 1
                    self._appendrow('Error', report, self.config)
        else:
            self.errors += 1
            self._appendrow('Error', report, self.config)

    def append_skipped(self, report):
        if hasattr(report, "wasxfail"):
            self.xfailed += 1
            self._appendrow('XFailed', report, self.config)
        else:
            self.skipped += 1
            self._appendrow('Skipped', report, self.config)

    def append_other(self, report):
        # For now, the only "other" the plugin give support is rerun
        self.rerun += 1
        self._appendrow('Rerun', report, self.config)

    def _generate_detail(self):
        tests = []
        sorted_result = self.sort_result()
        for cid, (cls, cls_results) in enumerate(sorted_result, 1):
            # subtotal for a class
            np = nf = ne = ns = 0
            for result in cls_results:
                if result.outcome == "Passed":  # pass
                    np += 1
                elif result.outcome in ["Failed", "XPassed", "XFailed"]:  # fail
                    nf += 1
                elif result.outcome == "Error":  # error
                    ne += 1
                elif result.outcome == "Skipped":  # skip
                    ns += 1

            # format class description
            name = cls
            doc = ""
            desc = '%s: %s' % (name, doc) if doc else name

            test = {
                'summary': {
                    'desc': desc,
                    'count': np + nf + ne + ns,
                    'pass': np,
                    'fail': nf,
                    'error': ne,
                    'skip': ns,
                    'cid': 'testclass%s' % cid,
                    'status': (ne and "error") or (nf and "fail") or (ns and "skip") or "pass"
                }, 'detail': []
            }

            for tid, result in enumerate(cls_results, 1):
                test['detail'].append(result.output(cid, tid))
                # ****修改添加接口请求的请求与响应信息详情
                html_content = cls_results[tid - 1].row_extra
                test['detail'][tid - 1]["output"] = html_content
            tests.append(test)

        return tests

    def sort_result(self):
        result_map = {}
        for result in self.results:
            if len(result.report.nodeid.split("::")) >= 2:
                cls = result.report.nodeid.split("::")[1]
            else:
                cls = result.report.nodeid.split("::")[0]
            result_map.setdefault(cls, []).append(result)
        return result_map.items()

    def _generate_report(self, session):
        suite_stop_time = datetime.datetime.now()
        duration = str((suite_stop_time - self.suite_start_time).total_seconds())[:-4] + "（单位：秒）"
        count = self.passed + self.failed + self.xpassed + self.xfailed + self.skipped + self.errors
        environment = self._generate_environment(session.config)
        tests = self._generate_detail()

        report_content = {
            "generator": "PyTestReport %s" % runner.__version__,
            "title": "%s" % self.config.getoption('pytest_title'),
            "description": "%s" % self.config.getoption('pytest_desc'),
            "environment": environment,
            "report_summary": {
                "start_time": self.suite_start_time.strftime('%Y-%m-%d %H:%M:%S'),
                "duration": duration,
                "suite_count": len(tests),
                "status": {
                    "pass": self.passed,
                    "fail": self.failed + self.xfailed + self.xpassed,
                    "error": self.errors,
                    "skip": self.skipped,
                    "count": count
                }
            }, "report_detail": {
                "tests": tests,
                "count": count,
                "pass": self.passed,
                "fail": self.failed + self.xfailed + self.xpassed,
                "error": self.errors,
                "skip": self.skipped,
            }
        }

        return report_content

    def _generate_environment(self, config):
        if not hasattr(config, '_metadata') or config._metadata is None:
            return []
        return config._metadata

    def _save_report(self, report_content, theme=None, stylesheet=None, template=None, javascript=None):

        dir_name = os.path.dirname(self.html_file)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(self.html_file, 'wb') as fp:
            ht_runner = runner.HTMLTestRunner(fp, theme=theme, stylesheet=stylesheet, template=template, javascript=javascript)
            report_content['stylesheet'] = ht_runner.get_stylesheet()
            report_content['javascript'] = ht_runner.get_javascript()
            return ht_runner.generate_report(report_content)

    def pytest_runtest_logreport(self, report):
        if report.passed:
            self.append_passed(report)
        elif report.failed:
            self.append_failed(report)
        elif report.skipped:
            self.append_skipped(report)
        else:
            self.append_other(report)

    def pytest_collectreport(self, report):
        if report.failed:
            self.append_failed(report)

    def pytest_sessionstart(self, session):
        self.suite_start_time = datetime.datetime.now()

    def pytest_sessionfinish(self, session):
        report_data = self._generate_report(session)
        theme = self.config.getoption('pytest_theme')
        stylesheet = self.config.getoption('pytest_stylesheet')
        template = self.config.getoption('pytest_template')
        javascript = self.config.getoption('pytest_javascript')
        self._save_report(report_data, theme, stylesheet, template, javascript)

    def pytest_terminal_summary(self, terminalreporter):
        terminalreporter.write_sep('-', 'generated html file: {0}'.format(self.html_file))
