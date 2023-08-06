def build_notify_list(notify):
    if notify is None:
        return []

    elif isinstance(notify, str):
        return [notify]

    else:
        return notify
