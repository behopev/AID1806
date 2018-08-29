#!/usr/bin/env python3    # 声明编译器位置
#coding = utf-8   # 声明编码类型

'''
name: behope
date: 2018-8-27
email: secret
modules: python3.5 mysql pymysql
This is a dict project for AID
'''

from socket import * 
import pymysql 
# from multiprocessing import Process
import os,sys
import time
import signal

HOST = '0.0.0.0'
PORT = 8888
ADDR = (HOST,PORT)

# class Handle_client(object):
#     def __init__(self,connfd,addr,db,cursor):
#         self.connfd = connfd
#         self.addr = addr
#         self.db = db
#         self.cursor = cursor

def handle_client_info(connfd,db):
    while True: # 子进程循环收发信息, 接收客户端的信息,判断进行什么处理
        client_info = connfd.recv(1024).decode()
        data = client_info.split(' ')
        if client_info == 'login':
            print('收到',connfd.getpeername(),'登录请求')
            do_login(connfd,db)
        elif client_info == 'register':
            print('收到',connfd.getpeername(),'注册请求')
            do_register(connfd,db)
        elif client_info == 'query':
            print('收到',connfd.getpeername(),'查询请求')
            do_query(connfd,db)
        elif client_info == 'history':
            print('收到',connfd.getpeername(),'历史请求')
            do_history(connfd,db)
        elif (not client_info) or client_info == 'quit':            
            print(connfd.getpeername(),'断开连接')
            connfd.close()
            sys.exit()


def do_login(connfd,db):
    connfd.send(b'ok')
    user_info = connfd.recv(1024).decode().split(' ')
    user_name = user_info[0]
    user_password = user_info[1]
    usertuple_sql = 'select * from user where name="%s" and password="%s"'%(user_name,user_password)  # 查询数据库是否存在
    cursor = db.cursor()
    cursor.execute(usertuple_sql)
    usertuple = cursor.fetchone()
    # print(usertuple)
    if (usertuple[1] == user_name) and (usertuple[2] == user_password):
        connfd.send(b'ok')
    else:
        connfd.send(b'fail')


def do_register(connfd,db):
    connfd.send(b'ok')
    user_info = connfd.recv(1024).decode().split(' ')  # 接收用户信息分割成列表
    user_name = user_info[0]
    user_password = user_info[1]
    cursor = db.cursor()
    usertuple_sql = 'select name,password from user'  # 查询数据库是否存在
    cursor.execute(usertuple_sql)
    usertuple = cursor.fetchone()
    if usertuple != None:
        connfd.send(b'fail')
        return
    else:
        insert_sql = 'insert into user(name,password) values ("%s","%s")' % (user_name,user_password)
        cursor.execute(insert_sql)
        db.commit()
        connfd.send(b'ok')

    # 老师版
    # usertuple_sql = 'select * from user where name="%s"' % user_name # 查询数据库是否存在
    # cursor.execute(usertuple_sql)
    # r = fetchone()
    # if r != None:
    #     connfd.send(b'fail')
    #     return
    # insert_sql = 'insert into user(name,password) values ("%s","%s")' % (user_name,user_password)
    # try:
    #     cursor.execute(insert_sql)
    #     db.commit()
    #     connfd.send(b'ok')
    # except:
    #     db.rollback()
    #     connfd.send(b'fail')
    #     return
    # else:
    #     print('%s注册成功' % user_name)


def do_query(connfd,db):

    def insert_history():
        tm = time.ctime()
        insert_history_sql = "insert into history(name,word,time) values ('%s','%s','%s')" % (query_word[0],query_word[1],tm)
        try:
            cursor.execute(insert_history_sql)
            db.commit()
        except:
            db.rollback()

    # 查询单词
    connfd.send(b'ok')
    query_word = connfd.recv(1024).decode()
    # print(query_word)
    query_word = query_word.split(' ')
    # print(query_word)
    cursor = db.cursor()
    query_sql = "select interpret from words where word='%s'" % query_word[1]
    # print(query_sql)
    cursor.execute(query_sql)
    db.commit()
    interpret = cursor.fetchone()[0]
    # print(interpret)
    if interpret == None:
        connfd.send(b'fail')
    # print(interpret)
    else:
        connfd.send(interpret.encode())
        # 插入历史记录
        insert_history()


def do_history(connfd,db):
    connfd.send(b'ok')
    name = connfd.recv(1024).decode()
    # print(name)
    cursor = db.cursor()
    try:
        history_sql = "select * from history where name='%s' order by time desc limit 10" % name
        cursor.execute(history_sql)
        db.commit()
        history_tuple = cursor.fetchall()
        # print(history_tuple)
        if not history_tuple:
            connfd.send(b'fail')
        else:
            connfd.send(b'ok')
            for i in history_tuple:
                time.sleep(0.1)
                msg = "用户:%s 单词:%s 时间:%s" % (i[1],i[2],i[3])
                connfd.send(msg.encode())
            time.sleep(0.1)
            connfd.send(b"##")
    except:
        connfd.send(b'fail')
        return


# 主控制流程,父子进程,子进程处理客户端请求,父进程接收新的连接
def main():
    # 连接数据库
    db = pymysql.connect(host='localhost',
                        port=3306,
                        user='root',
                        password='123456',
                        database='dict_db')
    # 创建游标
    cursor = db.cursor()
    # 创建流式套接字 等待连接
    sockfd = socket()
    sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    sockfd.bind(ADDR)
    sockfd.listen(5)

    signal.signal(signal.SIGCHLD,signal.SIG_IGN)  # 忽略子进程退出信号
    
    while True:  # 父进程循环接收新的连接
        try:
            print('等待连接...')
            connfd, addr = sockfd.accept()  # 连接上,创建收发套接字
        except KeyboardInterrupt:  # 如果是键入异常,关闭套接字退出服务器
            sockfd.close()
            sys.exit('服务器退出')
        except Exception as e:  # 其他异常就打印异常原因,继续监听
            print(e)
            continue
        # 有连接后, 创建子进程处理客户端信息
        pid = os.fork()
        if pid == 0:  # 子进程创建成功
            print(connfd.getpeername(),'已连接')
            sockfd.close()  # 子进程不用连接,关闭子进程的监听套接字
            # dictionary = Handle_client(connfd,addr,db,cursor)  # 子进程处理收到客户端的信息
            handle_client_info(connfd,db)  # 子进程处理收到客户端的信息
        else:
            connfd.close()  # 父进程不需要收发,关闭收发套接字
            continue  # 父进程继续监听连接

    sockfd.close()
    cursor.close()
    db.close()

if __name__ == '__main__':
    main()
