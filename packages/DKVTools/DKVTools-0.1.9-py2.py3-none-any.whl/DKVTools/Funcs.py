# -*- coding: UTF-8 -*-
# 创建时间：2018年3月9日21:29:09
# 创建人：  Dekiven_PC


import os
import sys
import platform
import zipfile
import shutil
# import subprocess
# import tempfile
'''
    常用工具函数
    python2 中的unicode -> python3 的str
    python2 中的str-> python3 的byteArray
'''

def pathJoin(_dir, fn, abs=False) :
    return formatPath(os.path.join(_dir, fn), abs)

def isPython3():
    '''判断python版本是否是3.x'''
    return sys.version_info >= (3,0)

def isFunc(func):
    '''判断对象是否是函数'''
    return hasattr(func,'__call__')
    # return callable(func)

def getPlatform():
    '''获取python运行平台'''
    return platform.system()

def isWindows():
    '''判断是否是win32平台'''
    return getPlatform().lower() == 'windows'

def isLinux():
    '''判断是否是linux平台'''
    return getPlatform().lower() == 'linux'

def isMac():
    '''判断是否是Mac OS平台'''
    return getPlatform().lower() == 'darwin'

def getUserPath():
    return formatPath(os.path.expanduser('~'))

def getUserName():
    return os.path.split(getUserPath())[-1]

def getDeviceName() :
    import socket
    return socket.getfqdn(socket.gethostname())

def getLocalHost() :
    '''获取设备ip
    '''
    import socket
    ip = '127.0.0.1'
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def getDesktopPath():
    '''获取桌面的路径，只支持win32、mac'''
    # if isWindows():
    #     if isPython3():
    #         import winreg           # 内置模块，获取windows注册表
    #     else:
    #         import _winreg as winreg
    #     key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    #     return winreg.QueryValueEx(key, "Desktop")[0]
    if isWindows() or isMac():
        return '%s/Desktop'%(getUserPath())
    else:
        # TODO: Linux
        return ''

def addTempPathForOs(path):
    '''添加path到系统的PATH环境变量中，暂时只支持win32'''
    if isWindows():
        os.environ['PATH']+= ';' +path

def addTempPathForPy(path):
    '''添加path到python运行环境的PATH环境变量中'''
    sys.path.append(path)

def getMainCwd():
    '''获取入口脚本的文件夹路径'''
    return os.path.split(sys.argv[0])[0]

def bytes2utf8Str(s, encodingOri='GBK') :
    if (isPython3() and not isinstance(s, str)) or (not isPython3() and not isinstance(s, unicode)) :
        try :
            s = s.decode(encodingOri)
        except Exception as e :
            s = s.decode('utf-8')
    return s.encode('utf-8').decode('utf-8')


def zipFolder(folder, zipPath = None,  exts= '.*', skipFiles = (), inZipPath='', suffixs=None):
    '''压缩文件夹
    folder:待压缩的文件夹
    zipPath:压缩文件存储路径，默认为文件绝对夹路径加上后缀'.zip'
    exts:参与压缩的文件格式后缀，默认为'.*'，表示所有文件都参与压缩，多个后缀用英文逗号（','）隔开，如：'.zip,.txt'
    skipFiles:跳过压缩的文件列表（list或tuple）,在文件夹中的绝对路径
    inZipPath:将所有文件统一放到inZipPath文件夹下
    '''
    exts = suffixs or exts
    if not isinstance(folder, str) :
        print('error:\tfolder [%s] is not a string!'%(str(folder)))
        return
    if not os.path.isabs(folder) :
        folder = os.path.join(pyDir, folder)
    folderLen = len(folder)
    fileInfos = []
    exts = (exts == '.*') and exts or str(exts).lower().split(',')

    # list解析操作
    skip = [l.replace('\\', '/').strip() for l in skipFiles]
    if os.path.exists(folder) and os.path.isdir(folder) :
        for _dir, folders, files in os.walk(folder) :
            for f in files :
                ext = os.path.splitext(f)
                ext = str(ext[-1]).lower()
                p = os.path.join(_dir, f)
                # 获取zip文件夹内的路径，去掉前面的/
                absP = p[folderLen+1:].replace('\\', '/').strip()
                if len(inZipPath) > 0 :
                    absP = pathJoin(inZipPath, absP)
                if (exts == '.*' or ext in exts) and (not absP in skip):
                    fileInfos.append((p, absP))
                    skip.append(absP)
        if len(fileInfos) > 0 :
            if zipPath is None :
                zipPath = folder + '.zip'
            dirName = os.path.dirname(zipPath)
            if not os.path.exists(dirName) :
                os.makedirs(dirName)
            zipF = zipfile.ZipFile(zipPath, 'w', zipfile.ZIP_DEFLATED)
            # print(password)
            # zipF.setpassword(password)
            for f, af in fileInfos :
                zipF.write(f, af)
            zipF.close()
            print('zip [%s] finished! Total files: %d'%(zipPath, len(fileInfos)))
            return fileInfos
        else :
            print('no files need to zip!')

    else :
        print('error:\tfolder [%s] do not exists!'%(folder))

def tryMakeParentDir(path) :
    '''尝试将传入的地址的父目录创建出来'''
    d = os.path.dirname(path)
    if not os.path.isdir(d) :
        os.makedirs(d)

def tryMakeDir(path) :
    '''尝试将传入的目录创建出来'''
    if not os.path.isdir(path) :
        if not os.path.isfile(path) :
            os.makedirs(path)
        else :
            raise Exception('path "%s" has a file or folder'%path)

def copyTree(srcDir, targetDir, removeBefore=False, exts='.*', skipDirs=(), suffix=None) :
    '''Copy the srcDir to targetDir.
    参数: srcDir, targetDir, removeBeforee=False, exts='.*', skipDirs=()
    skipDirs 使用相对于srcDir的路径
    '''
    # 版本兼容
    exts = suffix or exts
    try :
        import win32api
        import win32con
    except Exception as e :
        win32api = None

    if not os.path.exists(srcDir):
        print('dir ["%s"] do not exists!'%(srcDir))
        return False
    srcDir = formatPath(srcDir)
    targetDir = formatPath(targetDir)
    if removeBefore and os.path.isdir(targetDir):
        # shutil.rmtree(targetDir)
        removeTree(targetDir)

    # 如果是文件，拷贝
    if os.path.isfile(srcDir) :
        # print('copyTree 1 ')
        suf = os.path.splitext(srcDir)[1]
        if not targetDir[-len(suf):] == suf :
            # 目标位置是路径
            targetDir = pathJoin(targetDir, os.path.split(srcDir)[-1])
            # print('copyTree 2 '+targetDir)
        # print('copyTree 3 ')
        dirname = os.path.dirname(targetDir)
        if not os.path.isdir(dirname) :
            os.makedirs(dirname)
        shutil.copyfile(srcDir, targetDir)
        return True

    # print('copy ["%s"] to ["%s"] ...'%(srcDir, targetDir))
    if exts != '.*' and isinstance(exts, str) :
            exts = [f.strip().lower() for f in exts.split(',')]
    elif isinstance(exts, list) or isinstance(exts, tuple) :
        exts = [s.lower() for s in exts]

    for curDir, folders, files in os.walk(srcDir) :
        # 跳过skipDirs定义的文件夹
        # print('relative dir:'+getRelativePath(curDir, srcDir)[0])
        relativeDir = getRelativePath(curDir, srcDir)[0].strip()
        for sd in skipDirs :
            if formatPath(relativeDir).find(sd) == 0:
                relativeDir = None
                break
        if relativeDir == None :
            continue

        for f in files :
            if exts == '.*' or str(os.path.splitext(f)[-1]).strip().lower() in exts:
                p = pathJoin(curDir, f)
                tp = pathJoin(targetDir, p.replace(srcDir, '')[1:])
                td = os.path.split(tp)[0]
                if not os.path.exists(td) :
                    # print('make '+td)
                    os.makedirs(td)
                if isWindows() and os.path.exists(tp) and win32api is not None :
                    # win32上只能通过下面的方式修改文件显隐性，隐藏文件覆盖会引发权限问题
                    win32api.SetFileAttributes(tp, win32con.FILE_ATTRIBUTE_NORMAL)
                shutil.copyfile(p, tp)
    # print('copy ["%s"] to ["%s"] \tsucceeded!'%(srcDir, targetDir))
    return True

def removeTree(path) :
    if os.path.isdir(path):
        # shutil.rmtree(path)
        if isWindows() :
            tryCmd('rd /s /q "%s"'%(path.replace('/', '\\')))
        else :
            tryCmd('rm -rf "%s"'%(path))
    elif os.path.isfile(path) :
        removeFile(path)

def removeFile(path, safe=True) :
    '''删除文件
    path：       文件路径
    safe=True:   安全删除，使用的文件不删除
    返回值: 1：成功          2：没有该文件          Exeption: 安全删除失败
    '''
    if os.path.isfile(path) :
        if safe :
            try :
                os.unlink(path)
            except Exception as e :
                return e
        else :
            os.remove(path)
        return 1
    return 0

def renameFile(ori, tar) :
    if os.path.isfile(ori) and ori != tar :
        d = os.path.dirname(tar)
        if not os.path.isdir(d) :
            os.makedirs(d)
        os.raname(ori, tar)
        return True
    return False

def removeMacConfFiles( tar ) :
    '''删除Mac文件系统的配置文件(夹)，如：.DS_Store、__MACOSX'''
    if os.path.isdir(tar) :
        d = os.path.basename(tar)
        if d in ('__MACOSX',) :
            removeTree(d)
        else :
            for f in os.listdir(tar) :
                removeMacConfFiles(pathJoin(tar, f))
    elif os.path.isfile(tar) :
        f = os.path.basename(tar)
        if f in ('.DS_Store', ) :
            removeFile(tar)

def openFile(path, mode, encoding='utf-8') :
    '''以指定格式打开文件，返回文件'''
    import codecs
    return codecs.open(path, mode, encoding=encoding)

def startFile(path) :
    '''图形系统打开文件或文件夹，目前仅测支持win32和mac
    return ： 如果成功打开文件返回True， 否则返回False
    '''
    if os.path.exists(path) :
        if isWindows() :
            os.startfile(path)
            return True
        elif isMac():
            # path = path.replace(' ', '" "')
            os.system('open "%s"'%(path,))
            return True
    return False

def selectInFolder( path ) :
    '''打开path父目录，如果是win32选中path指向的文件（夹）
    return ： 如果成功打开文件返回True， 否则返回False
    '''
    if os.path.exists(path) :
        p = path
        if isWindows() :
            os.system('explorer.exe /select, "%s"'%path.replace('/', '\\'))
        else :
            startFile(os.path.dirname(path))
        return True

    return False

def getCounter(start = 1) :
    '''Get a counter, start is the value returned when first call the counter ,start is 0 if did not set
    '''
    c = [start-1]

    def count() :
        c[0] += 1
        return c[0]

    return count

def formatPath(path, abs=False) :
    path = str(path)
    if abs or os.path.exists(path) :
        path = os.path.abspath(path)
    return path.replace('\\', '/')

def getRelativePath(oriPath, relative2) :
    '''return path, success
    path:       the path that oriPath relative to relative2 ,if oriPath do not satrt with relative2,return oriPath
    success:    if oriPath satrt with relative2
    '''
    oriPath = formatPath(oriPath)
    relative2 = formatPath(relative2)
    if oriPath.find(relative2) == 0 :
        return oriPath.replace(relative2, '').strip('/'), True
        # TODO:测试一下sub的方法，正常就用sub
        # return oriPath.sub(len(relative2)).strip('/'), True
    else :
        return oriPath, False

def modifyFile(path, oldStrs, newStrs) :
    '''modifyFile(path, oldStrs, newStrs)   通过replace修改文件内容，不会有多余的换行符生成
    oldStrs 文件中需要替换的字符串tuple或者list
    newStrs 文件中替换为的字符串tuple或者list，与oldStrs一一对应
    '''
    if os.path.isfile(path) :
        f = open(path, 'rb')
        content = bytes2utf8Str(f.read())
        content = content.replace('\r\n', '\n')
        f.close()
        if newStrs and oldStrs and len(newStrs) == len(oldStrs) :
            for i in range(len(newStrs)) :
                content = content.replace(oldStrs[i], newStrs[i])
        f = None
        if isPython3() :
            f = open(path, 'w', encoding='utf-8')
        else :
            f = open(path, 'w')
        f.write(content)
        f.close()

def tryCmd(cmd) :
    import subprocess
    import traceback
    import tempfile
    import locale

    # cmd = cmd.encode(locale.getpreferredencoding())
    # if isPython3() :
    #     cmd = cmd.decode(locale.getpreferredencoding())
    out_temp = None
    lines = []
    encoding = locale.getpreferredencoding()

    try:
        out_temp = tempfile.SpooledTemporaryFile()
        fileno = out_temp.fileno()

        obj = subprocess.Popen(cmd, stdout=fileno, stderr=fileno, shell=True)
        obj.wait()
        out_temp.seek(0)
        lines = out_temp.readlines()
        # print (lines)
    except Exception as e:
        print (traceback.format_exc())
        # raise e
        # pass
    finally:
        if out_temp:
            out_temp.close()
        return [l.decode(encoding) for l in lines]

def tryCmdAsync(cmd, callback=None, onCompeleted=None, **args) :
    '''尝试异步运行命令
    params:
        callback:           每输出一行的回调，参数(lineStr, PopenObj)，默认None
        onCompeleted:       线程退出回调，命令执行完成，默认None
        **args:             不定参数，包含key：sleep(time.sleep时间，单位秒, 默认0.0001)  notDaemon(不是守护线程，默认False)  encoding(编码，默认计算机默认编码)
    '''
    import threading
    import subprocess
    import traceback
    import time
    # 获取系统编码
    import locale

    sleep = args.get('sleep') or 0.0001
    notDaemon = args.get('notDaemon') or False
    shell = args.get('shell') or True
    def func() :
        try:
            # encoding = args.get('encoding') or locale.getpreferredencoding()
            # obj = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=shell, encoding=encoding)
            obj = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=shell)
            count = 0
            while True :
                buff = obj.stdout.readline().splitlines()
                if obj.poll() is not None and len(buff) == 0  :
                    if onCompeleted :
                        onCompeleted()
                    break
                elif callback :
                    callback('\n'.join(buff), obj)

                time.sleep(sleep)
        except Exception as e:
            print (u'Exception:', traceback.format_exc())
            raise e
        finally:
            if out_temp:
                out_temp.close()

    t = threading.Thread(target=func)
    t.setDaemon(not notDaemon)
    t.start()

def getPythonObjByStr(pythonStr) :
    '''将传入的字符串转化为python对象（函数、值等），
    返回值是一个作用域，可使用 getPythonObjByStr('xxxxx')['yy']访问'''
    scope = {}
    exec_code = compile(funcStr, '<string>', 'exec')
    exec(exec_code, scope)
    return scope

def getFuncByStr(funcStr, funcName) :
    '''根据传入的字符串和方法名获取定义的函数'''
    scope = {}
    exec_code = compile(funcStr, '<string>', 'exec')
    exec(exec_code, scope)
    return scope[funcName]

def jsonLoads(jsonStr, **params) :
    '''py2 py3 json.loads'''
    import json
    return json.loads(jsonStr, **params)

def jsonDumps(data, **params) :
    '''py2 py3 json.dumps
    可用参数及默认值：
        skipkeys=False,
        ensure_ascii=True,
        check_circular=True,
        allow_nan=True,
        cls=None,
        indent=None,
        separators=None,
        encoding="utf-8",
        default=None,
        sort_keys=False
    '''
    import json
    if isPython3() and 'encoding' in list(params.keys()) :
        del params['encoding']
    return json.dumps(data, **params)


def CamelCase2UnderLine(s):
    '''驼峰法命名转下划线命名'''
    newStr = ''
    for i in range(len(s)):
        c = s[i]
        v = ord(c)
        if v > 64 and v < 91 :
            if i > 0 and i < len(s) - 1 :
                preV = ord(s[i-1])
                if preV > 96 and preV < 123 :
                    newStr = newStr + '_'
                else :
                    nextV = ord(s[i+1])
                    if nextV > 96 and nextV < 123 and preV != 95:
                        newStr = newStr + '_'
            newStr = newStr + chr(v+32)
        else :
            newStr = newStr + c
    # print(newStr)
    return newStr

def UnderLine2CamelCase(s):
    '''下划线命名转驼峰法命名'''
    newStr = ''
    arr = s.split('_')
    while arr[0] == '' and len(arr) > 0 :
        arr.pop(0)
    if len(arr) > 1 :
        for i in range(1, len(arr)) :
            a = arr[i]
            if len(a) > 0 :
                arr[i] = a[0].upper() + a[1:]
    return ''.join(arr)

def isStr(s) :
    if isPython3() :
        return isinstance(s, str)
    else :
        return isinstance(s, str) or isinstance(s, unicode)

def equals(a, b) :
    if isPython3() :
        import operator
        return operator.eq(a, b)
    else :
        return cmp(a, b) == 0

def tryGetDictValue(dic, key, default=None, delete=False) :
    '''从dict中获取key对应的value,
default: 若不存在key则返回传入的默认值,默认 None
delete:  是否在获取到值后删除对应键值对,默认 False
    '''
    if isinstance(dic, dict) :
        if delete :
            return dic.pop(key, default)
        else :
            ret = dic.get(key)
            if ret != None :
                return ret
            else :
                return default
    else :
        return default

def getFileMd5(filename):
    import hashlib
    if not os.path.isfile(filename):
        return
    myhash = hashlib.md5()# create a md5 object
    with open(filename,'rb') as f :
        while True:
            b = f.read(8096)# get file content.
            if not b :
                break
            myhash.update(b)#encrypt the file
    return myhash.hexdigest()

def hasChineseChar(string) :
    import re
    if re.search('[\u4e00-\u9fa5]', string) :
        return True
    return False

def hasSpaceChar(string) :
    import re
    if re.search(r'\s', string) :
        return True
    return False

def pyData2LuaLines( data, key=None, deepth=0, indent='    ', lines=None, clearNil=True, strMarks='\'', idx=None, listPerLine=None ) :
    '''将python基本类型数据转换为lua格式
    data, key=None, deepth=0, indent='    ', lines=None, clearNil=True, strMarks='\'', idx=None, listPerLine=None
    data:python数据
    key:生成的第一行为 local key = {
    listPerLine:如果是纯list或tuple，设置多少个数据为一行。默认None，不换行
    clearNil:清空为nil的字段
    indent:缩进字符串
    '''
    import re
    pattern = re.compile(r'^[a-zA-Z_][a-zA-Z_\d]*')

    if lines is None :
        lines = []
    _indent = indent * deepth
    line = _indent

    def append( l, i=None ) :
        '''去除多余的空行'''
        if i is None :
            # 添加一行
            if len(l.strip()) > 0 :
                lines.append(l)
        else :
            if len(l.strip()) > 0 :
                if i == 0 or (isinstance(listPerLine, int) and i%listPerLine == 0) :
                    lines.append(l)
                else :
                    lines[-1] += ' %s'%(l.strip(), )

    if key is not None :
        if isinstance(key, int) or isinstance(key, float) :
            if key == int(key) :
                key = int(key)
            line = '%s[%s] = '%(_indent, key)
        else :
            # print(pattern.search(key), key)
            if pattern.search(key) :
                line = '%s%s = '%(_indent, str(key).strip())
            else :
                line = '%s[%s%s%s] = '%(_indent, strMarks, str(key).strip(), strMarks)

    if isinstance(data, dict) :
        append(line)
        append('%s{'%(_indent))
        for k,v in list(data.items()) :
            pyData2LuaLines(v, k, deepth+1, indent, lines, clearNil, strMarks, None, listPerLine)
        append('%s},'%(_indent))

    elif isinstance(data, list) or isinstance(data, tuple) :
        append(line)
        append('%s{'%(_indent))
        for idx in range(len(data)) :
            v = data[idx]
            pyData2LuaLines(v, None, deepth+1, indent, lines, clearNil, strMarks, idx, listPerLine)
        append('%s},'%(_indent))

    elif type(data) == bool :
        line = '%s%s,'%(line, str(data).lower())
        append(line, idx)

    elif isinstance(data, str) :
        line = '%s%s%s%s,'%(line, strMarks, data, strMarks)
        append(line, idx)

    elif data is None :
        if not clearNil :
            line = '%s\'nil\','%(line,)
            append(line, idx)

    else :
        line = '%s%s,'%(line, str(data))
        append(line, idx)

    return lines

def delAllEmptySubFolders( path ) :
    '''删除指定路径下所有空文件夹'''
    if os.path.isdir(path) :
        for d, fds, fls in os.walk(path) :
            if len(fds) == 0 and len(fls) == 0 :
                delEmptyFoler(d)

def delEmptyFoler( path ) :
    '''如果传入文件夹为空则删除'''
    if os.path.isdir(path) :
        if len(os.listdir(path)) == 0 :
            removeTree(path)
            delEmptyFoler(os.path.dirname(path))

# ============================================线程相关===============================================================
# 见https://ituser.cn/python3-threading%E4%B9%8B%E7%BB%88%E6%AD%A2%E7%BA%BF%E7%A8%8B%E6%96%B9%E6%B3%95/
def __async_raise( tid, exctype ) :
    import threading
    import time
    import inspect
    import ctypes

    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def stopThread( thread ) :
    '''停止一个线程'''
    __async_raise(thread.ident, SystemExit)

# =============================================== 动态加载py模块 ============================================================
def execStr( s, raiseException=False ) :
    '''执行从字符串定义的python代码, 返回locals环境，示例：
    help(execStr('from DKVTools.Funcs import pyData2LuaLines as test')['test'])
    help(execStr('from DKVTools.Funcs import pyData2LuaLines')['pyData2LuaLines'])
    '''
    loc = locals()
    try :
        exec(s)
    except Exception as e:
        if raiseException :
            raise e
        else :
            print(e)
    return loc
# =============================================== 动态加载py模块 ============================================================

# ===========================================================================================================

def Singleton(cls, *args, **kwds):
    '''单例修饰符函数，参考见：
    python 单例：http://ghostfromheaven.iteye.com/blog/1562618
    python @修饰符：http://blog.csdn.net/lainegates/article/details/8166764
    '''
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kwds)
        return instances[cls]
    return _singleton

# ===========================================================================================================


# ==================================================测试========================================================
def __main() :
    # startFile(os.path.dirname(__file__))
    # startFile(getDesktopPath())
    # print(getLocalHost())
    # for s in ('as_dfg__h', '__as__b_df') :
    #     print(UnderLine2CamelCase(s), s)
    # selectInFolder(r"F:/cocos2dx/cocostudio/Docs/Cocos/CocosProjects/G003_en_PLAZA/cocosstudio/Scene.udf")
    help(execStr('from DKVTools.Funcs import pyData2LuaLines')['pyData2LuaLines'])



if __name__ == '__main__':
    __main()