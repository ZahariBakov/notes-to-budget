/**
 * What each account should hold, from the last check and the entries since.
 *
 * A check is the balance at the moment it was saved. The entries that count
 * after it are those dated after the check's day, and those dated the same
 * day but entered after the check. An entry dated earlier but entered later
 * was already in the money that was counted, so it does not count again.
 *
 * Rows typed into the sheets by hand have no time. A check without one is
 * the morning balance of its day; an entry without one counts as entered at
 * the end of its day. So all of that day's entries come after that check.
 */

const MAXIMUM_ENTRIES_SHOWN_SINCE_CHECK = 15;

/** Every entry as a plain object; rows without a date or amount are skipped. */
function readAllEntries(entriesSheet) {
  const rowCount = entriesSheet.getLastRow() - 1;
  if (rowCount <= 0) {
    return [];
  }
  return entriesSheet.getRange(2, 1, rowCount, ENTRY_COLUMN_COUNT).getValues()
      .filter(function (row) {
        return row[ENTRY_DATE_COLUMN - 1] instanceof Date &&
            typeof row[ENTRY_AMOUNT_COLUMN - 1] === 'number';
      })
      .map(function (row) {
        const date = row[ENTRY_DATE_COLUMN - 1];
        const enteredAt = row[ENTRY_ENTERED_AT_COLUMN - 1];
        return {
          date: date,
          dayKey: dayKey(date),
          // Rows typed by hand have no time; they count as entered at the end of their day.
          enteredAt: enteredAt instanceof Date ? enteredAt : endOfDay(date),
          amount: row[ENTRY_AMOUNT_COLUMN - 1],
          category: String(row[ENTRY_CATEGORY_COLUMN - 1]),
          account: String(row[ENTRY_ACCOUNT_COLUMN - 1]),
          toAccount: String(row[ENTRY_TO_ACCOUNT_COLUMN - 1]),
          description: String(row[ENTRY_DESCRIPTION_COLUMN - 1]),
        };
      });
}

/** Every check, oldest first. */
function readAllChecks(checksSheet) {
  const rowCount = checksSheet.getLastRow() - 1;
  if (rowCount <= 0) {
    return [];
  }
  return checksSheet.getRange(2, 1, rowCount, CHECK_ENTERED_AT_COLUMN).getValues()
      .filter(function (row) {
        return row[CHECK_DATE_COLUMN - 1] instanceof Date &&
            typeof row[CHECK_ACTUAL_COLUMN - 1] === 'number';
      })
      .map(function (row) {
        const date = row[CHECK_DATE_COLUMN - 1];
        const enteredAt = row[CHECK_ENTERED_AT_COLUMN - 1];
        return {
          dayKey: dayKey(date),
          account: String(row[CHECK_ACCOUNT_COLUMN - 1]),
          actual: row[CHECK_ACTUAL_COLUMN - 1],
          // A check typed by hand has no time: it is the morning balance of its day,
          // so every entry of that day comes after it.
          enteredAt: enteredAt instanceof Date ? enteredAt : startOfDay(date),
        };
      })
      .sort(function (first, second) { return first.enteredAt - second.enteredAt; });
}

/**
 * How one entry changes one account: income in it adds, everything paid
 * from it takes away, and a transfer moves money from one account to the
 * other.
 */
function changeOfAccount(entry, accountName, kindByCategory, transferName) {
  if (entry.category === transferName) {
    let change = 0;
    if (entry.account === accountName) {
      change -= entry.amount;
    }
    if (entry.toAccount === accountName) {
      change += entry.amount;
    }
    return change;
  }
  if (entry.account !== accountName) {
    return 0;
  }
  return kindByCategory[entry.category] === 'income' ? entry.amount : -entry.amount;
}

/** Whether an entry belongs after a check (see the top of this file). */
function isAfterCheck(entry, check) {
  return entry.dayKey > check.dayKey ||
      (entry.dayKey === check.dayKey && entry.enteredAt > check.enteredAt);
}

/**
 * The check screen for every account that is checked against its balance.
 *
 * For each: what it should hold now (null before its first check), the
 * last check, whether it was checked today, and the entries since then.
 */
function checkOverview(settings, entries, checks, transferName, now) {
  const kindByCategory = kindsOfCategories(settings);
  const todayKey = dayKey(now);
  return settings.accounts
      .filter(function (account) { return account.reconciled; })
      .map(function (account) {
        const accountChecks = checks.filter(function (check) {
          return check.account === account.name;
        });
        const lastCheck = accountChecks.length > 0 ? accountChecks[accountChecks.length - 1]
          : null;
        if (!lastCheck) {
          return { name: account.name, expected: null, lastCheckDay: '', checkedToday: false,
            entriesSinceCheck: [] };
        }
        let expected = lastCheck.actual;
        const since = [];
        entries.forEach(function (entry) {
          if (!isAfterCheck(entry, lastCheck) || entry.dayKey > todayKey) {
            return;
          }
          const change = changeOfAccount(entry, account.name, kindByCategory, transferName);
          if (change !== 0) {
            expected += change;
            since.push({ dayKey: entry.dayKey, change: change, category: entry.category,
              description: entry.description });
          }
        });
        since.reverse();
        return {
          name: account.name,
          expected: roundToCents(expected),
          lastCheckDay: lastCheck.dayKey,
          lastActual: lastCheck.actual,
          checkedToday: lastCheck.dayKey === todayKey,
          entriesSinceCheck: since.slice(0, MAXIMUM_ENTRIES_SHOWN_SINCE_CHECK),
          entriesSinceCheckCount: since.length,
        };
      });
}

/**
 * What is owed on each credit card: everything moved or paid from it,
 * less what was paid back into it. Only cards with something owed are listed.
 */
function creditCardDebts(settings, entries, transferName) {
  const kindByCategory = kindsOfCategories(settings);
  return settings.accounts
      .filter(function (account) { return account.creditCard; })
      .map(function (account) {
        let owed = 0;
        entries.forEach(function (entry) {
          owed -= changeOfAccount(entry, account.name, kindByCategory, transferName);
        });
        return { name: account.name, owed: roundToCents(owed) };
      })
      .filter(function (debt) { return debt.owed > 0; });
}

function kindsOfCategories(settings) {
  const kindByCategory = {};
  settings.categories.forEach(function (category) {
    kindByCategory[category.name] = category.kind;
  });
  return kindByCategory;
}

/** A day as text that sorts in order, for example 2026-11-22, in the script's time zone. */
function dayKey(date) {
  return Utilities.formatDate(date, Session.getScriptTimeZone(), 'yyyy-MM-dd');
}

function startOfDay(date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

function endOfDay(date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate(), 23, 59, 59);
}

function roundToCents(amount) {
  return Math.round(amount * 100) / 100;
}
