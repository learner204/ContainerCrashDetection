from services.alert_engine import AlertManager

def get_severity(confidence):
    return AlertManager().get_severity(confidence)
