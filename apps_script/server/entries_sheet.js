/**
 * The "Entries" sheet: every expense, income, saving and transfer, one row each.
 *
 * It is the only place where money is written down. The month sheets and
 * the year sheet only add it up.
 */

// Column numbers of the entries sheet.
const ENTRY_DATE_COLUMN = 1;
const ENTRY_AMOUNT_COLUMN = 2;
const ENTRY_CATEGORY_COLUMN = 3;
const ENTRY_ACCOUNT_COLUMN = 4;
const ENTRY_TO_ACCOUNT_COLUMN = 5;
const ENTRY_DESCRIPTION_COLUMN = 6;
const ENTRY_ONE_OFF_COLUMN = 7;
const ENTRY_ENTERED_AT_COLUMN = 8;
const ENTRY_ID_COLUMN = 9;
const ENTRY_COLUMN_COUNT = 9;

function prepareEntriesSheet(sheet, texts) {
  const header = [texts.date, texts.amount, texts.category, texts.account, texts.toAccount,
    texts.description, texts.oneOff, texts.enteredAt, texts.entryId];
  writeHeaderRow(sheet, header);

  const allRowsBelowHeader = function (column) {
    return sheet.getRange(2, column, sheet.getMaxRows() - 1, 1);
  };
  allRowsBelowHeader(ENTRY_DATE_COLUMN).setNumberFormat('dd.mm.yyyy');
  allRowsBelowHeader(ENTRY_AMOUNT_COLUMN).setNumberFormat(moneyFormat());
  allRowsBelowHeader(ENTRY_ONE_OFF_COLUMN).insertCheckboxes();
  allRowsBelowHeader(ENTRY_ENTERED_AT_COLUMN).setNumberFormat('dd.mm.yyyy hh:mm');
  setColumnWidths(sheet, [95, 100, 190, 150, 150, 260, 95, 135, 110]);
}

/**
 * The first row after the last filled date. getLastRow() would not do: the
 * one-off column has a checkbox on every row, and an empty checkbox still
 * counts as filled, so new rows would land at the very bottom.
 */
function firstFreeRow(sheet) {
  const dates = sheet.getRange(1, ENTRY_DATE_COLUMN, sheet.getMaxRows(), 1).getValues();
  let lastFilled = 1;
  dates.forEach(function (row, index) {
    if (row[0] !== '') {
      lastFilled = index + 1;
    }
  });
  return lastFilled + 1;
}

/** A bold dark header row that stays in place while scrolling. */
function writeHeaderRow(sheet, header) {
  sheet.getRange(1, 1, 1, header.length).setValues([header])
      .setFontWeight('bold').setBackground('#263238').setFontColor('#ffffff');
  sheet.setFrozenRows(1);
}

function setColumnWidths(sheet, widths) {
  widths.forEach(function (width, index) {
    sheet.setColumnWidth(index + 1, width);
  });
}
