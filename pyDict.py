import sys
import random
import re
import requests
from bs4 import BeautifulSoup
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette
from PyQt5.QtWidgets import *

def randHeader():
    ''' 随机生成Header '''
    head_connection = ['Keep-Alive', 'close']
    head_accept = ['text/html, application/xhtml+xml, */*']
    head_accept_language = ['zh-CN,fr-FR;q=0.5', 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3']
    head_user_agent = ['Opera/8.0 (Macintosh; PPC Mac OS X; U; en)',
                       'Opera/9.27 (Windows NT 5.2; U; zh-cn)',
                       'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0)',
                       'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)',
                       'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E)',
                       'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E; QQBrowser/7.3.9825.400)',
                       'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; BIDUBrowser 2.x)',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070309 Firefox/2.0.0.3',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.12) Gecko/20080219 Firefox/2.0.0.12 Navigator/9.0.0.6',
                       'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; rv:11.0) like Gecko)',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0 ',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Maxthon/4.0.6.2000 Chrome/26.0.1410.43 Safari/537.1 ',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.92 Safari/537.1 LBBROWSER',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/3.0 Safari/536.11',
                       'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
                       'Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en) Opera 8.0'
                       ]
    header = {
        'Connection': head_connection[0],
        'Accept': head_accept[0],
        'Accept-Language': head_accept_language[1],
        'User-Agent': head_user_agent[random.randrange(0, len(head_user_agent))]
    }
    return header

def getCurrentTime():
    # 获取当前时间
    return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))
	
def getURL(url, tries_num=5, sleep_time=0, time_out=10, max_retry=5, isproxy=0, proxy=None, encoding='utf-8'):
    ''' 获取网页 '''
    header = randHeader()
    try:
        res = requests.Session()
        if isproxy == 1:
            if proxy is None:
                print('===   proxy is empty     ====')
                return None
            res = requests.get(url, headers=header, timeout=time_out, proxies=proxy)
        else:
            res = requests.get(url, headers=header, timeout=time_out)
        res.raise_for_status()
    except requests.RequestException as e:
        if tries_num > 0:
            time.sleep(sleep_time)
            print(getCurrentTime(), url, 'URL Connection Error in ', max_retry-tries_num, ' try')
            return getURL(url, tries_num-1, sleep_time+10, time_out+10, max_retry, isproxy, proxy)
        return None
        
    res.encoding = encoding # 指定网页编码格式
    return res

def queryWords(word):
    ''' 利用有道翻译查询单词 '''
    url = 'http://dict.youdao.com/w/{}/'.format(word)
    html = getURL(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    trans_container = soup.find(class_='trans-container')
    
    if not trans_container:
        ''' not found the translation '''
        return [word]
        
    trans_li = trans_container.find_all('li')
    trans_data = [li.text.strip() for li in trans_li]
    return trans_data

class CustomWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self._initUI()
        
    def _initUI(self):
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.on_clipboard_changed)
        
        word_label = QLabel(self)
        word_label.setFont(QFont('Roman times', 20, QFont.Bold))
        
        trans_list = QListWidget(self)
        trans_list.setFont(QFont('normal', 12, QFont.Thin))
        
        grid = QGridLayout()
        grid.setSpacing(10)
        
        grid.addWidget(word_label, 1, 0)
        grid.addWidget(trans_list, 2, 0)
        
        self.word_label = word_label
        self.trans_list = trans_list
        
        pe = QPalette()
        pe.setColor(QPalette.WindowText, Qt.black) #设置字体颜色 
        pe.setColor(QPalette.Window, Qt.white) #设置背景颜色
        
        self.setAutoFillBackground(True)
        self.setPalette(pe)
        self.setLayout(grid)
        self.setGeometry(100, 100, 400, 240)
        self.setWindowTitle('有道翻译')
        self.show()
        
    def setWord(self, word):
        self.word_label.setText(word)
        self.word_label.adjustSize()
        
    def setTrans(self, trans):
        self.trans_list.clear()
        self.trans_list.addItems(trans)
        self.trans_list.adjustSize()
        
    def on_clipboard_changed(self):
        data = self.clipboard.mimeData()
        if data.hasText():
            word = data.text().strip()
            m = re.match(r'[a-zA-Z]+', word)
            if m:
                self.setWord(word)
                #self.setWindowFlags(self.windowFlags() & QtCore.Qt.WindowStaysOnTopHint)
                #self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
                trans = queryWords(word)
                self.setTrans(trans)
                
                ''' tip the window content has changed, but cannot move the window to the forground'''
                self.activateWindow()
                
            else:
                print(word)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CustomWindow()
    sys.exit(app.exec_())
    