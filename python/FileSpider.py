#coding: utf8
import os
import re
import time
import codecs
class FileSpider(object):
	def __init__(self):
		self.result = []
	def getResult(self, filepath):
		res = os.walk(filepath)
		for path,d,filelist in res:
			for filename in filelist:
				if os.path.splitext(filename)[1] == '.ftl':
					#print os.path.join(path, filename)
					self.result.append(os.path.join(path,filename))
		return self.result

class LableScan(object):
	def __init__(self):
		self.lables_cn = []
		self.lables_ot = []

	def check_contain_cn(self, check_str):
		for ch in check_str.decode('utf-8'):
			if u'\u4e00' <= ch <= u'\u9fa5':
				return True
		return False

	def check_is_cn(self, check_str):
		if check_str == "":
			return False

		for ch in check_str.decode('utf-8'):
			if u'\u4e00' > ch or   u'\u9fa5' < ch:
				return False
		return True
		

	def getLableFromFile(self, pattern, filepath):
		f = open(filepath)
		#f = codecs.open(filepath, 'r', 'utf-8')
		labs = re.findall(pattern, f.read(), re.S)
		if labs:
			for lab in labs:
				#cn_chk = re.findall(u"([\u4e00-\u9fa5]+)", lab)
				if self.check_is_cn(lab.strip()):
					self.lables_cn.append(lab.strip())
				else:
					self.lables_ot.append(lab)

	def getLablesCN(self):
		return self.lables_cn

	def getDistictLablesCN(self):
		return list(set(self.lables_cn))
		
a = FileSpider()
filelist = a.getResult('/home/citicbank/workspace/cbps-web')

pattern1 = r'<label.*?>(.*?)</label>'
pattern2 = u'<h[0-9]>([\u4e00-\u9fff]+?)</h[0-9]>'
pattern3 = r'<th.*?>(.*?)</th>'
ls = LableScan()
for filename in filelist:
	ls.getLableFromFile(pattern1, filename)
	ls.getLableFromFile(pattern2, filename)
	ls.getLableFromFile(pattern3, filename)
f = open('lable.out', 'w')
for line in ls.getDistictLablesCN():
	f.write(line + '\n')
