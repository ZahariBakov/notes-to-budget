/**
 * The "Settings" sheet: the person's categories and accounts.
 *
 * It is filled once from personal_settings.js. After that the sheet is
 * what counts, and the person changes categories and accounts there.
 */

const SETTINGS_HEADER_ROW = 3;
const SETTINGS_FIRST_ROW = 4;
const CATEGORIES_FIRST_COLUMN = 1;  // A: name, B: group, C: kind, D: icon
const CATEGORY_ICON_COLUMN = 4;
const ACCOUNTS_FIRST_COLUMN = 5;    // E: code, F: name, G: checked, H: credit card

function fillSettingsSheet(sheet, texts, personalSettings) {
  sheet.getRange('A1').setValue(texts.settingsHelp).setFontStyle('italic');

  writeSettingsHeader(sheet, CATEGORIES_FIRST_COLUMN,
      [texts.category, texts.group, texts.kind, texts.icon]);
  const categoryRows = personalSettings.categories.map(function (category) {
    return [category.name, groupOf(category, texts), texts.kinds[category.kind],
      suggestIcon(category.name, category.kind)];
  });
  sheet.getRange(SETTINGS_FIRST_ROW, CATEGORIES_FIRST_COLUMN, categoryRows.length, 4)
      .setValues(categoryRows);
  const kindChoices = SpreadsheetApp.newDataValidation()
      .requireValueInList(Object.keys(texts.kinds).map(function (kind) {
        return texts.kinds[kind];
      }), true)
      .build();
  sheet.getRange(SETTINGS_FIRST_ROW, CATEGORIES_FIRST_COLUMN + 2, 100, 1)
      .setDataValidation(kindChoices);

  writeSettingsHeader(sheet, ACCOUNTS_FIRST_COLUMN,
      [texts.code, texts.name, texts.reconciled, texts.creditCard]);
  const accountRows = personalSettings.accounts.map(function (account) {
    return [account.code, account.name, account.reconciled, account.creditCard];
  });
  sheet.getRange(SETTINGS_FIRST_ROW, ACCOUNTS_FIRST_COLUMN, accountRows.length, 4)
      .setValues(accountRows);
  sheet.getRange(SETTINGS_FIRST_ROW, ACCOUNTS_FIRST_COLUMN + 2, 30, 2).insertCheckboxes();

  setColumnWidths(sheet, [190, 170, 110, 140, 60, 190, 100, 110]);
  sheet.setFrozenRows(SETTINGS_HEADER_ROW);
}

/** Sheets made before icons existed get the column, filled with suggestions. */
function addIconColumnIfMissing(sheet, texts) {
  if (sheet.getRange(SETTINGS_HEADER_ROW, CATEGORY_ICON_COLUMN).getValue() !== '') {
    return;
  }
  writeSettingsHeader(sheet, CATEGORY_ICON_COLUMN, [texts.icon]);
  const rows = readFilledRows(sheet, CATEGORIES_FIRST_COLUMN, 3);
  const kindByWord = kindsByWord(texts);
  const icons = rows.map(function (row) {
    return [suggestIcon(row[0], kindByWord[String(row[2]).trim()])];
  });
  if (icons.length > 0) {
    sheet.getRange(SETTINGS_FIRST_ROW, CATEGORY_ICON_COLUMN, icons.length, 1).setValues(icons);
  }
  sheet.setColumnWidth(CATEGORY_ICON_COLUMN, 140);
}

/** Income, savings and investments are grouped under names from the app's language. */
function groupOf(category, texts) {
  if (category.group) {
    return category.group;
  }
  return category.kind === 'income' ? texts.incomeGroup : texts.savedGroup;
}

function writeSettingsHeader(sheet, firstColumn, header) {
  sheet.getRange(SETTINGS_HEADER_ROW, firstColumn, 1, header.length).setValues([header])
      .setFontWeight('bold').setBackground('#263238').setFontColor('#ffffff');
}

function kindsByWord(texts) {
  const kindByWord = {};
  Object.keys(texts.kinds).forEach(function (kind) {
    kindByWord[texts.kinds[kind]] = kind;
  });
  return kindByWord;
}

/**
 * The categories and accounts as they are in the sheet now.
 *
 * Returns { categories: [{ name, group, kind, icon }], accounts: [{ code,
 * name, reconciled, creditCard }] }, where kind is "expense", "income",
 * "saving" or "investment".
 */
function readSettings(sheet, texts) {
  const kindByWord = kindsByWord(texts);
  const categories = readFilledRows(sheet, CATEGORIES_FIRST_COLUMN, 4).map(function (row) {
    const kind = kindByWord[String(row[2]).trim()] || 'expense';
    return {
      name: String(row[0]).trim(),
      group: String(row[1]).trim(),
      kind: kind,
      icon: String(row[3]).trim() || suggestIcon(row[0], kind),
    };
  });
  const accounts = readFilledRows(sheet, ACCOUNTS_FIRST_COLUMN, 4).map(function (row) {
    return {
      code: String(row[0]).trim(),
      name: String(row[1]).trim(),
      reconciled: row[2] === true,
      creditCard: row[3] === true,
    };
  });
  return { categories: categories, accounts: accounts };
}

/** The rows of a settings table, down to the first one with an empty first cell. */
function readFilledRows(sheet, firstColumn, columnCount) {
  const rowCount = Math.max(sheet.getLastRow() - SETTINGS_FIRST_ROW + 1, 0);
  if (rowCount === 0) {
    return [];
  }
  const rows = sheet.getRange(SETTINGS_FIRST_ROW, firstColumn, rowCount, columnCount).getValues();
  const filled = [];
  for (let index = 0; index < rows.length; index++) {
    if (String(rows[index][0]).trim() === '') {
      break;
    }
    filled.push(rows[index]);
  }
  return filled;
}
