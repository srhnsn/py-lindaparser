import html
import http.cookiejar
import os
import re
import urllib


FIELD_PASSWORD = "fdsa"
FIELD_USERNAME = "asdf"
PATTERN_ASI = r'''asi=([^"^&]+)'''
PATTERN_GRADES = r'''<tr>''' + r'''\s*<td[^>]*>(.+?)</td>\s*''' * 10 + r'''</tr>'''
REQUEST_TIMEOUT = 20
URL_EXAM_OVERVIEW = r"https://linda.hs-heilbronn.de/qisstudent/rds?state=change&type=1&moduleParameter=studyPOSMenu&nextdir=change&next=menu.vm&subdir=applications&xml=menu&purge=y&navigationPosition=functions%2CstudyPOSMenu&breadcrumb=studyPOSMenu&topitem=functions&subitem=studyPOSMenu"
URL_GRADES = r"https://linda.hs-heilbronn.de/qisstudent/rds?state=notenspiegelStudent&next=list.vm&nextdir=qispos/notenspiegel/student&createInfos=Y&struct=auswahlBaum&nodeID=auswahlBaum%7Cabschluss%3Aabschl%3D84%2Cstgnr%3D1&expand=0&asi={asi}"
URL_LOGIN = r"https://linda.hs-heilbronn.de/qisstudent/rds?state=user&type=1&category=auth.login&startpage=portal.vm&breadCrumbSource=portal"
USER_AGENT = r"Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36"

ECTS_FIX = {
    281811: 5.0,
}

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


class AttemptError(Exception):
    pass


def get_asi():
    content = get_content(URL_EXAM_OVERVIEW)
    match = re.search(PATTERN_ASI, content)
    
    if not match:
        raise AttemptError("Could not parse ASI")
    
    return match.group(1)


def get_content(url, data=None):
    request = get_request(url, data)
    result = opener.open(request, timeout=REQUEST_TIMEOUT)
    return result.read().decode("utf-8")


def get_current_exams():
    asi = get_asi()
    grades_url = URL_GRADES.format(asi=asi)
    content = get_content(grades_url)
    exams = parse_grades_page(content)
    return exams


def get_request(url, data=None):
    if data:
        data = urllib.parse.urlencode(data).encode("utf-8")
    
    header = {
        "User-Agent": USER_AGENT,
    }
    
    return urllib.request.Request(url, data, header)


def login(username, password):
    jar.clear()
    
    data = {
        FIELD_USERNAME: username,
        FIELD_PASSWORD: password,
    }
    
    get_content(URL_LOGIN, data)


def parse_ects(ects_str):
    return float(ects_str.replace(",", "."))


def parse_id(id_str):
    return int(id_str)


def parse_grade(grade_str):
    match = re.search(r"^(\d+,\d+)", grade_str)
    
    if not match:
        return None
    
    return float(match.group(1).replace(",", "."))


def parse_passed(pass_str):
    return pass_str == "bestanden"


def parse_grades_page(content):
    raw_exams = re.findall(PATTERN_GRADES, content, re.DOTALL)
    exams = []
    
    for raw_exam in raw_exams:
        raw_exam = tuple(map(lambda x: x.strip(), raw_exam))
        
        exam = {
            "course_type": raw_exam[6],
            "ects": parse_ects(raw_exam[7]),
            "grade": parse_grade(raw_exam[1]),
            "id": parse_id(raw_exam[0]),
            "name": raw_exam[9],
            "passed": parse_passed(raw_exam[2]),
            "semester": raw_exam[8],
        }
        
        if not exam["ects"] and exam["id"] in ECTS_FIX:
            exam["ects"] = ECTS_FIX[exam["id"]]
        
        exams.append(exam)
    
    return exams
