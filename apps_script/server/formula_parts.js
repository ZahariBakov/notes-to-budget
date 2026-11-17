/**
 * Small pieces for building spreadsheet formulas.
 *
 * Some spreadsheet languages separate the parts of a formula with ";" and
 * others with ",", so every formula is built with the separator of this
 * spreadsheet.
 */

function findArgumentSeparator(sheet) {
  const testCell = sheet.getRange(1, sheet.getMaxColumns());
  const before = testCell.getFormula() || testCell.getValue();
  testCell.setFormula('=SUM(1;2)');
  SpreadsheetApp.flush();
  const worksWithSemicolon = testCell.getValue() === 3;
  testCell.setValue(before);
  return worksWithSemicolon ? ';' : ',';
}

/** Joins the parts of a function call, for example call('SUM', ['A1', 'B1'], ';'). */
function call(functionName, parts, separator) {
  return functionName + '(' + parts.join(separator) + ')';
}

/** A sheet name as formulas need it: 'My sheet'! */
function sheetReference(sheet) {
  return "'" + sheet.getName().replace(/'/g, "''") + "'!";
}

/**
 * A whole column of a sheet, such as 'Entries'!$B:$B.
 *
 * Whole columns keep working however many entries are added.
 */
function wholeColumn(sheet, columnNumber) {
  const letter = columnLetter(columnNumber);
  return sheetReference(sheet) + '$' + letter + ':$' + letter;
}

function columnLetter(columnNumber) {
  let letters = '';
  let rest = columnNumber;
  while (rest > 0) {
    const remainder = (rest - 1) % 26;
    letters = String.fromCharCode(65 + remainder) + letters;
    rest = Math.floor((rest - 1) / 26);
  }
  return letters;
}

function textInFormula(text) {
  return '"' + String(text).replace(/"/g, '""') + '"';
}

/** =D9+D10+D11, or =0 when there are no rows. */
function sumOfCells(column, rows) {
  if (rows.length === 0) {
    return '=0';
  }
  return '=' + rows.map(function (row) { return column + row; }).join('+');
}
