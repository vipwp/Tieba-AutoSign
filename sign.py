#!/usr/bin/env python
#coding=gbk
#email:jeos@live.fi
import urllib
import urllib2
import cookielib
import json
import re,time,os,random,sys,base64
import getpass
import optparse
try:
  from accounts import accounts_here
except:
  pass

class TieBa:
  def __init__(self,username,password):
    self.username=username.decode("utf8").encode("gbk")
    self.password=password
    cj = cookielib.CookieJar()
    self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    self.opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux i686)')]
    urllib2.install_opener(self.opener)

  def urlopen(self,*args):
    try:
      if len(args)==1:
        fd=urllib2.urlopen(args[0])
      else:
        req = urllib2.Request(args[0], urllib.urlencode(args[1]))
        fd = urllib2.urlopen(req)
      return fd.read()
    except urllib2.HTTPError:
      print ('Error = =')
      time.sleep(1)
      if len(args)>1 and 'tbs' in args[1]:
        if 'tid' in args[1]:
          args[1]['tbs']=self.getTbs(args[1]['tid'])
        else:
          args[1]['tbs']=self.getTbs()
      self.urlopen(*args)


  def getFid(self):
    page = self.urlopen(self.tb_url)
    fid=re.findall("fid:'(\d+)'",page)
    if fid==[]:
      print ('Error = = Retry in 1s')
      time.sleep(1)
      return self.getFid()
    else:
      return fid[0]


  def getTbs(self,tid=None):
    if tid:
      page = self.urlopen("http://tieba.baidu.com/p/%s"%tid)
      print  ("http://tieba.baidu.com/p/%s"%tid)
      tbs=re.findall("'tbs'  : \"(\w+)\"",page)[0]
    else:
      page = self.urlopen(self.tb_url)
      tbs=re.findall('PageData.tbs = "(\w+)"',page)[0]

    return tbs


  def sign(self): #手机版签到
    sign_url="http://wapp.baidu.com/f/q/sign"
    data={'kw':self.kw}
    data['tbs']=self.getTbs()
    try:
      res = self.urlopen(sign_url,data).decode("u8").encode("gbk")
      tbk = re.findall('</a>(.+)<div class="bc">',res)[0]
    except:
      tbk = "签到异常"
	  
    #print res
   
    from HTMLParser import HTMLParser
    html=tbk
    html=html.strip()
    html=html.strip("\n")
    result=[]
    parse=HTMLParser()
    parse.handle_data=result.append
    parse.feed(html)
    parse.close()
    print "".join(result)
	
#  这一段注释是电脑版签到代码
#  def sign(self):
#    sign_url="http://tieba.baidu.com/sign/add"
#    data={'ie':'utf-8','kw':self.kw}
#    data['tbs']=self.getTbs()
#    res = self.urlopen(sign_url,data)
#    try:
#      res = json.loads(res)
#    except:
#      pass
#    if not res or res['error']!='':
#      print  ('Failed or Already Signed')
#    else:
#      print  ('Successful','You are the %dth Sign'%res['data']['finfo']['current_rank_info']['sign_count'])

  def login(self):
    def post():
      url = 'https://passport.baidu.com/v2/api/?login'
      page = self.urlopen(url,data)

    data={"username":self.username,"password":self.password,"verifycode":'',
        "mem_pass":"on","charset":"GBK","isPhone":"false","index":"0",
        "safeflg":"0","staticpage":"http://tieba.baidu.com/tb/v2Jump.html",
          "loginType":"1","tpl":"tb","codestring":'',
          "callback":"parent.bdPass.api.loginLite._submitCallBack"}

    post()
    token_url="https://passport.baidu.com/v2/api/?loginliteinfo&username=%s&isPhone=false&tpl=tb&immediatelySubmit=false&index=0&t=1345615911499"%self.username
    token_page=self.urlopen(token_url)
    data["token"]=re.findall("token:'(\w+)'" ,token_page)[0]
    post()

    return True

  def enter(self,tb_url):
    if tb_url.startswith('http://'):
      self.tb_url=tb_url
    else:
      self.tb_url="http://tieba.baidu.com%s"%tb_url
    self.fid=self.getFid()
    self.kw=re.findall("kw=([%\w]+)",self.tb_url)[0]
    self.kw=urllib.unquote(self.kw)

    print "签到 "+self.kw+" 吧"

  def getTibBas(self):
    page=self.urlopen('http://tieba.baidu.com/')
    return re.findall('<a class="j_ba_l.+" forum-id="\d+" forum=".+" forum-type="\d+" forum-like="1" href="(.+)" target="_blank"',page)


def main():
#   如果要指定用户名那就从这里开始注释
    parser = optparse.OptionParser()  
    parser.add_option("-u", "--usr", dest="u",  
                  help="username", metavar="username ")  
    parser.add_option("-p", "--psw", dest="p",
                  help="password", metavar="password ")  
    parser.add_option("-f", "--frm", dest="f",
                  help="forum name", metavar="forumname")  
    parser.add_option("-b", "--b64", dest="b",
                  help="base64 encoded password", metavar="[BASE64] ")  
    parser.add_option("-r", "--r13", dest="r",
                  help="rotate13 encoded password", metavar="[ROT_13] ") 
    (options, args) = parser.parse_args()  
    if options.u:
      u=options.u.decode("gbk").encode("u8")
    else:
      u=raw_input('输入用户名: ').decode("gbk").encode("u8")
    if options.p:
      p=options.p
    else:
      if options.b:
        p=base64.decodestring(options.b)
      else:
        if options.r:
          p=options.r.encode('rot13')
        else:
          print '输入密码: '
          p=getpass.getpass('')
#   注释到这里为止
    #u='YOUR_USERNAME'
    #p='PASSWORD'
    print u.decode("u8").encode("gbk")+' 开始签到'
    t = TieBa(u,p)
    if t.login():
      if options.f:
          t.enter('http://tieba.baidu.com/f?kw='+options.f+'&fr=itb_favo&fp=favo')
          t.sign()
      else:
        for i in t.getTibBas():
          t.enter(i)
          t.sign()
    print '签到完成'

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit("操作被用户中止.")
