from services.alert_engine import AlertManager, get_alert
from services.severity import get_severity


def test_alert_manager_paths():
    manager = AlertManager()
    assert "Normal" in manager.get_alert(0, 0.9)
    assert "Mild Impact Warning" in manager.get_alert(1, 0.9)
    assert "Low Confidence" in manager.get_alert(1, 0.1)
    assert "SEVERE CRASH" in manager.get_alert(2, 0.9)
    assert "Container Shift" in manager.get_alert(3, 0.5)


def test_alert_module_level_function():
    assert isinstance(get_alert(0, 0.5), str)


def test_severity_levels_via_manager_and_wrapper():
    manager = AlertManager()
    assert manager.get_severity(0.2) == ("Normal", "green")
    assert manager.get_severity(0.5) == ("Warning", "orange")
    assert manager.get_severity(0.9) == ("Critical", "red")
    assert get_severity(0.5) == ("Warning", "orange")
