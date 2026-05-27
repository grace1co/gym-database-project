# Gym Database Project

A gym membership database system built with Oracle SQL, PL/SQL, and Python. This project manages gym locations, members, membership plans, active memberships, check-ins, and reporting queries.

## Features

- Creates a normalized gym membership database schema
- Stores gym locations, members, plans, memberships, and check-ins
- Uses SQL constraints for data validation
- Includes PL/SQL triggers for business rules
- Tracks active and inactive memberships
- Validates member check-ins
- Includes reporting queries for membership and gym activity
- Provides a simple Python GUI for viewing gym data

## Tech Stack

- Oracle SQL
- PL/SQL
- Python
- Tkinter
- oracledb

## Files

| File | Description |
|---|---|
| `gym.sql` | Main database schema, inserts, views, triggers, and procedures |
| `Queries.txt` | SQL queries used for testing and reporting |
| `gym_output.txt` | SQL output/results from running the database project |
| `gym_gui.py` | Python GUI for interacting with the gym database |

## What I Learned

This project helped me practice relational database design, SQL joins, constraints, triggers, views, and connecting a Python interface to an Oracle database. I also learned how to structure a database around real business rules, such as requiring a member to have an active membership before checking in.

## Future Improvements

- Add login authentication for gym staff
- Improve the GUI design
- Add member search and filtering
- Add reports for monthly revenue and attendance trends
- Add better error handling for invalid check-ins

## Presentation & Demo

### Demo Video
Watch the full video here:
https://youtu.be/9flpTS8G9zY

### Presentation Slides
https://docs.google.com/presentation/d/1nGVk4JfzUP3VE6tINBu4m4al-NdD1gXgdDZ80Fs-12Y/edit?usp=sharing
