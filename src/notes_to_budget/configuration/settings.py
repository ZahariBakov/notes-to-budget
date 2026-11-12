"""The general settings of one person's budget."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    language: str
    currency_symbol: str
    notes_folder_name: str
    ledger_folder_name: str
    review_folder_name: str
    workbook_file_name_pattern: str
    """File name of the workbook; ``{year}`` is replaced by the year."""

    def workbook_file_name(self, year: int) -> str:
        return self.workbook_file_name_pattern.format(year=year)
