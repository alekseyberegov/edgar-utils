from datetime import date

class Date(object):
    """ 
        A date class that provides a number of useful methods to track financial fillings
    """
    def __init__(self, date_str: str) -> None:
        """
            Parameters
            ----------
            date_str : str
            The date string in YYYY-MM-DD format
        """
        self.date_inst = date.fromisoformat(date_str)
        super().__init__()

    def __str__(self) -> str:
        """
            Converts this date object into a YYYY-MM-DD string

            Returns
            -------
            str
                the string representation of this date object
        """
        return self.date_inst.__str__()

    def quarter(self):
        return  (self.date_inst.month - 1) // 3 + 1