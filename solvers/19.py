from typing import Dict


def is_leap_year(year: int) -> bool:
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0


def days_in_month(year: int, month: int) -> int:
    # month: 1..12
    if month == 2:
        return 29 if is_leap_year(year) else 28
    if month in (4, 6, 9, 11):
        return 30
    return 31


def count_sundays_on_first(start_year: int, end_year: int) -> int:
    # Day of week encoding: 0=Mon, 1=Tue, ..., 6=Sun
    dow_first_of_month = 0  # 1 Jan 1900 was Monday

    count = 0
    for year in range(1900, end_year + 1):
        for month in range(1, 13):
            if start_year <= year <= end_year and dow_first_of_month == 6:
                count += 1

            dow_first_of_month = (dow_first_of_month + days_in_month(year, month)) % 7
    return count


def main() -> None:
    ans = count_sundays_on_first(1901, 2000)
    print(ans)


if __name__ == "__main__":
    main()
