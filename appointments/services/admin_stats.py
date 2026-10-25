import base64
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .dashboard_stats import monthly_appointment_counts


def count_appointments_by_month(*, months_back: int = 12):
    """
    Return (labels, counts) for the last `months_back` natural months, current
    month included. Every month is present (count 0 when empty). Labels: YYYY-MM
    """
    return monthly_appointment_counts(months_back)


def render_monthly_chart_png_base64(*, months_back: int = 12):
    """
    Returns a data URI: data:image/png;base64,...
    """
    labels, counts = count_appointments_by_month(months_back=months_back)

    plt.figure(figsize=(10, 5))
    plt.bar(labels, counts)
    plt.xticks(rotation=45)
    plt.title(f"Citas por mes (últimos {months_back} meses)")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()

    return f"data:image/png;base64,{img_b64}"