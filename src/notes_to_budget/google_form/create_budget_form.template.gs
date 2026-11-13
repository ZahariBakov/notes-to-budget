/**
 * Creates your budget form and the spreadsheet for the current month.
 *
 * How to use it (once):
 *   1. Open https://script.google.com and start a new project.
 *   2. Replace everything in the editor with this file.
 *   3. Choose the function "createBudgetForm" and press Run.
 *   4. Google asks you to allow the script to create a form and a
 *      spreadsheet in your own account. The script touches nothing else.
 *   5. The links to the new form and spreadsheet appear in the log and
 *      on the first sheet of the spreadsheet.
 *
 * This file was written by notes-to-budget from your own settings.
 * The SETUP block below holds your categories, accounts and labels.
 */

const SETUP = /*SETUP_PLACEHOLDER*/ null;

// Columns of the sheet that receives the answers, in the order of the form.
const AMOUNT_COLUMN = 'B';
const CATEGORY_COLUMN = 'C';
const ACCOUNT_COLUMN = 'D';
const TO_ACCOUNT_COLUMN = 'F';

// Rows 4-7 of the month sheet hold the totals; the table starts below them.
const FIRST_TABLE_ROW = 10;

function createBudgetForm() {
  if (SETUP === null) {
    throw new Error(
        'This is the empty template, without your categories. ' +
        'Run "notes-to-budget form-script" and paste the file it writes ' +
        '(create_budget_form.gs in your data folder) instead of this one.');
  }
  const labels = SETUP.labels;
  const newSpreadsheet = SpreadsheetApp.create(labels.spreadsheetTitle);
  // Remember the empty first sheet now: linking the form adds the answers
  // sheet in front of it, and the summary must not be written over the answers.
  const monthSheetId = newSpreadsheet.getSheets()[0].getSheetId();
  const form = createForm(labels);

  form.setDestination(FormApp.DestinationType.SPREADSHEET, newSpreadsheet.getId());
  const answersSheet = waitForAnswersSheet(newSpreadsheet.getId());
  answersSheet.setName(labels.answersSheet);
  const answers = "'" + answersSheet.getName().replace(/'/g, "''") + "'!";

  // Open the spreadsheet again, so the list of sheets includes the answers.
  const spreadsheet = SpreadsheetApp.openById(newSpreadsheet.getId());
  const monthSheet = findSheetById(spreadsheet, monthSheetId);
  const separator = findArgumentSeparator(monthSheet);
  writeMonthSheet(monthSheet, labels, answers, separator, form);
  writeBalancesSheet(spreadsheet, labels, answers, separator);
  spreadsheet.setActiveSheet(monthSheet);
  spreadsheet.moveActiveSheet(1);

  Logger.log(labels.linkToForm + ': ' + form.getPublishedUrl());
  Logger.log(labels.linkToSpreadsheet + ': ' + spreadsheet.getUrl());
}

function createForm(labels) {
  const form = FormApp.create(labels.formTitle);
  form.setDescription(labels.formDescription);
  form.setConfirmationMessage(labels.saved);
  form.setShowLinkToRespondAgain(true);

  const accountLabels = SETUP.accounts.map(function (account) { return account.label; });
  const mustBeNumber = FormApp.createTextValidation()
      .setHelpText(labels.amountMustBeNumber)
      .requireNumber()
      .build();

  form.addTextItem()
      .setTitle(labels.amount)
      .setHelpText(labels.amountHelp)
      .setValidation(mustBeNumber)
      .setRequired(true);
  form.addListItem()
      .setTitle(labels.category)
      .setChoiceValues(SETUP.categories.map(function (category) { return category.name; }))
      .setRequired(true);
  form.addMultipleChoiceItem()
      .setTitle(labels.account)
      .setChoiceValues(accountLabels)
      .setRequired(true);
  form.addTextItem().setTitle(labels.description);
  form.addListItem()
      .setTitle(labels.toAccount)
      .setHelpText(labels.toAccountHelp)
      .setChoiceValues(accountLabels);
  form.addCheckboxItem().setTitle(labels.oneOff).setChoiceValues([labels.oneOffYes]);
  form.addDateItem().setTitle(labels.date).setHelpText(labels.dateHelp);
  return form;
}

/** The sheet for the answers appears a moment after the form is linked. */
function waitForAnswersSheet(spreadsheetId) {
  for (let attempt = 0; attempt < 15; attempt++) {
    SpreadsheetApp.flush();
    const sheets = SpreadsheetApp.openById(spreadsheetId).getSheets();
    for (let index = 0; index < sheets.length; index++) {
      if (sheets[index].getFormUrl()) {
        return sheets[index];
      }
    }
    Utilities.sleep(1000);
  }
  throw new Error('The sheet with the answers did not appear. Run the function again.');
}

/** Some languages separate the parts of a formula with ";" and others with ",". */
function findSheetById(spreadsheet, sheetId) {
  const sheets = spreadsheet.getSheets();
  for (let index = 0; index < sheets.length; index++) {
    if (sheets[index].getSheetId() === sheetId) {
      return sheets[index];
    }
  }
  throw new Error('The sheet for the month summary was not found. Run the function again.');
}

function findArgumentSeparator(emptySheet) {
  const testCell = emptySheet.getRange('Z1');
  testCell.setFormula('=SUM(1;2)');
  SpreadsheetApp.flush();
  const worksWithSemicolon = testCell.getValue() === 3;
  testCell.clear();
  return worksWithSemicolon ? ';' : ',';
}

/**
 * A whole column of the answers sheet, such as 'Answers'!$B:$B.
 *
 * Whole columns are used on purpose: every new answer is inserted as a
 * new row, which would push a range like B2:B down and past the answer.
 */
function wholeColumn(answers, column) {
  return answers + '$' + column + ':$' + column;
}

function writeMonthSheet(sheet, labels, answers, separator, form) {
  const amounts = wholeColumn(answers, AMOUNT_COLUMN);
  const categories = wholeColumn(answers, CATEGORY_COLUMN);
  const money = '#,##0.00 "' + SETUP.currencySymbol + '"';

  sheet.setName(labels.monthSheet);
  sheet.getRange('A1').setValue(labels.spreadsheetTitle).setFontSize(16).setFontWeight('bold');
  sheet.getRange('A2').setValue(labels.linkToForm);
  sheet.getRange('B2').setValue(form.getPublishedUrl());

  const header = [labels.group, labels.category, labels.plan, labels.actual, labels.remaining];
  sheet.getRange(FIRST_TABLE_ROW - 1, 1, 1, header.length).setValues([header])
      .setFontWeight('bold').setBackground('#263238').setFontColor('#ffffff');

  let row = FIRST_TABLE_ROW;
  const rowsByKind = { expense: [], income: [], saving: [], investment: [] };
  SETUP.categories.forEach(function (category) {
    if (!rowsByKind[category.kind]) {
      return;  // transfers are not shown in the summary
    }
    sheet.getRange(row, 1, 1, 2).setValues([[category.group, category.name]]);
    sheet.getRange(row, 4).setFormula(
        '=SUMIF(' + categories + separator + '$B' + row + separator + amounts + ')');
    if (category.kind === 'expense') {
      sheet.getRange(row, 3).setBackground('#c8e6c9');
      sheet.getRange(row, 5).setFormula(
          '=IF(C' + row + '=""' + separator + '""' + separator + 'C' + row + '-D' + row + ')');
    }
    rowsByKind[category.kind].push(row);
    row++;
  });
  sheet.getRange(FIRST_TABLE_ROW, 3, row - FIRST_TABLE_ROW, 3).setNumberFormat(money);

  const totals = [
    [labels.income, sumOfRows(rowsByKind.income)],
    [labels.expenses, sumOfRows(rowsByKind.expense)],
    [labels.savedAndInvested, sumOfRows(rowsByKind.saving.concat(rowsByKind.investment))],
    [labels.left, '=B4-B5-B6'],
  ];
  totals.forEach(function (total, index) {
    sheet.getRange(4 + index, 1).setValue(total[0]).setFontWeight('bold');
    sheet.getRange(4 + index, 2).setFormula(total[1]).setNumberFormat(money).setFontWeight('bold');
  });
  sheet.getRange(3, 1).setValue(labels.planHelp).setFontStyle('italic');
  sheet.setFrozenRows(FIRST_TABLE_ROW - 1);
  setColumnWidths(sheet, [170, 210, 110, 110, 110]);
}

function setColumnWidths(sheet, widths) {
  widths.forEach(function (width, index) {
    sheet.setColumnWidth(index + 1, width);
  });
}

function sumOfRows(rows) {
  if (rows.length === 0) {
    return '=0';
  }
  return '=' + rows.map(function (row) { return 'D' + row; }).join('+');
}

/** Compares what the entries say each account should hold with what it really holds. */
function writeBalancesSheet(spreadsheet, labels, answers, separator) {
  const sheet = spreadsheet.insertSheet(labels.balancesSheet);
  const money = '#,##0.00 "' + SETUP.currencySymbol + '"';
  const amounts = wholeColumn(answers, AMOUNT_COLUMN);
  const categories = wholeColumn(answers, CATEGORY_COLUMN);
  const accounts = wholeColumn(answers, ACCOUNT_COLUMN);
  const toAccounts = wholeColumn(answers, TO_ACCOUNT_COLUMN);
  const incomeCategoryNames = SETUP.categories
      .filter(function (category) { return category.kind === 'income'; })
      .map(function (category) { return category.name; });

  const header = [labels.account, labels.startOfMonth, labels.expected, labels.actualNow,
    labels.difference];
  sheet.getRange(1, 1, 1, header.length).setValues([header])
      .setFontWeight('bold').setBackground('#263238').setFontColor('#ffffff');

  let row = 2;
  SETUP.accounts.forEach(function (account) {
    if (!account.reconciled) {
      return;
    }
    sheet.getRange(row, 1).setValue(account.label);
    sheet.getRange(row, 2).setBackground('#c8e6c9');
    sheet.getRange(row, 4).setBackground('#c8e6c9');
    // Every entry of an account takes money out of it, except income,
    // which puts money in. So:
    //   start - (all entries of the account) + 2 x (its income entries)
    //         + transfers that arrive in the account
    // Only plain SUMIF and SUMIFS are used; they work in every spreadsheet.
    const thisAccount = '$A' + row;
    const incomeOfThisAccount = incomeCategoryNames.map(function (incomeCategoryName) {
      return 'SUMIFS(' + amounts + separator + accounts + separator + thisAccount + separator +
          categories + separator + '"' + incomeCategoryName.replace(/"/g, '""') + '")';
    });
    sheet.getRange(row, 3).setFormula(
        '=B' + row +
        '-SUMIF(' + accounts + separator + thisAccount + separator + amounts + ')' +
        '+2*(' + (incomeOfThisAccount.join('+') || '0') + ')' +
        '+SUMIF(' + toAccounts + separator + thisAccount + separator + amounts + ')');
    sheet.getRange(row, 5).setFormula(
        '=IF(D' + row + '=""' + separator + '""' + separator + 'D' + row + '-C' + row + ')');
    row++;
  });
  sheet.getRange(2, 2, Math.max(row - 2, 1), 4).setNumberFormat(money);
  sheet.getRange(row + 1, 1).setValue(labels.balancesHelp).setFontStyle('italic');
  setColumnWidths(sheet, [210, 150, 130, 130, 130]);
}
