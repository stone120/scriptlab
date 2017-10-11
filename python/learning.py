#coding=utf-8
import urllib
import urllib2
import cookielib
import re
import time
import os
import sys
import fileinput
#from urlgrabber.keepalive import HTTPHandler

_choice_course_file='course.txt'
_cookie_file='cookie.txt'
_user_name='user'
_passwd='passwd'

user_agent = 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)'
headers = {
        'User-Agent' : user_agent,
        'Accept-Language' : 'zh-CN'
        }
def print_cookie(cookie):
    for item in cookie:
        print('Name =' + item.name)
        print('Value =' + item.value)

def logout(opener):
    logout_url = 'http://learningcourse.webdomain.com:81/ksproduct/core/user/otherlogonout.action '
    opener.open(logout_url)
    
def examlogout(opener):
    url = 'http://learning.webdomain.com/exam/app/exam/login/logout.jsp'
    opener.open(url)

def login(opener):
    login_url = 'http://learning.webdomain.com/jsp/ldaplogining.jsp'
    login_data = { 'name': _user_name, 'pwd' : _passwd }
    data = urllib.urlencode(login_data)
    opener.open(login_url, data)

def search_lesson(opener, le_name):
    url = ' http://learning.webdomain.com/cmd/StudentNewControl?flag=selectedLessonList&param1=' + le_name
    response = opener.open(url)
    return get_lesson_id(response.read())

def choice_course(opener, le_id):
    url = 'http://learning.webdomain.com/cmd/ChoiceCourseControl '
    post_data = { 'flag': 'insertSelectedLesson', 'us_id' : '186831', 'lessonInfo' : le_id + '*0.0&', 'le_id' : le_id}
    data = urllib.urlencode(post_data)
    opener.open(url, data)

def get_lesson(opener):
    get_lesson_url = 'http://learning.webdomain.com/cmd/StudentNewControl?flag=selectedLessonStudy&topMenu=02&leftMenu=01'
    get_lesson_data = { 'topMenu' : '02', 'leftMenu' : '01', 'content' : '' }
    data = urllib.urlencode(get_lesson_data)
    response = opener.open(get_lesson_url, data)
    html = response.read()
    return html

def get_lesson_id(html):
    pattern = """<a[^>]+href=["']javascript:_openLessonDetail\((.*?)\);["']"""
    webpage_regex = re.compile(pattern, re.IGNORECASE)
    return webpage_regex.findall(html)

def get_lesson_info(html):
    pattern = """onClick=["']javascript:_enterCourse[1-9]{0,1}\((.*?)\);["']"""
    webpage_regex = re.compile(pattern, re.IGNORECASE)
    return webpage_regex.findall(html)

def get_SCOID(html):
    pattern = """top.window.API.setSCOID\('(.*?)'\);"""
    webpage_regex = re.compile(pattern, re.IGNORECASE)
    result = webpage_regex.findall(html)
    if result:
        return result[0]
    else:
        return 'ZX0101'


def learn_lesson(opener, le_id):
    learn_url = "http://learning.webdomain.com/cmd/LessonStudyControl?flag=study&tl_id=&le_id=" + le_id +"&isStation=0&tc_id=1&type=4&isEnty=1&isSelected=1"
    #learn_url = "http://learningcourse.webdomain.com:81/jsp/scorm/classroom/Classroom.jsp?intFrameFlip=180&tl_id=0&le_id=" + le_id + "&us_id=186831&sessionUTDID=5996569&sessionStudyTime=" + str(long(time.time()) - 3600)
    response = opener.open(learn_url)

    # 2. refresh course
    learn_url_2 = 'http://learning.webdomain.com/cmd/LessonStudyControl?flag=refreshCourseware'
    refer_url = response.geturl()

    # refer_url_1 : sessionStudyTime changed
    refer_url_1 = refer_url
    patten = 'sessionStudyTime='
    find_rst = refer_url.find(patten)

    if find_rst != -1:
        session_study_time = refer_url[find_rst:].split(patten)[1]
        print(session_study_time)
        refer_url_1 = refer_url[0:find_rst-1] + patten + str(long(session_study_time) - 3600)
        print(refer_url)

def get_SCOID(html):
    pattern = """top.window.API.setSCOID\('(.*?)'\);"""
    webpage_regex = re.compile(pattern, re.IGNORECASE)
    result = webpage_regex.findall(html)
    if result:
        return result[0]
    else:
        return 'ZX0101'


def learn_lesson(opener, le_id, tl_id, le_type, tc_id, is_station, str_type):
    learn_url = "http://learning.webdomain.com/cmd/LessonStudyControl?flag=study&tl_id=" + tl_id  + "&le_id=" + le_id +"&isStation=" + is_station + "&tc_id="+ tc_id + "&type="+ le_type + "&isEnty=1&isSelected=1"
    if str_type != "":
        learn_url = learn_url + "&strType="+str_type
    response = opener.open(learn_url)

    # 2. refresh course
    learn_url_2 = 'http://learning.webdomain.com/cmd/LessonStudyControl?flag=refreshCourseware'
    refer_url = response.geturl()

    # refer_url_1 : sessionStudyTime changed
    refer_url_1 = refer_url
    patten = 'sessionStudyTime='
    find_rst = refer_url.find(patten)

    if find_rst != -1:
        session_study_time = refer_url[find_rst:].split(patten)[1]
        print(session_study_time)
        refer_url_1 = refer_url[0:find_rst-1] + patten + str(long(session_study_time) - 3600)
        print(refer_url)
    #opener.open(refer_url_1)  # reopen url with time changed
    #opener.addheaders = [('Referer',refer_url_1),('User-Agent',user_agent),('Accept-Language','zh-CN')]


    opener.addheaders = [('Referer',refer_url),('User-Agent',user_agent),('Accept-Language','zh-CN')]
    opener.open(learn_url_2)

    if le_type == "2":
        return ""
    # 3. 
    learn_url_3 = 'http://learningcourse.webdomain.com:81/jsp/scorm/classroom/ScormAPI.jsp?tl_id=0&le_id=' + le_id + '&us_id=186831&distrURL=null'
    opener.open(learn_url_3)

    # 4. get scoid
    learn_url_4 = 'http://learningcourse.webdomain.com:81/jsp/scorm/classroom/CurrentChapter.jsp?tl_id=' + le_id +'&le_id=' + le_id +'&us_id=186831'
    response4 = opener.open(learn_url_4)
    return get_SCOID(response4.read())

def set_lesson_complete(opener, le_id, scoid):
    post_url = 'http://learningcourse.webdomain.com:81/jsp/scorm/classroom/ScormLMSPut.jsp'
    post_data = 'us_id=186831&le_id=' +  le_id+ '&scoID=' + scoid + '&dataXML=<?xml version="1.0" encoding="GB2312" ?><root><CMICore><student_id>186831</student_id><student_name>peaktele</student_name><lesson_location></lesson_location><credit>credit</credit><lesson_status>completed</lesson_status><entry>ab-initio</entry><CMIScore><raw>0</raw><min>60</min><max>100</max></CMIScore><total_time>0000:50:00.00</total_time><lesson_mode>normal</lesson_mode><exit></exit><session_time>00:00:00.0</session_time><lesson_progress></lesson_progress></CMICore><suspend_data></suspend_data><launch_data></launch_data><comments></comments></root>'
    refer_url = 'http://learningcourse.webdomain.com:81/jsp/scorm/classroom/ScormAPI.jsp?tl_id=0&le_id=' + le_id + '&us_id=186831&distrURL=null'
    opener.addheaders = [('Accept','*/*'),('User-Agent',user_agent),('Accept-Language','zh-CN'),('Accept-Encoding','gzip, deflate'),('Content-Type','application/x-www-form-urlencoded'),('Referer',refer_url),('Connection','Keep-Alive'),('Pragma','no-cache')]
    response = opener.open(post_url, post_data)

def exit_learn_lesson(opener, le_id):
    exit_lesson_url = 'http://learning.webdomain.com/jsp/common/lessonstudy/ExitClassroom.jsp?us_id=186831&le_id=' + le_id
    response = opener.open(exit_lesson_url)

def run():
    cookie=cookielib.MozillaCookieJar(_cookie_file)
    if os.path.exists(_cookie_file):
    	cookie.load(ignore_discard=True, ignore_expires=True)
    handler=urllib2.HTTPCookieProcessor(cookie)
    opener=urllib2.build_opener(handler)
    opener.addheaders = [('User-Agent',user_agent),('Accept-Language','zh-CN')]

    #keepalive_handler = HTTPHandler()
    #opener2 = urllib2.build_opener(keepalive_handler)

    logout(opener)
    print_cookie(cookie)
    examlogout(opener)
    login(opener)

    # choice course
    if len(sys.argv) >0 :
        if os.path.exists(_choice_course_file):
            for line in fileinput.input(_choice_course_file):
                for le_id in search_lesson(opener, line):
                    print(le_id)
                    choice_course(opener, le_id)

    #exit()
    # learn course
    html = get_lesson(opener)
    #for lessid in get_lesson_id(html):
    for le_info in get_lesson_info(html):
        print(le_info)
        le_info_arr = le_info.split(',')
        le_id = le_info_arr[0].replace("'",'')
        tl_id = le_info_arr[1].replace("'",'')
        le_type = le_info_arr[2].replace("'",'')
        tc_id = le_info_arr[3].replace("'",'')
        is_station = le_info_arr[4].replace("'",'')
        str_type = ""
        if len(le_info_arr) >= 8:
            str_type = le_info_arr[7].replace("'",'')
        time.sleep(5)
        scoid = learn_lesson(opener, le_id, tl_id, le_type, tc_id, is_station,str_type)
        time.sleep(5)
        print(scoid)
        if scoid != "":
            set_lesson_complete(opener, le_id, scoid)
            time.sleep(5)
        exit_learn_lesson(opener, le_id)
        #exit()
    # save cookie
    cookie.save(ignore_discard=True, ignore_expires=True)
run()

# test code
def test_get_lesson_id():
    html = r'''<td width="57%"> <a href="javascript:_enterLessonDetail('218466');" class="blue1">p</a> </td>'''
    for lessid in get_lesson_id(html):
        print(lessid)

#test_get_lesson_id()
