/**
 * One sheet per month: the plan and the actual amount for every category.
 *
 * The actual amounts are formulas over the "Entries" sheet, so a new entry
 * shows up here at once. Only the plan is typed by hand, in the green cells.
 */

const MONTH_TOTALS_FIRST_ROW = 3;   // rows 3-6: income, expenses, saved, left
const MONTH_HEADER_ROW = 8;
const MONTH_FIRST_CATEGORY_ROW = 9;
const MONTH_DATES_COLUMN = 7;       // G1: first day, G2: last day (hidden)
const PLAN_BACKGROUND = '#c8e6c9';

function writeMonthSheet(sheet, monthNumber, settings, entriesSheet, separator, texts) {
  const plansByCategory = readPlans(sheet);
  clearSheet(sheet);

  const year = budgetYear();
  sheet.getRange('A1').setValue(texts.monthNames[monthNumber - 1] + ' ' + year)
      .setFontSize(16).setFontWeight('bold');
  sheet.getRange('G1').setFormula('=' + call('DATE', [year, monthNumber, 1], separator));
  sheet.getRange('G2').setFormula('=' + call('EOMONTH', ['G1', 0], separator));
  sheet.hideColumns(MONTH_DATES_COLUMN);

  const header = [texts.group, texts.category, texts.plan, texts.actual, texts.remaining];
  sheet.getRange(MONTH_HEADER_ROW, 1, 1, header.length).setValues([header])
      .setFontWeight('bold').setBackground('#263238').setFontColor('#ffffff');

  const categories = settings.categories;
  const rowsByKind = { expense: [], income: [], saving: [], investment: [] };
  const names = [];
  const plans = [];
  const actualFormulas = [];
  const remainingFormulas = [];
  categories.forEach(function (category, index) {
    const row = MONTH_FIRST_CATEGORY_ROW + index;
    names.push([category.group, category.name]);
    plans.push([category.kind === 'expense' ? (plansByCategory[category.name] || '') : '']);
    actualFormulas.push(['=' + amountOfCategoryBetween(entriesSheet, '$B' + row, '$G$1', '$G$2',
        separator)]);
    remainingFormulas.push([category.kind === 'expense'
      ? '=' + call('IF', ['C' + row + '=""', '""', 'C' + row + '-D' + row], separator)
      : '']);
    rowsByKind[category.kind].push(row);
  });

  if (categories.length > 0) {
    const count = categories.length;
    sheet.getRange(MONTH_FIRST_CATEGORY_ROW, 1, count, 2).setValues(names);
    sheet.getRange(MONTH_FIRST_CATEGORY_ROW, 3, count, 1).setValues(plans);
    sheet.getRange(MONTH_FIRST_CATEGORY_ROW, 4, count, 1).setFormulas(actualFormulas);
    sheet.getRange(MONTH_FIRST_CATEGORY_ROW, 5, count, 1).setFormulas(remainingFormulas);
    sheet.getRange(MONTH_FIRST_CATEGORY_ROW, 3, count, 3).setNumberFormat(moneyFormat());
    rowsByKind.expense.forEach(function (row) {
      sheet.getRange(row, 3).setBackground(PLAN_BACKGROUND);
    });
    showNegativeInRed(sheet, sheet.getRange(MONTH_FIRST_CATEGORY_ROW, 5, count, 1));
  }

  const totals = [
    [texts.income, sumOfCells('D', rowsByKind.income)],
    [texts.expenses, sumOfCells('D', rowsByKind.expense)],
    [texts.savedAndInvested, sumOfCells('D', rowsByKind.saving.concat(rowsByKind.investment))],
    [texts.left, '=B3-B4-B5'],
  ];
  totals.forEach(function (total, index) {
    const row = MONTH_TOTALS_FIRST_ROW + index;
    sheet.getRange(row, 1).setValue(total[0]).setFontWeight('bold');
    sheet.getRange(row, 2).setFormula(total[1]).setNumberFormat(moneyFormat())
        .setFontWeight('bold');
  });
  showNegativeInRed(sheet, sheet.getRange(MONTH_TOTALS_FIRST_ROW + 3, 2));

  sheet.setFrozenRows(MONTH_HEADER_ROW);
  setColumnWidths(sheet, [190, 210, 110, 110, 110]);
}

/**
 * SUMIFS of the entries of one category between two dates.
 * The dates are cell references, for example $G$1 and $G$2.
 */
function amountOfCategoryBetween(entriesSheet, categoryCell, firstDay, lastDay, separator) {
  const dates = wholeColumn(entriesSheet, ENTRY_DATE_COLUMN);
  return call('SUMIFS', [
    wholeColumn(entriesSheet, ENTRY_AMOUNT_COLUMN),
    wholeColumn(entriesSheet, ENTRY_CATEGORY_COLUMN), categoryCell,
    dates, '">="&' + firstDay,
    dates, '"<="&' + lastDay,
  ], separator);
}

/** The plans already typed into a month sheet, so refreshing the sheet keeps them. */
function readPlans(sheet) {
  const plans = {};
  const rowCount = sheet.getLastRow() - MONTH_FIRST_CATEGORY_ROW + 1;
  if (rowCount <= 0) {
    return plans;
  }
  sheet.getRange(MONTH_FIRST_CATEGORY_ROW, 2, rowCount, 2).getValues().forEach(function (row) {
    if (row[0] !== '' && row[1] !== '') {
      plans[row[0]] = row[1];
    }
  });
  return plans;
}

function clearSheet(sheet) {
  sheet.clear();
  sheet.clearConditionalFormatRules();
  sheet.getRange(1, 1, sheet.getMaxRows(), sheet.getMaxColumns()).clearDataValidations();
  sheet.showColumns(1, sheet.getMaxColumns());
  sheet.setFrozenRows(0);
}

function showNegativeInRed(sheet, range) {
  const rules = sheet.getConditionalFormatRules();
  rules.push(SpreadsheetApp.newConditionalFormatRule()
      .whenNumberLessThan(0)
      .setFontColor('#c62828')
      .setRanges([range])
      .build());
  sheet.setConditionalFormatRules(rules);
}
