# Birthday Reminder

A tiny command-line tool that tells you **whose birthday is today** and **how many days are left** until everyone else's.

Type one command:

```bash
birthday_status
```

---

## What it does (the simple version)

You keep a plain text list of people and their birthdays in one file. This tool reads that list and prints:

1. A friendly line for anyone whose birthday is **today**.
2. A neat table of **everyone else**, sorted so the next birthday is at the top, with a number showing how many days away it is.

Example output:

```
Today is Alice's Birthday - 09/10/2026

Name          Birthday    Days Until
------------  ----------  ----------
Chandan       27/10               18
Ratna         16/12               68
Mukesh        06/03              148
Dad           08/10/1971         364
```

- People whose birthday is today show up in the "Today is ..." line, so they are **not** repeated in the table.
- The `Birthday` column keeps the year when the list had one.
- The last column counts from today to the next time that birthday comes around.

---

## Who is this for?

- **Non-technical users:** if you can open a terminal and type `birthday_status`, you can use it. You only ever edit one text file (your birthday list). See [Quick start](#quick-start).
- **Technical users:** jump to [How it works](#how-it-works-technical).

---

## Quick start

1. Make sure Python 3 is installed (it comes with Termux).
2. Put your birthday list in this exact file:

   ```
   /storage/emulated/0/Notes/Personal/Birthday
   ```

   One person per line, in the form `Name :- date`. For example:

   ```
   Aaron :- March 28 (28/03/2004)
   Emiley :- March 24
   Gurusaran :- 12 May
   ```

3. Run the command from any folder:

   ```bash
   birthday_status
   ```

That's it. The tool creates a small `birthdays.txt` file in whatever folder you run it from, so it doesn't have to re-read and re-format your list every single time.

---

## Installation

The command is a small Bash wrapper that calls a Python script. To make it available system-wide:

```bash
chmod +x birthday_status birthday_status.py
ln -sf "$(pwd)/birthday_status" ~/.local/bin/birthday_status
```

Because `~/.local/bin` is already on your `PATH` in Termux, you can now run `birthday_status` from anywhere.

---

## How it works (technical)

### Data flow

```
/storage/emulated/0/Notes/Personal/Birthday   (your raw list)
                │
                │  parse + normalize (only if no local cache exists)
                ▼
        ./birthdays.txt   (cache, in the CURRENT working directory)
                │
                │  compute days-until + sort
                ▼
             stdout
```

1. **Cache-first:** If `birthdays.txt` exists in the current directory, it is read directly and the raw source is ignored.
2. **Otherwise:** the source file is parsed, normalized, and written to `birthdays.txt` in the current directory.
3. Entries are turned into `(name, day, month, year)` tuples.
4. `days_until` is the difference between today and the **next occurrence** of that month/day.
5. Anyone with `days_until == 0` is printed in the "Today is ..." block; everyone else is sorted ascending by `days_until` and printed as a table.

### `birthdays.txt` format

Pipe-separated, one record per line:

```
Name|DD|MM|YYYY
```

- `YYYY` is left **empty** when the original entry had no year (`Aaron|28|03|2004`, `Emiley|24|03|`).
- This file is written by the tool and is **git-ignored** because it contains personal data.

### Supported input formats

The parser is deliberately forgiving. A line is `Name` and a date separated by `:` (an optional `-` after the colon is ignored).

| Example input line             | Interpreted as        |
| ------------------------------ | --------------------- |
| `Aaron :- March 28 (28/03/2004)` | 28/03/2004           |
| `Mom :- April 25 1975`         | 25/04/1975            |
| `Emiley :- March 24`           | 24/03 (no year)       |
| `Gurusaran :- 12 May`          | 12/05 (no year)       |

The parenthesised `(DD/MM/YYYY)` is treated as the source of truth when present. Otherwise the parser looks for a month name, then a day number (1–31), then a 4-digit year.

**Skipped entries** (no day + month available):

| Example input line | Why it is skipped          |
| ------------------ | -------------------------- |
| `Asrita :- Dec`    | month only, no day         |
| `Sri haran :- `    | empty date                 |

### Date edge cases

- The countdown is based only on **month/day**, never the year.
- If today is the birthday, the next occurrence is **today** (`0` days).
- **Feb 29** is mapped to **Feb 28** in non-leap years.
- Each run uses a fresh `date.today()`, so results are always current.

### Files in this repository

| File                 | Role                                                     |
| -------------------- | -------------------------------------------------------- |
| `birthday_status`    | Bash wrapper; finds its own directory and runs the Python |
| `birthday_status.py` | All the parsing, date math, and formatting logic          |
| `README.md`          | This document                                             |
| `LICENSE`            | MIT license                                               |
| `.gitignore`         | Keeps personal data and junk out of git                   |

### Configuration

To point the tool at a different raw list, edit the constant at the top of `birthday_status.py`:

```python
SOURCE_FILE = "/storage/emulated/0/Notes/Personal/Birthday"
```

---

## Requirements

- **Termux** on Android (or any Linux with a compatible bash path).
- **Python 3** (Termux ships with it).

> The wrapper uses the shebang `#!/data/data/com.termux/files/usr/bin/bash` and the script is executed with `python3`. `/usr/bin/env` does not exist on Termux, which is why the absolute Termux bash path is used.

---

## Privacy

Your real birthdays live in one private text file (`birthdays.txt` and the raw source). `birthdays.txt` is listed in `.gitignore`, so it is **never** committed or uploaded. Only the code goes to GitHub.

---

## Troubleshooting

| Symptom                              | Fix                                                                 |
| ------------------------------------ | ------------------------------------------------------------------- |
| `command not found: birthday_status` | Re-run the `ln -sf ... ~/.local/bin/` step above.                    |
| `source file not found`              | Check the path in `SOURCE_FILE` and that the file exists.           |
| `no valid birthdays found`           | Check that your lines are `Name :- date` and have at least a day and month. |
| Wrong/old data                       | Delete `birthdays.txt` in the current directory and run again.      |

---

## License

Released under the [MIT License](LICENSE).
