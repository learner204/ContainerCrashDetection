from dashboard.confidence_gauge import confidence_gauge
from dashboard import severity_bar as severity_bar_module


def test_confidence_gauge_returns_plotly_figure():
    fig = confidence_gauge(0.73)
    fig_dict = fig.to_dict()

    assert fig_dict["data"][0]["type"] == "indicator"
    assert fig_dict["data"][0]["value"] == 73.0


def test_severity_bar_calls_streamlit_markdown(monkeypatch):
    calls = {}

    def fake_markdown(content, unsafe_allow_html=False):
        calls["content"] = content
        calls["unsafe"] = unsafe_allow_html

    monkeypatch.setattr(severity_bar_module.st, "markdown", fake_markdown)

    severity_bar_module.severity_bar("Warning", "orange")

    assert "Severity Level: Warning" in calls["content"]
    assert "background-color:orange" in calls["content"]
    assert calls["unsafe"] is True
