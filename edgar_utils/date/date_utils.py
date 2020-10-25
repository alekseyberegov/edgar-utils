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
        """
            Returns
            -------
            int
                the quarter number 1..4
        """
        return  (self.date_inst.month - 1) // 3 + 1

    def diff_quarter(self, from_date: 'Date') -> int:
        """
            Returns the difference between the quarter number of this date and that of from_date

            Parameters
            ----------
            from_date : Date
                the date from which quarters are counted

            Return
            ------
            int
                the difference between the quarter number of this date and that of from_date
        """
        return self.quarter() - from_date.quarter()
