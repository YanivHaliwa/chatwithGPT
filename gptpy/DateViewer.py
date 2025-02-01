#!/usr/bin/env python3
import datetime

def show_date():
    today = datetime.date.today()
    print(today.strftime("%Y-%m-%d"))

if __name__ == "__main__":
    show_date()