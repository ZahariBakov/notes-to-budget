/**
 * What the app remembers about its spreadsheet: language, currency, year
 * and which sheet is which.
 *
 * Sheets are found by their id, not their name, so renaming a sheet does
 * not break the app. The values are kept in the script's own properties,
 * which both the spreadsheet menu and the phone app can read.
 */

const PROPERTY_LANGUAGE = 'language';
const PROPERTY_CURRENCY_SYMBOL = 'currencySymbol';
const PROPERTY_YEAR = 'year';
const PROPERTY_SHEET_IDS = 'sheetIds';
const PROPERTY_SPREADSHEET_ID = 'spreadsheetId';
const DEFAULT_LANGUAGE = 'en';

function appProperties() {
  const scriptProperties = PropertiesService.getScriptProperties();
  if (!scriptProperties.getProperty(PROPERTY_YEAR)) {
    // The first version kept these in the spreadsheet's properties.
    const earlierProperties = PropertiesService.getDocumentProperties();
    if (earlierProperties && earlierProperties.getProperty(PROPERTY_YEAR)) {
      scriptProperties.setProperties(earlierProperties.getProperties());
    }
  }
  return scriptProperties;
}

function hasPersonalSettings() {
  return typeof PERSONAL_SETTINGS !== 'undefined' && PERSONAL_SETTINGS !== null;
}

function isPrepared() {
  return Boolean(appProperties().getProperty(PROPERTY_YEAR));
}

function currentLanguage() {
  const remembered = appProperties().getProperty(PROPERTY_LANGUAGE);
  if (remembered) {
    return remembered;
  }
  return hasPersonalSettings() ? PERSONAL_SETTINGS.language : DEFAULT_LANGUAGE;
}

function currentTexts() {
  return TEXTS[currentLanguage()] || TEXTS[DEFAULT_LANGUAGE];
}

function currencySymbol() {
  return appProperties().getProperty(PROPERTY_CURRENCY_SYMBOL) || '';
}

function budgetYear() {
  return Number(appProperties().getProperty(PROPERTY_YEAR));
}

function moneyFormat() {
  return '#,##0.00 "' + currencySymbol() + '"';
}

/** The budget spreadsheet, also when the phone app runs without it being open. */
function budgetSpreadsheet() {
  const active = SpreadsheetApp.getActiveSpreadsheet();
  if (active) {
    return active;
  }
  return SpreadsheetApp.openById(appProperties().getProperty(PROPERTY_SPREADSHEET_ID));
}

/** Ids of the app's sheets by their role, for example { entries: 123, month1: 456 }. */
function rememberedSheetIds() {
  return JSON.parse(appProperties().getProperty(PROPERTY_SHEET_IDS) || '{}');
}

function rememberSheetId(role, sheet) {
  const sheetIds = rememberedSheetIds();
  sheetIds[role] = sheet.getSheetId();
  appProperties().setProperty(PROPERTY_SHEET_IDS, JSON.stringify(sheetIds));
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
