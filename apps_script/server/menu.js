/** Adds the "Budget" menu to the spreadsheet every time it is opened. */
function onOpen() {
  const texts = currentTexts();
  SpreadsheetApp.getUi()
      .createMenu(texts.menuTitle)
      .addItem(texts.menuPrepare, 'prepareSpreadsheet')
      .addToUi();
}
