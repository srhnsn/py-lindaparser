Linda Parser
============
This program has a [port in Go](https://github.com/srhnsn/go-lindaparser).

Requirements
------------
* Python 3

Usage
-----
### Preparation
1. Open a console window.
1. Change into the directory of the program.
1. Set the environment variables `HHN_USERNAME` and `HHN_PASSWORD` to your HHN login credentials.  
On Windows: `SET HHN_USERNAME=foobar` and `SET HHN_PASSWORD=mypassword`

### Average grade calculator
Run `python calculate_average_grades.py`. If will fetch the current exam results and will present them and print the average grades. The view is separated by the Grundstudium and the Hauptstudium.

It is possible to adjust wrong ECTS values on Linda by modifying the `ECTS_FIX` variable at the top of `lindaparser.py`. The key of the dictionary must be the course ID number as an integer.

### New exam finder
Run `python find_new_exams.py`. On the first run, the program will create an `exams.json` file containing all currently available exam information. If you run the command again, it will print any new exam results it finds on Linda. If it does not find any new exam results, the program will not output anything.
