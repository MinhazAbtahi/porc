from datetime import datetime

def create_timestamp(datetime_obj=datetime.now()):
    """
    If given a `datetime_obj`, converts it to milliseconds since epoch.
    Else, returns the milliseconds between now and the epoch.
    """
    epoch = datetime.utcfromtimestamp(0)
    delta = datetime_obj - epoch
    seconds = delta.total_seconds()
    milliseconds = seconds * 1000
    return int(milliseconds)

def resolve_futures(futures):
    """
    Resolve futures en masse, throwing a fit if any have non-20X responses.
    """
    results = []
    for future in futures:
        result = future.result()
        # any failure will automatically escalate to the next scope
        result.raise_for_status()
        results.append(result)
    return results