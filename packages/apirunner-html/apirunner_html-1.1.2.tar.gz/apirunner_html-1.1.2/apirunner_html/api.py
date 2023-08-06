from .runner import HTMLTestRunner

__all__ = ["make_report"]


def make_report(stream, data, theme=None, stylesheet=None, template=None, javascript=None):
    test_runner = HTMLTestRunner(stream, theme=theme, stylesheet=stylesheet, template=template, javascript=javascript)
    data['stylesheet'] = test_runner.get_stylesheet()
    data['javascript'] = test_runner.get_javascript()
    return test_runner.generate_report(data)
