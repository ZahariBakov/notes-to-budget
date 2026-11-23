/**
 * Brings older entries into "Entries", for example the months written
 * down before the app existed.
 *
 * The entries come from imported_entries.js, a file made on the computer
 * and kept out of git like personal_settings.js:
 *
 *   const IMPORTED_ENTRIES = [
 *     { date: '2026-01-04', amount: 5, category: 'Groceries', account: 'Cash',
 *       toAccount: '', description: 'bread', oneOff: false, id: '…' },
 *   ];
 *
 * The menu shows "Import older entries" only while that file is there.
 * An entry whose number is already in the sheet is skipped, so importing
 * twice does not write anything twice.
 */

function hasEntriesToImport() {
  return typeof IMPORTED_ENTRIES !== 'undefined' && Array.isArray(IMPORTED_ENTRIES);
}

/** From the menu, or from the script editor (Run > importEntries); there the result is in the log. */
function importEntries() {
  const texts = currentTexts();
  if (!hasEntriesToImport()) {
    tell(texts.nothingToImport);
    return;
  }
  const spreadsheet = budgetSpreadsheet();
  const settings = readSettings(findSheetByRole(spreadsheet, 'settings'), texts);
  const problems = problemsInImportedEntries(IMPORTED_ENTRIES, settings, texts);
  if (problems.length > 0) {
    tell(texts.importProblems + '\n\n' + problems.slice(0, 15).join('\n'));
    return;
  }

  let written = 0;
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const entriesSheet = findSheetByRole(spreadsheet, 'entries');
    const knownIds = {};
    const rowCount = entriesSheet.getLastRow() - 1;
    if (rowCount > 0) {
      entriesSheet.getRange(2, ENTRY_ID_COLUMN, rowCount, 1).getValues().forEach(function (row) {
        knownIds[String(row[0])] = true;
      });
    }
    const rows = IMPORTED_ENTRIES
        .filter(function (entry) { return !knownIds[entry.id]; })
        .map(function (entry) {
          return [dateFromText(entry.date), entry.amount, entry.category, entry.account,
            entry.toAccount || '', entry.description || '', entry.oneOff === true, '', entry.id];
        });
    if (rows.length > 0) {
      const firstRow = firstFreeRow(entriesSheet);
      makeRoomForRow(entriesSheet, firstRow + rows.length - 1, ENTRY_ONE_OFF_COLUMN);
      entriesSheet.getRange(firstRow, 1, rows.length, ENTRY_COLUMN_COUNT).setValues(rows);
      SpreadsheetApp.flush();
    }
    written = rows.length;
  } finally {
    lock.releaseLock();
  }
  tell(fill(texts.importedEntries, {
    count: written, skipped: IMPORTED_ENTRIES.length - written,
  }));
}

/** A message box in the spreadsheet; the script editor has none, so it goes to the log too. */
function tell(message) {
  console.log(message);
  try {
    SpreadsheetApp.getUi().alert(message);
  } catch (error) {
    // Run from the script editor: the log above has the message.
  }
}

/** Every entry must have a date, an amount, and a category and accounts from the settings. */
function problemsInImportedEntries(entries, settings, texts) {
  const categories = {};
  settings.categories.forEach(function (category) { categories[category.name] = true; });
  categories[texts.transfer] = true;
  const accounts = {};
  settings.accounts.forEach(function (account) { accounts[account.name] = true; });

  const problems = [];
  entries.forEach(function (entry, index) {
    const where = (index + 1) + ' (' + entry.date + ' ' + entry.amount + ' ' +
        entry.description + '): ';
    if (!/^\d{4}-\d{2}-\d{2}$/.test(entry.date) || typeof entry.amount !== 'number' ||
        !entry.id) {
      problems.push(where + texts.importBadEntry);
    } else if (!categories[entry.category]) {
      problems.push(where + fill(texts.importUnknownCategory, { name: entry.category }));
    } else if (!accounts[entry.account] ||
        (entry.category === texts.transfer && !accounts[entry.toAccount])) {
      problems.push(where + fill(texts.importUnknownAccount, {
        name: accounts[entry.account] ? entry.toAccount : entry.account,
      }));
    }
  });
  return problems;
}

function dateFromText(text) {
  return new Date(Number(text.slice(0, 4)), Number(text.slice(5, 7)) - 1,
      Number(text.slice(8, 10)));
}

/** fill('{count} entries', { count: 3 }) gives '3 entries'. */
function fill(text, values) {
  return text.replace(/\{(\w+)\}/g, function (whole, name) {
    return values[name] !== undefined ? values[name] : whole;
  });
}
