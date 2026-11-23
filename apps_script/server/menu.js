/** Adds the "Budget" menu to the spreadsheet every time it is opened. */
function onOpen() {
  const texts = currentTexts();
  const menu = SpreadsheetApp.getUi()
      .createMenu(texts.menuTitle)
      .addItem(texts.menuPrepare, 'prepareSpreadsheet');
  if (hasEntriesToImport()) {
    menu.addItem(texts.menuImport, 'importEntries');
  }
  menu.addToUi();
}
