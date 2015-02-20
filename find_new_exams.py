import json
import os
import socket
import sys
import time

import lindaparser

USERNAME = os.getenv("HHN_USERNAME")
PASSWORD = os.getenv("HHN_PASSWORD")

ATTEMPT_DELAY = 20
EXAMS_CACHE = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "exams.json")
MAX_ATTEMPTS = 3

attempts = 0


def find_new_exams(current_exams, cached_exams):
    if cached_exams is None:
        return []
    
    new_exams = []
    
    for current_exam in current_exams:
        if current_exam not in cached_exams:
            new_exams.append(current_exam)
    
    return new_exams


def get_cached_exams():
    try:
        fh = open(EXAMS_CACHE, "r", encoding="utf-8")
    except FileNotFoundError:
        return
    
    content = json.load(fh)
    fh.close()
    return content


def log(*args, **kwargs):
    pass
    print(*args, **kwargs)



def main():
    global attempts
    attempts += 1
    
    try:
        try_new_attempt()
        return
    except (lindaparser.AttemptError, socket.timeout) as e:
        log("Error: {}".format(repr(e)))
    
    if attempts >= MAX_ATTEMPTS:
        print("Aborting after {} unsuccessful attempts".format(MAX_ATTEMPTS))
        sys.exit(1)
    
    log("Trying again in {} seconds".format(ATTEMPT_DELAY))
    
    time.sleep(ATTEMPT_DELAY)
    main()


def save_exams(exams):
    fh = open(EXAMS_CACHE, "w", encoding="utf-8")
    json.dump(exams, fh, indent=4)
    fh.close()


def try_new_attempt():
    if not USERNAME:
        print("HHN_USERNAME not set")
        sys.exit(1)
    
    if not PASSWORD:
        print("HHN_PASSWORD not set")
        sys.exit(1)
    
    lindaparser.login(USERNAME, PASSWORD)
    current_exams = lindaparser.get_current_exams()
    
    cached_exams = get_cached_exams()
    save_exams(current_exams)
    new_exams = find_new_exams(current_exams, cached_exams)
    
    if not new_exams:
        sys.exit()
    
    for new_exam in new_exams:
        print("{semester}: {name}".format(**new_exam))


if __name__ == "__main__":
    main()
