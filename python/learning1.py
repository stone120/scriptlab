#coding=utf-8
import urllib
import urllib2
import cookielib
import re
import time
import os
import sys
import fileinput

_choice_course_file='course.txt'  # 选课功能，课程列表
_cookie_file='cookie1.txt'  # 可以不存在
#_learn_by_time=False   # 是否学满 _time 分钟

user_agent = 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)'
headers = {
        'User-Agent' : user_agent,
        'Accept-Language' : 'zh-CN'
        }
class LearnCourse():
    def __init__(self, user_name, passwd, learn_by_time):
        self.user_name = user_name
        self.passwd = passwd
        self.learn_by_time = learn_by_time

        self.us_id = ""
        cookie = cookielib.MozillaCookieJar(_cookie_file)
        if os.path.exists(_cookie_file):
            cookie.load(ignore_discard=True, ignore_expires=True)
        handler = urllib2.HTTPCookieProcessor(cookie)
        self.opener = urllib2.build_opener(handler)
        self.opener.addheaders = [('User-Agent',user_agent),('Accept-Language','zh-CN')]
    
    def run(self):
        self.logout()
        self.examlogout()

        # login 
        self.login()
    
        # choice course
        if os.path.exists(_choice_course_file):
            print("begin to choice course with:" + _choice_course_file)
            for line in fileinput.input(_choice_course_file):
                le_id_arr = self.search_lesson(line)
                for le_id in le_id_arr:
                    print("begin to choice lesson:" + le_id)
                    self.choice_course(le_id)
    
        # learn course
        html = self.get_lesson()
        page_no = 1
        #for le_info in get_lesson_info(html):
        for le_info in self.get_all_lesson_info(html, page_no):
            print("begin to learn lesson:" + le_info)
            le_info_arr = le_info.replace("'",'').split(',')
            le_time = int(float(le_info_arr[0]) * 60)
            le_id = le_info_arr[1]
            tl_id = le_info_arr[2]
            le_type = le_info_arr[3]
            tc_id = le_info_arr[4]
            is_station = le_info_arr[5]
            str_type = ""
            if len(le_info_arr) >= 8:
                str_type = le_info_arr[7]
            time.sleep(5)
            scoid = self.learn_lesson(le_id, tl_id, le_type, tc_id, is_station,str_type, le_time)
            
            time.sleep(5)
            if scoid != "":
                self.set_lesson_complete(le_id, scoid)
                time.sleep(5)
            self.exit_learn_lesson(le_id)
            #exit()
        # save cookie
        #cookie.save(ignore_discard=True, ignore_expires=True)

    def print_cookie(cookie):
        for item in cookie:
            print('Name =' + item.name)
            print('Value =' + item.value)

    def logout(self):
        logout_url = 'http://learningcourse.domainname.com:81/ksproduct/core/user/otherlogonout.action '
        self.opener.open(logout_url)
    
    def examlogout(self):
        url = 'http://learning.domainname.com/exam/app/exam/login/logout.jsp'
        self.opener.open(url)

    def login(self):
        login_url = 'http://learning.domainname.com/jsp/ldaplogining.jsp'
        login_data = { 'name': self.user_name, 'pwd' : self.passwd }
        data = urllib.urlencode(login_data)
        self.opener.open(login_url, data)

    def search_lesson(self, le_name):
        url = ' http://learning.domainname.com/cmd/StudentNewControl?flag=selectedLessonList&param1=' + le_name
        response = self.opener.open(url)
        html = response.read()
        self.us_id = self.get_us_id(html)
        le_id = self.get_lesson_id(html)
        return  le_id

    def get_us_id(self, html):
        pattern = """insertAfavouritesCourse&us_id=(.*?)&le_id="""
        webpage_regex = re.compile(pattern, re.IGNORECASE)
        res = webpage_regex.findall(html)
        if res:
            return  res[0]
    
    def choice_course(self, le_id):
        url = 'http://learning.domainname.com/cmd/ChoiceCourseControl '
        post_data = { 'flag': 'insertSelectedLesson', 'us_id' : self.us_id, 'lessonInfo' : le_id + '*0.0', 'le_id' : le_id}
        data = urllib.urlencode(post_data)
        self.opener.open(url, data)
    
    def get_lesson(self):
        get_lesson_url = 'http://learning.domainname.com/cmd/StudentNewControl?flag=selectedLessonStudy&topMenu=02&leftMenu=01'
        get_lesson_data = { 'topMenu' : '02', 'leftMenu' : '01', 'content' : '' }
        data = urllib.urlencode(get_lesson_data)
        response = self.opener.open(get_lesson_url, data)
        html = response.read()
        return html
    
    def get_lesson_id(self, html):
        choosen_pattern = """<input type="button" value="已选择" class="button_gray"/>"""
        choose_regex = re.compile(choosen_pattern, re.IGNORECASE)
        res = choose_regex.findall(html)
        if len(res) > 0:
            # have choose 
            return []
        pattern = """<a[^>]+href=["']javascript:_openLessonDetail\((.*?)\);["']"""
        webpage_regex = re.compile(pattern, re.IGNORECASE)
        return webpage_regex.findall(html)
    
    def get_lesson_info(self, html):
        pattern = """onClick=["']javascript:_enterCourse[1-9]{0,1}\((.*?)\);["']"""
        webpage_regex = re.compile(pattern, re.IGNORECASE)
        return webpage_regex.findall(html)
    
    def get_all_lesson_info(self, html, page_no):
        pattern = """onClick=["']javascript:_enterCourse[1-9]{0,1}\((.*?)\);["']"""
        webpage_regex = re.compile(pattern, re.IGNORECASE)
        all_lesson_info = webpage_regex.findall(html)
    
        time_pattern = """<td width="20%" class="gray2 font12">课时：(.*?)</td>"""
        time_regex = re.compile(time_pattern, re.IGNORECASE)
        time_list = time_regex.findall(html)
        for index,value in enumerate(time_list):
            all_lesson_info[index] = value + ',' + all_lesson_info[index]
        #print(all_lesson_info)
    
        # go next page and find lesson
        last_pattern = """<td  width="50px;" class="gray2">后一页</td>"""
        last_regex = re.compile(last_pattern, re.IGNORECASE)
        last_page = last_regex.findall(html)
        if len(last_page) > 0:
            return all_lesson_info
        else:
            url = 'http://learning.domainname.com/cmd/StudentNewControl?flag=selectedLessonStudy&content=&topMenu=02&leftMenu=01&currentPage=' +str(page_no + 1)
            response = self.opener.open(url)
            html = response.read()
            return  all_lesson_info + get_all_lesson_info(opener, html, page_no + 1)
    
    def get_SCOID(self, html):
        pattern = """top.window.API.setSCOID\('(.*?)'\);"""
        webpage_regex = re.compile(pattern, re.IGNORECASE)
        result = webpage_regex.findall(html)
        if result:
            return result[0]
        else:
            return 'ZX0101'
    
    
    def get_us_id_from_html(self, html):
        pattern = """us_id=(.*?)&le_id="""
        webpage_regex = re.compile(pattern, re.IGNORECASE)
        res = webpage_regex.findall(html)
        if res:
            #print(res[0])
            return  res[0]

    def get_us_id_from_url(self, url):
        pattern = """us_id=(.*?)&sessionUTDID="""
        webpage_regex = re.compile(pattern, re.IGNORECASE)
        res = webpage_regex.findall(url)
        if res:
            return  res[0]
    
    
    def learn_lesson(self, le_id, tl_id, le_type, tc_id, is_station, str_type, le_time):
        learn_url = "http://learning.domainname.com/cmd/LessonStudyControl?flag=study&tl_id=" + tl_id  + "&le_id=" + le_id +"&isStation=" + is_station + "&tc_id="+ tc_id + "&type="+ le_type + "&isEnty=1&isSelected=1"
        if str_type != "":
            learn_url = learn_url + "&strType="+str_type
        response = self.opener.open(learn_url)
    
        # 2. refresh course
        learn_url_2 = 'http://learning.domainname.com/cmd/LessonStudyControl?flag=refreshCourseware'
        refer_url = response.geturl()
    
    
        # get us_id
        if le_type == "2":
            self.us_id = self.get_us_id_from_html(response.read())
        else:
            self.us_id = self.get_us_id_from_url(refer_url)
        if self.us_id:
            print("current user id is:" + self.us_id)
        else:
            print("can't get us_id , exit")
            exit(1)
    
        # refer_url_1 : sessionStudyTime changed
        refer_url_1 = refer_url
        patten = 'sessionStudyTime='
        find_rst = refer_url.find(patten)
    
        if find_rst != -1:
            session_study_time = refer_url[find_rst:].split(patten)[1]
            #print(session_study_time)
            refer_url_1 = refer_url[0:find_rst-1] + patten + str(long(session_study_time) - 3600)
            #print(refer_url)
        #self.opener.open(refer_url_1)  # reopen url with time changed
        #opener.addheaders = [('Referer',refer_url_1),('User-Agent',user_agent),('Accept-Language','zh-CN')]
    
    
        self.opener.addheaders = [('Referer',refer_url),('User-Agent',user_agent),('Accept-Language','zh-CN')]
        if self.learn_by_time:
            print("begin learn lesson:" + le_id + " , and it will cost " + str(le_time) + " miniutes")
            #for i in range(_time):
            for i in range(le_time):
                time.sleep(60)
                self.opener.open(learn_url_2)
        else:
            self.opener.open(learn_url_2)


        if le_type == "2":
            return ""
        # 3. 
        learn_url_3 = 'http://learningcourse.domainname.com:81/jsp/scorm/classroom/ScormAPI.jsp?tl_id=0&le_id=' + le_id + '&us_id=' + self.us_id + '&distrURL=null'
        self.opener.open(learn_url_3)
    
        # 4. get scoid
        learn_url_4 = 'http://learningcourse.domainname.com:81/jsp/scorm/classroom/CurrentChapter.jsp?tl_id=' + le_id +'&le_id=' + le_id +'&us_id=' + self.us_id 
        response4 = self.opener.open(learn_url_4)
        return self.get_SCOID(response4.read())
    
    def set_lesson_complete(self, le_id, scoid):
        post_url = 'http://learningcourse.domainname.com:81/jsp/scorm/classroom/ScormLMSPut.jsp'
        post_data = 'us_id=' + self.us_id + '&le_id=' +  le_id+ '&scoID=' + scoid + '&dataXML=<?xml version="1.0" encoding="GB2312" ?><root><CMICore><student_id>' + self.us_id + '</student_id><student_name>peaktele</student_name><lesson_location></lesson_location><credit>credit</credit><lesson_status>completed</lesson_status><entry>ab-initio</entry><CMIScore><raw>0</raw><min>60</min><max>100</max></CMIScore><total_time>0000:50:00.00</total_time><lesson_mode>normal</lesson_mode><exit></exit><session_time>00:00:00.0</session_time><lesson_progress></lesson_progress></CMICore><suspend_data></suspend_data><launch_data></launch_data><comments></comments></root>'
        refer_url = 'http://learningcourse.domainname.com:81/jsp/scorm/classroom/ScormAPI.jsp?tl_id=0&le_id=' + le_id + '&us_id=' + self.us_id + '&distrURL=null'
        self.opener.addheaders = [('Accept','*/*'),('User-Agent',user_agent),('Accept-Language','zh-CN'),('Accept-Encoding','gzip, deflate'),('Content-Type','application/x-www-form-urlencoded'),('Referer',refer_url),('Connection','Keep-Alive'),('Pragma','no-cache')]
        response = self.opener.open(post_url, post_data)
    
    def exit_learn_lesson(self, le_id):
        exit_lesson_url = 'http://learning.domainname.com/jsp/common/lessonstudy/ExitClassroom.jsp?us_id=' + self.us_id + '&le_id=' + le_id
        response = self.opener.open(exit_lesson_url)
    
# test code
def test():
    user_name = raw_input('Please input user name:')
    passwd = raw_input ('Pleaase input password:')
    quick_learn =  raw_input('Y: quick learn, set course complete & exit;   N: learn X miniutes the course set,  .  Please input [Y, N]:')
    if quick_learn == 'Y':
        learn_by_time = False
    else:
        learn_by_time = True 

    learn_course = LearnCourse(user_name, passwd, learn_by_time)
    learn_course.run()

if __name__== '__main__':
    test()


