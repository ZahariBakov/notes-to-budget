/**
 * The "Year" sheet: every category month by month, with the total and the
 * monthly average. One-off entries are left out of the average.
 */

const YEAR_MONTHS_SO_FAR_ROW = 2;
const YEAR_HEADER_ROW = 4;
const YEAR_FIRST_CATEGORY_ROW = 5;
const YEAR_FIRST_MONTH_COLUMN = 3;                          // C = January
const YEAR_TOTAL_COLUMN = YEAR_FIRST_MONTH_COLUMN + 12;     // O
const YEAR_AVERAGE_COLUMN = YEAR_TOTAL_COLUMN + 1;          // P

function writeYearSheet(sheet, settings, entriesSheet, separator, texts) {
  clearSheet(sheet);
  const year = budgetYear();
  const totalLetter = columnLetter(YEAR_TOTAL_COLUMN);

  sheet.getRange('A1').setNumberFormat('@').setValue(texts.yearSheet + ' ' + year)
      .setFontSize(16).setFontWeight('bold');
  sheet.getRange(YEAR_MONTHS_SO_FAR_ROW, 1).setValue(texts.monthsSoFar);
  sheet.getRange(YEAR_MONTHS_SO_FAR_ROW, 2).setFormula('=' + call('IF', [
    year + '<YEAR(TODAY())', 12,
    call('IF', [year + '>YEAR(TODAY())', 0, 'MONTH(TODAY())'], separator),
  ], separator));

  const header = [texts.group, texts.category].concat(texts.monthNames)
      .concat([texts.total, texts.monthlyAverage]);
  sheet.getRange(YEAR_HEADER_ROW, 1, 1, header.length).setValues([header])
      .setFontWeight('bold').setBackground('#263238').setFontColor('#ffffff')
      .setWrap(true);

  const categories = settings.categories;
  const rowsByKind = { expense: [], income: [], saving: [], investment: [] };
  const names = [];
  const formulas = [];
  categories.forEach(function (category, index) {
    const row = YEAR_FIRST_CATEGORY_ROW + index;
    names.push([category.group, category.name]);
    const rowFormulas = [];
    for (let month = 1; month <= 12; month++) {
      const firstDay = call('DATE', [year, month, 1], separator);
      const lastDay = call('EOMONTH', [firstDay, 0], separator);
      rowFormulas.push('=' + amountOfCategoryBetween(entriesSheet, '$B' + row, firstDay, lastDay,
          separator));
    }
    rowFormulas.push('=' + call('SUM', [
      columnLetter(YEAR_FIRST_MONTH_COLUMN) + row + ':' + columnLetter(YEAR_TOTAL_COLUMN - 1) + row,
    ], separator));
    rowFormulas.push('=' + averageWithoutOneOffs(entriesSheet, row, year, totalLetter, separator));
    formulas.push(rowFormulas);
    rowsByKind[category.kind].push(row);
  });

  const count = categories.length;
  if (count > 0) {
    sheet.getRange(YEAR_FIRST_CATEGORY_ROW, 1, count, 2).setValues(names);
    sheet.getRange(YEAR_FIRST_CATEGORY_ROW, YEAR_FIRST_MONTH_COLUMN, count, 14)
        .setFormulas(formulas);
  }

  const totalsFirstRow = YEAR_FIRST_CATEGORY_ROW + count + 1;
  const totals = [
    [texts.income, rowsByKind.income],
    [texts.expenses, rowsByKind.expense],
    [texts.savedAndInvested, rowsByKind.saving.concat(rowsByKind.investment)],
  ];
  totals.forEach(function (total, index) {
    const row = totalsFirstRow + index;
    sheet.getRange(row, 2).setValue(total[0]);
    const rowFormulas = [];
    for (let column = YEAR_FIRST_MONTH_COLUMN; column <= YEAR_AVERAGE_COLUMN; column++) {
      rowFormulas.push(sumOfCells(columnLetter(column), total[1]));
    }
    sheet.getRange(row, YEAR_FIRST_MONTH_COLUMN, 1, rowFormulas.length).setFormulas([rowFormulas]);
  });
  const leftRow = totalsFirstRow + 3;
  sheet.getRange(leftRow, 2).setValue(texts.left);
  const leftFormulas = [];
  for (let column = YEAR_FIRST_MONTH_COLUMN; column <= YEAR_AVERAGE_COLUMN; column++) {
    const letter = columnLetter(column);
    leftFormulas.push('=' + letter + totalsFirstRow + '-' + letter + (totalsFirstRow + 1) + '-' +
        letter + (totalsFirstRow + 2));
  }
  sheet.getRange(leftRow, YEAR_FIRST_MONTH_COLUMN, 1, leftFormulas.length)
      .setFormulas([leftFormulas]);
  sheet.getRange(totalsFirstRow, 2, 4, YEAR_AVERAGE_COLUMN - 1).setFontWeight('bold');
  showNegativeInRed(sheet, sheet.getRange(leftRow, YEAR_FIRST_MONTH_COLUMN, 1, 14));

  sheet.getRange(YEAR_FIRST_CATEGORY_ROW, YEAR_FIRST_MONTH_COLUMN, count + 5, 14)
      .setNumberFormat(moneyFormat());
  sheet.setFrozenRows(YEAR_HEADER_ROW);
  sheet.setFrozenColumns(2);
  setColumnWidths(sheet, [170, 200].concat(new Array(12).fill(95)).concat([105, 130]));
}

/** (total - one-off entries of the year) / months so far, or empty before the year starts. */
function averageWithoutOneOffs(entriesSheet, row, year, totalLetter, separator) {
  const dates = wholeColumn(entriesSheet, ENTRY_DATE_COLUMN);
  const oneOffs = call('SUMIFS', [
    wholeColumn(entriesSheet, ENTRY_AMOUNT_COLUMN),
    wholeColumn(entriesSheet, ENTRY_CATEGORY_COLUMN), '$B' + row,
    dates, '">="&' + call('DATE', [year, 1, 1], separator),
    dates, '"<="&' + call('DATE', [year, 12, 31], separator),
    wholeColumn(entriesSheet, ENTRY_ONE_OFF_COLUMN), 'TRUE',
  ], separator);
  const monthsSoFar = '$B$' + YEAR_MONTHS_SO_FAR_ROW;
  return call('IF', [
    monthsSoFar + '=0', '""',
    '(' + totalLetter + row + '-' + oneOffs + ')/' + monthsSoFar,
  ], separator);
}
