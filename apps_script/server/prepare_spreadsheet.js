/**
 * Prepares the spreadsheet the first time and refreshes it after the
 * settings change.
 *
 * The first time, it creates the sheets and fills "Settings" from
 * personal_settings.js. Every time, it makes the month sheets and the year
 * sheet again from "Settings". Entries, checks and typed plans are kept.
 */

function prepareSpreadsheet() {
  const ui = SpreadsheetApp.getUi();
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const isFirstTime = !documentProperties().getProperty(PROPERTY_YEAR);

  if (isFirstTime) {
    if (!hasPersonalSettings()) {
      ui.alert(currentTexts().missingPersonalSettings);
      return;
    }
    documentProperties().setProperties({
      [PROPERTY_LANGUAGE]: PERSONAL_SETTINGS.language,
      [PROPERTY_CURRENCY_SYMBOL]: PERSONAL_SETTINGS.currencySymbol,
      [PROPERTY_YEAR]: String(new Date().getFullYear()),
    });
    spreadsheet.setSpreadsheetTimeZone(Session.getScriptTimeZone());
  }
  const texts = currentTexts();
  useLocaleOfLanguage(spreadsheet, texts);
  const sheetsBefore = spreadsheet.getSheets();

  const entriesSheet = findOrCreateSheet(spreadsheet, 'entries', texts.entriesSheet,
      function (sheet) { prepareEntriesSheet(sheet, texts); });
  const checksSheet = findOrCreateSheet(spreadsheet, 'checks', texts.checksSheet,
      function (sheet) { prepareChecksSheet(sheet, texts); });
  const settingsSheet = findOrCreateSheet(spreadsheet, 'settings', texts.settingsSheet,
      function (sheet) { fillSettingsSheet(sheet, texts, startingSettings(texts)); });

  const settings = readSettings(settingsSheet, texts);
  const separator = findArgumentSeparator(entriesSheet);
  const monthSheets = [];
  for (let month = 1; month <= 12; month++) {
    const monthSheet = findOrCreateSheet(spreadsheet, monthRole(month), texts.monthNames[month - 1],
        function () {});
    writeMonthSheet(monthSheet, month, settings, entriesSheet, separator, texts);
    monthSheets.push(monthSheet);
  }
  const yearSheet = findOrCreateSheet(spreadsheet, 'year', texts.yearSheet, function () {});
  writeYearSheet(yearSheet, settings, entriesSheet, separator, texts);

  putInOrder(spreadsheet, monthSheets.concat([yearSheet, entriesSheet, checksSheet,
    settingsSheet]));
  if (isFirstTime) {
    removeEmptySheets(spreadsheet, sheetsBefore);
  }
  openCurrentMonth(spreadsheet, monthSheets);
  ui.alert(texts.prepared);
}

/** The settings to start from: the person's own, from personal_settings.js. */
function startingSettings(texts) {
  if (!hasPersonalSettings()) {
    throw new Error(texts.missingPersonalSettings);
  }
  return PERSONAL_SETTINGS;
}

/**
 * A new spreadsheet may read dates and numbers the English way, and then
 * a typed 17.11.2026 stays plain text that no formula counts.
 */
function useLocaleOfLanguage(spreadsheet, texts) {
  if (texts.spreadsheetLocale && spreadsheet.getSpreadsheetLocale() !== texts.spreadsheetLocale) {
    spreadsheet.setSpreadsheetLocale(texts.spreadsheetLocale);
    SpreadsheetApp.flush();
  }
}

function findOrCreateSheet(spreadsheet, role, name, prepareNewSheet) {
  const existing = findSheetByRole(spreadsheet, role);
  if (existing) {
    return existing;
  }
  const sheet = spreadsheet.insertSheet(name, spreadsheet.getNumSheets());
  rememberSheetId(role, sheet);
  prepareNewSheet(sheet);
  return sheet;
}

function putInOrder(spreadsheet, sheets) {
  sheets.forEach(function (sheet, index) {
    spreadsheet.setActiveSheet(sheet);
    spreadsheet.moveActiveSheet(index + 1);
  });
}

/** The empty "Sheet1" a new spreadsheet starts with is not needed. */
function removeEmptySheets(spreadsheet, sheetsBefore) {
  sheetsBefore.forEach(function (sheet) {
    if (sheet.getLastRow() === 0 && sheet.getLastColumn() === 0) {
      spreadsheet.deleteSheet(sheet);
    }
  });
}

function openCurrentMonth(spreadsheet, monthSheets) {
  const today = new Date();
  const month = today.getFullYear() === budgetYear() ? today.getMonth() : 0;
  spreadsheet.setActiveSheet(monthSheets[month]);
}
