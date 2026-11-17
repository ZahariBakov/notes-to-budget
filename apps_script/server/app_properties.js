/**
 * What the app remembers about this spreadsheet: its language, currency,
 * year and which sheet is which.
 *
 * Sheets are found by their id, not their name, so renaming a sheet does
 * not break the app.
 */

const PROPERTY_LANGUAGE = 'language';
const PROPERTY_CURRENCY_SYMBOL = 'currencySymbol';
const PROPERTY_YEAR = 'year';
const PROPERTY_SHEET_IDS = 'sheetIds';
const DEFAULT_LANGUAGE = 'en';

function documentProperties() {
  return PropertiesService.getDocumentProperties();
}

function hasPersonalSettings() {
  return typeof PERSONAL_SETTINGS !== 'undefined' && PERSONAL_SETTINGS !== null;
}

function currentLanguage() {
  const remembered = documentProperties().getProperty(PROPERTY_LANGUAGE);
  if (remembered) {
    return remembered;
  }
  return hasPersonalSettings() ? PERSONAL_SETTINGS.language : DEFAULT_LANGUAGE;
}

function currentTexts() {
  return TEXTS[currentLanguage()] || TEXTS[DEFAULT_LANGUAGE];
}

function currencySymbol() {
  return documentProperties().getProperty(PROPERTY_CURRENCY_SYMBOL) || '';
}

function budgetYear() {
  return Number(documentProperties().getProperty(PROPERTY_YEAR));
}

function moneyFormat() {
  return '#,##0.00 "' + currencySymbol() + '"';
}

/** Ids of the app's sheets by their role, for example { entries: 123, month1: 456 }. */
function rememberedSheetIds() {
  return JSON.parse(documentProperties().getProperty(PROPERTY_SHEET_IDS) || '{}');
}

function rememberSheetId(role, sheet) {
  const sheetIds = rememberedSheetIds();
  sheetIds[role] = sheet.getSheetId();
  documentProperties().setProperty(PROPERTY_SHEET_IDS, JSON.stringify(sheetIds));
}

/** The app's sheet for this role, or null if there is none yet. */
function findSheetByRole(spreadsheet, role) {
  const sheetId = rememberedSheetIds()[role];
  if (sheetId === undefined) {
    return null;
  }
  const sheets = spreadsheet.getSheets();
  for (let index = 0; index < sheets.length; index++) {
    if (sheets[index].getSheetId() === sheetId) {
      return sheets[index];
    }
  }
  return null;
}

function monthRole(monthNumber) {
  return 'month' + monthNumber;
}
