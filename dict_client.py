from socket import * 
import pymysql 
from multiprocessing import Process
import os,sys,getpass


def do_login(sockfd):
    user_name = input('请输入注册用户名:')
    user_password = getpass.getpass('请输入密码:')
    user_info = '%s %s'%(user_name,user_password)
    sockfd.send(user_info.encode())  # 把用户信息发给服务器判断是否存在
    confirm_info = sockfd.recv(1024).decode()
    if confirm_info == 'ok':
        return user_name
    elif confirm_info == 'fail':
        input('登录失败请重新登录或注册,请按回车返回')
        return 1

def login(sockfd,user_name):
    print('欢迎 %s 登录成功' % user_name)
    while True:
        print('\n=========================')
        print('1. 查询')
        print('2. 历史记录')
        print('0. 注销')
        print('=========================')
        second_choice = input('请输入选项:')
        if second_choice == '1':
            sockfd.send(b'query')
            data = sockfd.recv(1024).decode()
            if data == 'ok':
                do_query(sockfd,user_name)
        elif second_choice == '2':
            sockfd.send(b'history')
            data = sockfd.recv(1024).decode()
            if data == 'ok':
                do_history(sockfd,user_name)
        elif second_choice == '0':
            return
        else:
            input('输入错误,请按回车返回')
            return 1


def do_register(sockfd):
    while True:
        user_name = input('请输入注册用户名:')
        user_password = getpass.getpass('请输入密码:')
        user_password1 = getpass.getpass('请重复输入密码:')
        if(' 'in user_name) or (' 'in user_password):
            print('用户名密码不允许空格')
            continue
        if user_password != user_password1:
            print('两次密码不一致')
            continue
        user_info = '%s %s'%(user_name,user_password)
        sockfd.send(user_info.encode())
        confirm_info = sockfd.recv(1024).decode()
        if confirm_info == 'ok':
            input('注册成功,请按回车返回')
            return 0
        elif confirm_info == 'fail':
            input('用户名已存在,注册失败,按回车返回')
            return 1


def do_query(sockfd,user_name):
    word = input('请输入要查询的单词:')
    word_info = '%s %s' % (user_name,word)
    sockfd.send(word_info.encode())
    interpret = sockfd.recv(2048).decode()
    if interpret == 'fail':
        print('没有这个单词')
    else:
        print('单词解释:',interpret)
        input('按回车返回')


def do_history(sockfd,user_name):
    sockfd.send(user_name.encode())
    data = sockfd.recv(1024).decode()
    if data == 'ok':
        while True:
            history_info =  sockfd.recv(1024).decode()
            if history_info == '##':
                break
            print(history_info)
    else:
        print('没有历史记录')


def main():
    if len(sys.argv)<3:
        print('连接地址输入错误')
        return

    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    ADDR = (HOST,PORT)

    sockfd = socket()
    sockfd.connect(ADDR)

    while True:
        print('\n=========================')
        print('欢迎使用电子词典')
        print('1. 登录')
        print('2. 注册')
        print('0. 退出')
        print('=========================')
        choice = input('请输入选项:')
        # try:  
        #     choice = input('请输入选项:')
        # except Exception:
        #     print('命令输入错误')
        #     continue
        # if choice not in ['1','2','3']:
        #     print('选项输入错误')
        #     sys.stdin.flush() # 清除输入
        #     continue

        if choice in ('1','登录'):
            sockfd.send(b'login')
            data = sockfd.recv(1024).decode()
            if data == 'ok':
                name = do_login(sockfd)
                if name != 1:
                    login(sockfd,name)
        elif choice in ('2','注册'):
            sockfd.send(b'register')
            data = sockfd.recv(1024).decode()
            if data == 'ok':
                do_register(sockfd)
        elif choice in ('0','退出'):
            sockfd.send(b'quit')
            sockfd.close()
            sys.exit('再见')
        else:
            input('输入错误,请按回车返回')


if __name__ == '__main__':
    main()