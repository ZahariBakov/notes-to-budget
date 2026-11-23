/**
 * The month screen and the list of entries: read a month, change or delete
 * one entry.
 *
 * An entry is found by its number (the last column of "Entries"), not by its
 * row, so sorting or moving rows in the sheet does no harm. Rows typed by
 * hand get a number the first time a month is read.
 */

/** The overview and the entries of one month of the budget's year. */
function getMonthDetails(monthNumber) {
  const texts = currentTexts();
  if (!isPrepared()) {
    throw new Error(texts.notPreparedYet);
  }
  return monthDetails(budgetSpreadsheet(), Number(monthNumber), texts);
}

/**
 * Replaces an entry with what the person changed. The time it was first
 * entered stays, so the morning check still counts it the same way.
 */
function updateEntry(entryId, entry, viewedMonth) {
  const texts = currentTexts();
  const spreadsheet = budgetSpreadsheet();
  const settings = readSettings(findSheetByRole(spreadsheet, 'settings'), texts);
  const checkedEntry = checkEntry(entry, settings, texts);
  changeEntriesSheet(spreadsheet, function (entriesSheet) {
    const row = findEntryRow(entriesSheet, entryId, texts);
    entriesSheet.getRange(row, 1, 1, ENTRY_ONE_OFF_COLUMN).setValues([[
      checkedEntry.date,
      checkedEntry.amount,
      checkedEntry.categoryName,
      checkedEntry.accountName,
      checkedEntry.toAccountName,
      checkedEntry.description,
      checkedEntry.oneOff,
    ]]);
  });
  return everythingAfterChange(spreadsheet, settings, viewedMonth, texts);
}

function deleteEntry(entryId, viewedMonth) {
  const texts = currentTexts();
  const spreadsheet = budgetSpreadsheet();
  const settings = readSettings(findSheetByRole(spreadsheet, 'settings'), texts);
  changeEntriesSheet(spreadsheet, function (entriesSheet) {
    entriesSheet.deleteRow(findEntryRow(entriesSheet, entryId, texts));
  });
  return everythingAfterChange(spreadsheet, settings, viewedMonth, texts);
}

function changeEntriesSheet(spreadsheet, change) {
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    change(findSheetByRole(spreadsheet, 'entries'));
    SpreadsheetApp.flush();
  } finally {
    lock.releaseLock();
  }
}

/** What the page shows again after a change: the viewed month, today's month and the checks. */
function everythingAfterChange(spreadsheet, settings, viewedMonth, texts) {
  const allEntries = readAllEntries(findSheetByRole(spreadsheet, 'entries'));
  const today = new Date();
  return {
    details: monthDetails(spreadsheet, Number(viewedMonth), texts),
    month: monthOverview(spreadsheet, today.getFullYear(), today.getMonth() + 1, texts),
    checks: checkOverview(settings, allEntries,
        readAllChecks(findSheetByRole(spreadsheet, 'checks')), texts.transfer, today),
    creditCardDebts: creditCardDebts(settings, allEntries, texts.transfer),
  };
}

function monthDetails(spreadsheet, monthNumber, texts) {
  const year = budgetYear();
  const entriesSheet = findSheetByRole(spreadsheet, 'entries');
  giveNumbersToEntries(entriesSheet);
  return {
    monthNumber: monthNumber,
    overview: monthOverview(spreadsheet, year, monthNumber, texts),
    entries: entriesOfMonth(entriesSheet, year, monthNumber),
  };
}

/** The entries of one month, the newest first. */
function entriesOfMonth(entriesSheet, year, monthNumber) {
  const rowCount = entriesSheet.getLastRow() - 1;
  if (rowCount <= 0) {
    return [];
  }
  return entriesSheet.getRange(2, 1, rowCount, ENTRY_COLUMN_COUNT).getValues()
      .filter(function (row) {
        const date = row[ENTRY_DATE_COLUMN - 1];
        return date instanceof Date && date.getFullYear() === year &&
            date.getMonth() === monthNumber - 1 && row[ENTRY_ID_COLUMN - 1] !== '';
      })
      .map(function (row) {
        const enteredAt = row[ENTRY_ENTERED_AT_COLUMN - 1];
        return {
          id: String(row[ENTRY_ID_COLUMN - 1]),
          dayKey: dayKey(row[ENTRY_DATE_COLUMN - 1]),
          amount: Number(row[ENTRY_AMOUNT_COLUMN - 1]) || 0,
          category: String(row[ENTRY_CATEGORY_COLUMN - 1]),
          account: String(row[ENTRY_ACCOUNT_COLUMN - 1]),
          toAccount: String(row[ENTRY_TO_ACCOUNT_COLUMN - 1]),
          description: String(row[ENTRY_DESCRIPTION_COLUMN - 1]),
          oneOff: row[ENTRY_ONE_OFF_COLUMN - 1] === true,
          enteredAt: enteredAt instanceof Date ? enteredAt.getTime() : 0,
        };
      })
      .sort(function (first, second) {
        if (first.dayKey !== second.dayKey) {
          return first.dayKey < second.dayKey ? 1 : -1;
        }
        return second.enteredAt - first.enteredAt;
      });
}

/** Gives a number to every entry that has a date but no number yet (rows typed by hand). */
function giveNumbersToEntries(entriesSheet) {
  const rowCount = entriesSheet.getLastRow() - 1;
  if (rowCount <= 0) {
    return;
  }
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const dates = entriesSheet.getRange(2, ENTRY_DATE_COLUMN, rowCount, 1).getValues();
    const idRange = entriesSheet.getRange(2, ENTRY_ID_COLUMN, rowCount, 1);
    const ids = idRange.getValues();
    let changed = false;
    ids.forEach(function (id, index) {
      if (id[0] === '' && dates[index][0] instanceof Date) {
        id[0] = Utilities.getUuid();
        changed = true;
      }
    });
    if (changed) {
      idRange.setValues(ids);
      SpreadsheetApp.flush();
    }
  } finally {
    lock.releaseLock();
  }
}

function findEntryRow(entriesSheet, entryId, texts) {
  const rowCount = entriesSheet.getLastRow() - 1;
  if (rowCount > 0 && entryId) {
    const ids = entriesSheet.getRange(2, ENTRY_ID_COLUMN, rowCount, 1).getValues();
    for (let index = 0; index < ids.length; index++) {
      if (String(ids[index][0]) === String(entryId)) {
        return index + 2;
      }
    }
  }
  throw new Error(texts.entryNotFound);
}
