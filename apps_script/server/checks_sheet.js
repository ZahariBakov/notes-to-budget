/**
 * The "Checks" sheet: the morning balances, one row per account and day.
 *
 * The app fills it from the check screen: what the account really holds,
 * what the entries say it should hold, and the difference between them.
 */

const CHECK_DATE_COLUMN = 1;
const CHECK_ACCOUNT_COLUMN = 2;
const CHECK_ACTUAL_COLUMN = 3;
const CHECK_EXPECTED_COLUMN = 4;
const CHECK_DIFFERENCE_COLUMN = 5;
const CHECK_ENTERED_AT_COLUMN = 6;

function prepareChecksSheet(sheet, texts) {
  writeHeaderRow(sheet, [texts.date, texts.account, texts.actual, texts.expected,
    texts.difference, texts.enteredAt]);

  const rowsBelowHeader = sheet.getMaxRows() - 1;
  sheet.getRange(2, CHECK_DATE_COLUMN, rowsBelowHeader, 1).setNumberFormat('dd.mm.yyyy');
  sheet.getRange(2, CHECK_ACTUAL_COLUMN, rowsBelowHeader, 3).setNumberFormat(moneyFormat());
  sheet.getRange(2, CHECK_ENTERED_AT_COLUMN, rowsBelowHeader, 1)
      .setNumberFormat('dd.mm.yyyy hh:mm');
  setColumnWidths(sheet, [95, 150, 110, 110, 110, 135]);
}
