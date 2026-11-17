/**
 * Every word the app shows, in each language it speaks.
 * Keep the same keys in every language.
 */
const TEXTS = {
  bg: {
    // How the spreadsheet reads typed dates and numbers: 17.11.2026 and 12,50.
    spreadsheetLocale: 'bg_BG',
    menuTitle: 'Бюджет',
    menuPrepare: 'Подготви или обнови таблицата',
    prepared: 'Таблицата е готова. Месеците и „Година“ са направени от листа „Настройки“.',
    missingPersonalSettings:
        'Липсват твоите настройки (personal_settings.js). Пусни „notes-to-budget app-settings“, ' +
        'сложи файла в папката apps_script и качи приложението с clasp push.',

    entriesSheet: 'Записи',
    checksSheet: 'Сверки',
    settingsSheet: 'Настройки',
    yearSheet: 'Година',
    monthNames: ['Януари', 'Февруари', 'Март', 'Април', 'Май', 'Юни', 'Юли', 'Август',
      'Септември', 'Октомври', 'Ноември', 'Декември'],

    date: 'Дата',
    amount: 'Сума',
    category: 'Категория',
    account: 'Сметка',
    toAccount: 'Към сметка',
    description: 'Описание',
    oneOff: 'Еднократно',
    enteredAt: 'Въведено на',
    entryId: 'Номер',
    actual: 'Реално',
    expected: 'Очаквано',
    difference: 'Разлика',

    settingsHelp: 'Тук са категориите и сметките ти. Ако промениш нещо, избери ' +
        'Бюджет > Подготви или обнови таблицата. Записите и плановете остават.',
    group: 'Група',
    kind: 'Вид',
    code: 'Код',
    name: 'Име',
    reconciled: 'Сверява се',
    creditCard: 'Кредитна карта',
    kinds: { expense: 'разход', income: 'приход', saving: 'спестяване', investment: 'инвестиция' },
    incomeGroup: 'Приходи',
    savedGroup: 'Спестено и инвестирано',
    transfer: 'Прехвърляне между сметки',

    income: 'Приходи',
    expenses: 'Разходи',
    savedAndInvested: 'Спестено и инвестирано',
    left: 'Остатък',
    plan: 'План',
    remaining: 'Остава',
    total: 'Общо',
    monthlyAverage: 'Средно на месец (без еднократните)',
    monthsSoFar: 'Изминали месеци',
  },

  en: {
    // Empty: keep the spreadsheet's own locale, since English is written in many ways.
    spreadsheetLocale: '',
    menuTitle: 'Budget',
    menuPrepare: 'Prepare or refresh the spreadsheet',
    prepared: 'The spreadsheet is ready. The months and "Year" are made from the Settings sheet.',
    missingPersonalSettings:
        'Your settings (personal_settings.js) are missing. Run "notes-to-budget app-settings", ' +
        'put the file in the apps_script folder and upload the app with clasp push.',

    entriesSheet: 'Entries',
    checksSheet: 'Checks',
    settingsSheet: 'Settings',
    yearSheet: 'Year',
    monthNames: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
      'September', 'October', 'November', 'December'],

    date: 'Date',
    amount: 'Amount',
    category: 'Category',
    account: 'Account',
    toAccount: 'To account',
    description: 'Description',
    oneOff: 'One-off',
    enteredAt: 'Entered at',
    entryId: 'Number',
    actual: 'Actual',
    expected: 'Expected',
    difference: 'Difference',

    settingsHelp: 'Your categories and accounts. If you change something, choose ' +
        'Budget > Prepare or refresh the spreadsheet. Your entries and plans stay.',
    group: 'Group',
    kind: 'Kind',
    code: 'Code',
    name: 'Name',
    reconciled: 'Checked',
    creditCard: 'Credit card',
    kinds: { expense: 'expense', income: 'income', saving: 'saving', investment: 'investment' },
    incomeGroup: 'Income',
    savedGroup: 'Saved and invested',
    transfer: 'Transfer between accounts',

    income: 'Income',
    expenses: 'Expenses',
    savedAndInvested: 'Saved and invested',
    left: 'Left',
    plan: 'Plan',
    remaining: 'Remaining',
    total: 'Total',
    monthlyAverage: 'Monthly average (without one-offs)',
    monthsSoFar: 'Months so far',
  },
};
