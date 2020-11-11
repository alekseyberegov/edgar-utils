from typing import List

"""
    The list of years used for testing
"""
YEAR_LIST: List[int] = [2017, 2018, 2019, 2020]

YEAR_COUNT: int = len(YEAR_LIST)

YEAR_MAX: int = max(YEAR_LIST)

"""
    The list of quarters named as in Edgar INDEX
"""
QUARTER_LIST: List[str] = ['QTR1', 'QTR2', 'QTR3', 'QTR4']

"""
    The number of test files per the quarter directory in test repo
"""
FILE_PER_DIR = 3

"""
    The list of year/quarter to simulate EDGAR index repository
"""
EDGAR_QUARTER: List[str] = ['2017-QTR4-92', '2018-QTR1-25']