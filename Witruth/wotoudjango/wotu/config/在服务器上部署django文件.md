## 服务器数据库配置

### 1、安装mysql

ubuntu上安装[**MySQL**](http://lib.csdn.net/base/mysql)非常简单只需要几条命令就可以完成。

1. **sudo apt-get install mysql-server**

   中间会提示为root用户设置密码，这里设置为admin

2. **apt-get isntall mysql-client**

3. **sudo apt-get install libmysqlclient-dev**

安装完成之后可以使用如下命令来检查是否安装成功：

**sudo netstat -tap | grep mysql**

通过上述命令检查之后，如果看到有mysql 的socket处于 listen 状态则表示安装成功。

登陆mysql数据库可以通过如下命令：

**mysql -u root -p **

启动mysql服务器

**sudo /etc/init.d/mysql start**

### 2、外网链接服务器mysql

修改配置文件的bind-address：

**sudo vi /etc/mysql/mysql.conf.d/mysqld.cnf**

将bind-address=127.0.0.1 一行注释

同时，给所有的ip用户可以使用root用户名，admin密码登录mysql的权限，首先进入mysql交互模式**mysql -u root -p **输入admin登录，随后输入：

**GRANT ALL PRIVILEGES ON *.* TO ‘root’@’%′ IDENTIFIED BY ‘admin’ WITH GRANT OPTION;**

现在外网就可以访问了。

### 3、安装mongodb

（1）sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6

（2）根据不同ubuntu版本

Ubuntu 12.04

echo "deb [ arch=amd64 ] http://repo.mongodb.org/apt/ubuntu precise/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list

Ubuntu 14.04

echo "deb [ arch=amd64 ] http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list

Ubuntu 16.04

echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list

（3）sudo apt-get update

（4）sudo apt-get install -y mongodb-org

启动monogdb：

**sudo service mongod start**

### 4、外网链接服务器mongodb

修改mongodb的配置文件

**sudo vi /etc/mongod.conf**

将bindIp修改为0.0.0.0





## 依赖库

1 Django ： pip install django

2 mysql库pymysql： pip install pymysql

3 html解析哭beautifulsoup：pip install beautifulsoup

4 自动化测试库 ： sudo pip install selenium

5 sudo pip install chardet

6 关键句提取库textrank：sudo pip install textrank4zh

会安装依赖库：jieba 、 numpy 、networkx、decorator等

7 mongodb链接库pymongo: sudo pip install pymongo

8 科学计算库pandas :sudo pip --no-cache-dir install pandas

9 机器学习库sklearn: sudo pip --no-cache-dir install sklearn

10 scipy库 ： sudo pip --no-cache-dir install scipy

11 lda库：sudo pip --no-cache-dir install lda

 12 gensim库 ： sudo pip --no-cache-dir install gensim

13 写excel库 ： sudo pip --no-cache-dir install xlwt





## 在服务器上部署django文件

### 1、linux上安装nginx

**sudo apt-get install nginx**

一些nginx的操作：

fnngj@ubuntu:~$/etc/init.d/nginx start  #启动

fnngj@ubuntu:~$/etc/init.d/nginx stop  #关闭

fnngj@ubuntu:~$ /etc/init.d/nginxrestart  #重启

### 2、安装 uwsgi

**sudo pip install uwsgi**

### 3、创建uwsgi配置文件

在项目根路径下创建一个ini文件，命名为myweb_uwsgi.ini

文件内容：

```
# myweb_uwsgi.ini file
[uwsgi]

# Django-related settings

socket = :8000

# the base directory (full path)
chdir      = /home/yuanyuan/wotoudjango

# Django s wsgi file
module     = first.wsgi

# process-related settings
# master
master     = true

# maximum number of worker processes
processes    = 2

# ... with appropriate permissions - may be needed
# chmod-socket  = 664
# clear environment on exit
vacuum     = true
```

socket  指定项目执行的端口号。chdir   指定项目在服务器的路径的目录。

### 4、修改django配置

要允许使用外网访问，settings.py文件中allow_host修改

**ALLOWED_HOSTS = ['\*']**

### 5、项目从本地传入到服务器

从我的电脑传入服务器命令为：

**sudo scp -r wotoudjango **[**yuanyuan@106.75.65.56:/home/yuanyuan/**](mailto:yuanyuan@106.75.65.56:/home/yuanyuan/)

### 6、配置nginx的参数

**sudo vi /etc/nginx/nginx.conf**

在http中加入如下的内容

![图片 1](/Users/shixiaowen/Downloads/图片 1.png)

几个重要的地方，listen后面指定端口号，server_name指定用什么访问，

uwsgi_read_timeout指的是超时限制，最好设大一些，因为爬虫计算较慢。最后一行，alias指定css、js这些文件的路径，否则无法正常显示css样式以及js样式，

### 7、执行下面的命令

**export PYTHONPATH=$PYTHONPATH:/home/yuanyuan/wotoudjango/wotu/:/home/yuanyuan/wotoudjango/wotu/spiders/shengwugu_crawl/**

### 8、启动

**uwsgi--ini myweb_uwsgi.ini** 

### 9、访问

[http://106.75.65.56:80/home](http://106.75.65.56:80/home)



参考链接：

http://www.cnblogs.com/fnng/p/5268633.html









































































