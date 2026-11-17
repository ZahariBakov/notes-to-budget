/**
 * The icon shown on each category tile.
 *
 * Icons come from Tabler Icons (https://tabler.io/icons); the "Icon" column
 * of the Settings sheet holds the name of one, for example "shopping-cart".
 * These are only the first suggestions; the person can change any of them.
 */

const SUGGESTED_ICONS = {
  // Bulgarian
  'сметки': 'file-invoice',
  'кредит': 'building-bank',
  'абонаменти': 'repeat',
  'застраховки и данъци': 'shield-check',
  'пазар': 'shopping-cart',
  'алкохол и цигари': 'glass-full',
  'за дома': 'home',
  'хранене в работа': 'briefcase',
  'хранене навън': 'tools-kitchen-2',
  'заведения': 'beer',
  'кола': 'car',
  'коли': 'car',
  'транспорт': 'gas-station',
  'деца': 'mood-kid',
  'домашен любимец': 'paw',
  'здраве': 'first-aid-kit',
  'лична грижа': 'scissors',
  'дрехи': 'shirt',
  'спорт': 'run',
  'забавления': 'movie',
  'почивки': 'plane',
  'празници': 'gift',
  'празници и подаръци': 'gift',
  'обучения': 'school',
  'други': 'dots',
  'загубени': 'question-mark',
  'заплата': 'cash',
  'наем': 'key',
  'допълнителни': 'coins',
  'спестявания': 'pig-money',
  'инвестиции': 'chart-line',

  // English
  'bills': 'file-invoice',
  'loan': 'building-bank',
  'subscriptions': 'repeat',
  'insurance and taxes': 'shield-check',
  'groceries': 'shopping-cart',
  'home': 'home',
  'food at work': 'briefcase',
  'eating out': 'tools-kitchen-2',
  'cafes and bars': 'beer',
  'car': 'car',
  'transport': 'gas-station',
  'children': 'mood-kid',
  'pet': 'paw',
  'health': 'first-aid-kit',
  'personal care': 'scissors',
  'clothes': 'shirt',
  'sport': 'run',
  'entertainment': 'movie',
  'holidays': 'plane',
  'celebrations and gifts': 'gift',
  'education': 'school',
  'other': 'dots',
  'lost': 'question-mark',
  'salary': 'cash',
  'rent': 'key',
  'additional': 'coins',
  'savings': 'pig-money',
  'investments': 'chart-line',
};

const ICON_FOR_KIND = {
  expense: 'receipt',
  income: 'cash',
  saving: 'pig-money',
  investment: 'chart-line',
};

const TRANSFER_ICON = 'arrows-exchange';

function suggestIcon(categoryName, kind) {
  return SUGGESTED_ICONS[String(categoryName).trim().toLowerCase()] ||
      ICON_FOR_KIND[kind] || ICON_FOR_KIND.expense;
}
