from datetime import datetime, timedelta

def uuid1_time_to_datetime(time: int):
    """
    :param time: time in seconds
    :return: the datetime formatted date
    """

    return datetime(1582, 10, 15) + timedelta(microseconds=time // 10)