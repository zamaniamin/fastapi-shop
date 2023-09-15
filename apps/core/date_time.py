from datetime import datetime


class DateTime:

    @classmethod
    def string(cls, obj: datetime):
        """
        Convert a datetime object to a formatted string.

        This method takes a datetime object `obj` and converts it into a string
        in the format 'YYYY-MM-DD HH:MM:SS'. If `obj` is None or evaluates to False,
        it returns None.

        Parameters:
        cls (object): An instance of the class (although this argument is not used).
        obj (datetime or None): The datetime object to be converted to a string.

        Returns:
        str or None: A formatted string representation of the datetime object,
                     or None if the input is None or evaluates to False.
        """

        return obj.strftime('%Y-%m-%d %H:%M:%S') if obj else None

    @classmethod
    def now(cls):
        return datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
