"Base file containing OncoPlotCreator"

import openpyxl
import pandas as pd
from openpyxl.utils.dataframe import dataframe_to_rows


class OncoPlotCreator:
    """Creates an oncoplot from a dataframe
    containing respective rows and columns with hexcolor data

    :param df: pandas dataframe containing hexcolor data [pandas.DataFrame]
    :param cell_size: size of each cell in pixels [int]
    :param workbook: openpyxl workbook object [openpyxl.Workbook]
    :param offset: number of rows to offset inserted data [int]

    :Example:
    .. code-block:: python

        opc = OncoPlotCreator(df=my_df, cell_size=60, workbook=wb, offset=10)
        opc.gen_base_oncoplot()
        opc.save(filename="my_oncoplot.xlsx")

    """

    CELL_SIZE: int
    OUT_PATH: str = None
    DF: pd.DataFrame
    WORKBOOK: openpyxl.Workbook
    WORKSHEET: openpyxl.Workbook.active
    OFFSET: int

    def __init__(
        self,
        df: pd.DataFrame,
        cell_size: int = 60,
        workbook: openpyxl.Workbook = openpyxl.Workbook(),
        offset: int = 10,
    ) -> None:
        """Initializes a OncoPlotCreator class, expects `df`, `cell_size`, `workbook`, `offset`
        which is row offset inserted at beginning of self.WS"""
        self.DF = df
        self.CELL_SIZE = cell_size
        self.WORKBOOK = workbook
        self.WORKSHEET = self.WORKBOOK.active
        self.OFFSET = offset
        self._load_df_to_ws()

    def _load_df_to_ws(self):
        """loads self.DF to self.WS"""
        for row in dataframe_to_rows(self.DF, index=True):
            self.WORKSHEET.append(row)

    def _insert_offset(self):
        for i in range(0, self.OFFSET):
            self.WORKSHEET.insert_rows(0)

    def gen_base_oncoplot(self):
        """Generates base oncoplot from self.DF
        expects self.DF to be loaded to self.WS
        """
        thin = openpyxl.styles.Side(border_style="thin", color="ffffff")
        self._insert_offset()
        _c = 1
        for row in self.WORKSHEET.iter_rows():
            self.WORKSHEET.row_dimensions[_c].height = self.CELL_SIZE
            for cell in row:
                if type(cell.value) == str:
                    cell.fill = openpyxl.styles.PatternFill(
                        patternType="solid", fgColor=cell.value.replace("#", "")
                    )
                    cell.value = ""
                    cell.border = openpyxl.styles.Border(
                        top=thin, bottom=thin, right=thin, left=thin
                    )
            _c += 1

    def save(self, filename: str) -> None:
        """saves generated workbook to file
        :param filename: filename to save workbook to [str]
        """
        self.WORKBOOK.save(filename=filename)
