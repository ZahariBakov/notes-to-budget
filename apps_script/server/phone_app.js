/**
 * The phone app: the page it shows and the calls the page makes.
 *
 * The page (client/index.html) calls getStartData() when it opens and
 * saveEntry() for every new entry, through google.script.run.
 */

const FREQUENT_CATEGORY_COUNT = 8;
const DAYS_THAT_DECIDE_FREQUENT_CATEGORIES = 90;

/** Shows the page when the app's address is opened. */
function doGet() {
  return HtmlService.createTemplateFromFile('client/index')
      .evaluate()
      .setTitle(currentTexts().appTitle)
      .addMetaTag('viewport', 'width=device-width, initial-scale=1, viewport-fit=cover')
      .addMetaTag('mobile-web-app-capable', 'yes')
      .addMetaTag('apple-mobile-web-app-capable', 'yes');
}

/** Puts one HTML file into another: <?!= include('client/styles') ?> */
function include(fileName) {
  return HtmlService.createHtmlOutputFromFile(fileName).getContent();
}

/** Everything the page needs to show the new entry screen. */
function getStartData() {
  const texts = currentTexts();
  if (!isPrepared()) {
    throw new Error(texts.notPreparedYet);
  }
  const spreadsheet = budgetSpreadsheet();
  const settings = readSettings(findSheetByRole(spreadsheet, 'settings'), texts);
  const entriesSheet = findSheetByRole(spreadsheet, 'entries');
  const recentEntries = readRecentEntries(entriesSheet);
  const allEntries = readAllEntries(entriesSheet);
  const today = new Date();

  return {
    checks: checkOverview(settings, allEntries,
        readAllChecks(findSheetByRole(spreadsheet, 'checks')), texts.transfer, today),
    creditCardDebts: creditCardDebts(settings, allEntries, texts.transfer),
    texts: texts,
    currencySymbol: currencySymbol(),
    categories: settings.categories,
    transfer: { name: texts.transfer, kind: 'transfer', icon: TRANSFER_ICON, group: '' },
    frequentCategoryNames: frequentCategoryNames(recentEntries, settings.categories,
        texts.transfer),
    accounts: settings.accounts,
    lastAccountName: recentEntries.length > 0 ? recentEntries[recentEntries.length - 1].account
      : '',
    month: monthOverview(spreadsheet, today.getFullYear(), today.getMonth() + 1, texts),
  };
}

/**
 * Writes one entry into the "Entries" sheet.
 *
 * entry: { amount, categoryName, accountName, toAccountName, description,
 * oneOff, date: 'YYYY-MM-DD' or '' for today }.
 * Returns the month overview, the checks and what is owed on credit cards
 * after the entry, so the page can show them.
 */
function saveEntry(entry) {
  const texts = currentTexts();
  if (!isPrepared()) {
    throw new Error(texts.notPreparedYet);
  }
  const spreadsheet = budgetSpreadsheet();
  const settings = readSettings(findSheetByRole(spreadsheet, 'settings'), texts);
  const checkedEntry = checkEntry(entry, settings, texts);

  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const entriesSheet = findSheetByRole(spreadsheet, 'entries');
    const row = Math.max(entriesSheet.getLastRow(), 1) + 1;
    entriesSheet.getRange(row, 1, 1, ENTRY_COLUMN_COUNT).setValues([[
      checkedEntry.date,
      checkedEntry.amount,
      checkedEntry.categoryName,
      checkedEntry.accountName,
      checkedEntry.toAccountName,
      checkedEntry.description,
      checkedEntry.oneOff,
      new Date(),
      Utilities.getUuid(),
    ]]);
    SpreadsheetApp.flush();
  } finally {
    lock.releaseLock();
  }

  const allEntries = readAllEntries(findSheetByRole(spreadsheet, 'entries'));
  return {
    month: monthOverview(spreadsheet, checkedEntry.date.getFullYear(),
        checkedEntry.date.getMonth() + 1, texts),
    checks: checkOverview(settings, allEntries,
        readAllChecks(findSheetByRole(spreadsheet, 'checks')), texts.transfer, new Date()),
    creditCardDebts: creditCardDebts(settings, allEntries, texts.transfer),
  };
}

/**
 * Writes the morning check: what each account really holds now.
 *
 * balances: [{ accountName, actual }]; accounts left empty are not sent.
 * Every check is kept as its own row, so the history stays in the sheet.
 * Returns the checks after saving.
 */
function saveChecks(balances) {
  const texts = currentTexts();
  if (!isPrepared()) {
    throw new Error(texts.notPreparedYet);
  }
  const spreadsheet = budgetSpreadsheet();
  const settings = readSettings(findSheetByRole(spreadsheet, 'settings'), texts);
  const checkedNames = settings.accounts
      .filter(function (account) { return account.reconciled; })
      .map(function (account) { return account.name; });
  const checked = (balances || []).filter(function (balance) {
    return checkedNames.indexOf(balance.accountName) !== -1 && isFinite(Number(balance.actual)) &&
        String(balance.actual) !== '';
  });
  if (checked.length === 0) {
    throw new Error(texts.nothingToCheck);
  }

  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const entriesSheet = findSheetByRole(spreadsheet, 'entries');
    const checksSheet = findSheetByRole(spreadsheet, 'checks');
    const now = new Date();
    const before = checkOverview(settings, readAllEntries(entriesSheet),
        readAllChecks(checksSheet), texts.transfer, now);
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const rows = checked.map(function (balance) {
      const actual = roundToCents(Number(balance.actual));
      const account = before.find(function (overview) {
        return overview.name === balance.accountName;
      });
      const expected = account && account.expected !== null ? account.expected : '';
      const difference = expected === '' ? '' : roundToCents(actual - expected);
      return [today, balance.accountName, actual, expected, difference, now];
    });
    const firstRow = Math.max(checksSheet.getLastRow(), 1) + 1;
    checksSheet.getRange(firstRow, 1, rows.length, rows[0].length).setValues(rows);
    SpreadsheetApp.flush();
  } finally {
    lock.releaseLock();
  }

  return checkOverview(settings, readAllEntries(findSheetByRole(spreadsheet, 'entries')),
      readAllChecks(findSheetByRole(spreadsheet, 'checks')), texts.transfer, new Date());
}

/** Checks the entry again on the server: the page is not the only way to call this. */
function checkEntry(entry, settings, texts) {
  const amount = Number(entry.amount);
  if (!isFinite(amount) || amount === 0) {
    throw new Error(texts.amountMissing);
  }
  const isTransfer = entry.categoryName === texts.transfer;
  const categoryNames = settings.categories.map(function (category) { return category.name; });
  if (!isTransfer && categoryNames.indexOf(entry.categoryName) === -1) {
    throw new Error(texts.categoryMissing);
  }
  const accountNames = settings.accounts.map(function (account) { return account.name; });
  if (accountNames.indexOf(entry.accountName) === -1) {
    throw new Error(texts.accountMissing);
  }
  let toAccountName = '';
  if (isTransfer) {
    if (accountNames.indexOf(entry.toAccountName) === -1) {
      throw new Error(texts.toAccountMissing);
    }
    if (entry.toAccountName === entry.accountName) {
      throw new Error(texts.sameAccounts);
    }
    toAccountName = entry.toAccountName;
  }
  return {
    date: readEntryDate(entry.date, texts),
    amount: Math.round(amount * 100) / 100,
    categoryName: entry.categoryName,
    accountName: entry.accountName,
    toAccountName: toAccountName,
    description: String(entry.description || '').trim(),
    oneOff: entry.oneOff === true,
  };
}

/** A date written as YYYY-MM-DD, or today when it is empty. */
function readEntryDate(written, texts) {
  const today = new Date();
  if (!written) {
    return new Date(today.getFullYear(), today.getMonth(), today.getDate());
  }
  const parts = /^(\d{4})-(\d{2})-(\d{2})$/.exec(written);
  if (!parts) {
    throw new Error(texts.dateNotValid);
  }
  const date = new Date(Number(parts[1]), Number(parts[2]) - 1, Number(parts[3]));
  if (date.getMonth() !== Number(parts[2]) - 1) {
    throw new Error(texts.dateNotValid);
  }
  return date;
}

/** The entries of the last few months: date, category and account. */
function readRecentEntries(entriesSheet) {
  const rowCount = entriesSheet.getLastRow() - 1;
  if (rowCount <= 0) {
    return [];
  }
  const since = new Date();
  since.setDate(since.getDate() - DAYS_THAT_DECIDE_FREQUENT_CATEGORIES);
  return entriesSheet.getRange(2, 1, rowCount, ENTRY_ACCOUNT_COLUMN).getValues()
      .filter(function (row) { return row[0] instanceof Date && row[0] >= since; })
      .map(function (row) { return { category: row[2], account: row[3] }; });
}

/**
 * The categories used most in the last few months, shown first on the
 * screen; a frequent transfer is shown there too. Without entries yet, the
 * first expense categories are shown.
 */
function frequentCategoryNames(recentEntries, categories, transferName) {
  const known = {};
  categories.forEach(function (category) { known[category.name] = true; });
  known[transferName] = true;
  const timesUsed = {};
  recentEntries.forEach(function (entry) {
    if (known[entry.category]) {
      timesUsed[entry.category] = (timesUsed[entry.category] || 0) + 1;
    }
  });
  const used = Object.keys(timesUsed).sort(function (first, second) {
    return timesUsed[second] - timesUsed[first];
  });
  const names = used.slice(0, FREQUENT_CATEGORY_COUNT);
  categories.forEach(function (category) {
    if (names.length < FREQUENT_CATEGORY_COUNT && category.kind === 'expense' &&
        names.indexOf(category.name) === -1) {
      names.push(category.name);
    }
  });
  return names;
}

/**
 * The plan and actual amount of every category in a month, read from that
 * month's sheet. Returns null for a month outside the budget's year.
 */
function monthOverview(spreadsheet, year, monthNumber, texts) {
  if (year !== budgetYear()) {
    return null;
  }
  const sheet = findSheetByRole(spreadsheet, monthRole(monthNumber));
  const rowCount = sheet.getLastRow() - MONTH_FIRST_CATEGORY_ROW + 1;
  const categories = {};
  let plannedExpenses = 0;
  if (rowCount > 0) {
    sheet.getRange(MONTH_FIRST_CATEGORY_ROW, 2, rowCount, 3).getValues().forEach(function (row) {
      const plan = typeof row[1] === 'number' ? row[1] : null;
      categories[row[0]] = { plan: plan, actual: Number(row[2]) || 0 };
      plannedExpenses += plan || 0;
    });
  }
  return {
    name: texts.monthNames[monthNumber - 1],
    expenses: Number(sheet.getRange(MONTH_TOTALS_FIRST_ROW + 1, 2).getValue()) || 0,
    plannedExpenses: plannedExpenses,
    categories: categories,
  };
}
