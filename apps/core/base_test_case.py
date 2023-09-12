from datetime import datetime


class BaseTestCase:

    @staticmethod
    def assert_datetime_format(date):
        formatted_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
        assert date == formatted_date
