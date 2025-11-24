def normalize_price_range(raw):
    if raw is None:
        return None

    lowered = raw.lower().replace(" ", "")
    if lowered in ("неустановлен", "неустановлено"):
        return "не установлен"

    value = raw.replace(" ", "")
    if value.count("-") != 1:
        return None

    start, end = value.split("-", 1)
    if not start.isdigit() or not end.isdigit():
        return None

    start_val = int(start)
    end_val = int(end)
    if start_val <= 0 or end_val <= 0 or start_val >= end_val:
        return None

    return f"{start_val}-{end_val}"


def normalize_event_time(raw):
    if raw is None:
        return None

    lowered = raw.lower().replace(" ", "")
    if lowered in ("неустановлено", "неустановлен"):
        return "не установлено"

    value = raw.replace(" ", "")
    if value.count(":") != 1:
        return None

    day, month = value.split(":", 1)
    if not day.isdigit() or not month.isdigit():
        return None

    day_val = int(day)
    month_val = int(month)
    if month_val < 1 or month_val > 12:
        return None
    if day_val < 1 or day_val > 31:
        return None

    return f"{day_val:02}:{month_val:02}"
