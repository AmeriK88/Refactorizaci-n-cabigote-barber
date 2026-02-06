from collections import defaultdict
from datetime import timedelta
import base64
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from django.utils import timezone
from django.utils.timezone import localtime

from appointments.models import Cita


def count_appointments_by_month(*, months_back: int = 12):
    """
    Return (labels, counts) for last `months_back` months.
    Labels format: YYYY-MM
    """
    start = timezone.now() - timedelta(days=30 * months_back)

    fechas = (
        Cita.objects.filter(fecha__gte=start, fecha__isnull=False)
        .values_list("fecha", flat=True)
    )

    counter = defaultdict(int)
    for dt in fechas:
        dt_local = localtime(dt)
        label = f"{dt_local.year}-{dt_local.month:02d}"
        counter[label] += 1

    labels = sorted(counter.keys())
    counts = [counter[l] for l in labels]

    if not labels:
        return ["No data"], [0]

    return labels, counts


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