from datetime import datetime

from apps.core.date_time import DateTime


class BaseTestCase:

    @staticmethod
    def assert_datetime_format(date: str | datetime):
        if isinstance(date, datetime):
            date = DateTime.string(date)

        formatted_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
        assert date == formatted_date

    @staticmethod
    def convert_datetime_to_string(date):
        return DateTime.string(date)
