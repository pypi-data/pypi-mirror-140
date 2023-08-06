 # -*- coding: utf-8 -*-
from pwn import *
	
ALL_NUMBERS = [str(number).zfill(4) for number in range(10000)]
START=['7426', '1375', '9825', '1206']

def info():
	info={
"questname":"QGame_Pro_revenge",
"platform":"ctfshow",
"contest" : "jwb(juan wang bei)",
"description":"jwb misc.",
"requirements":"python pwntools.",
"module options":[
	{"name":"port","required":True,"description":"the port of pwn.challenge.ctf.show."},
	]
}
	return(info)

def is_fit(number_str,guess_str,xAxB):
	"""
	用于分析当前列表中的一个数字与上一个猜测的数字是否符合xAxB的格式
	"""
	_A=0
	_B=0
	_ban1 =[0,1,2,3]
	_ban2 = [0,1,2,3]
	for i in range(4):
		if(guess_str[i] == number_str[i]):
			_A += 1
			_ban1.remove(i)
			_ban2.remove(i)
	for i in _ban1:
		for j in _ban2:
			if(guess_str[i] == number_str[j]):
				_B += 1
				_ban2.remove(j)
				break
	return (f'{_A}A{_B}B'==xAxB)


def trim_numbers(current_list,guess_str,xAxB):
	"""
	用于根据当前可能列表和上次猜测的字符串及结果生成可能的字符串列表
	"""
	_tmp_list=[]
	for number_str in current_list:
		if is_fit(number_str,guess_str,xAxB):
			_tmp_list.append(number_str)
	return(_tmp_list)


def solve(port):
	sh=remote("pwn.challenge.ctf.show",port)
	r=sh.recvline().decode()
	r=sh.recvline().decode()	
	while True:
		r=sh.recvline().decode()
		if "flag" in r:
			print(r,end="")
			r=sh.recvall().decode()
			return(r)
		print(r,end="")
		_current_list=ALL_NUMBERS[:]
		for _round in range(9):
			if _round<len(START):
				sh.sendline(START[_round])
				_last_try=START[_round]
			else:
				sh.sendline(_next_for_try)
				_last_try=_next_for_try
			r=sh.recvline().decode()
			if "perfect" in r:
				break
			xAxB=r.split(' ')[0]
			_current_list=trim_numbers(_current_list,_last_try,xAxB)
			_next_for_try=_current_list[0]



def exploit(options):
	port=options["port"]
	while True:
		try:
			flag=solve(port)
			print(flag)
			return("本题算做签到题谁敢有意见！！！！")
		except:
			print("Once More!!!!!")
			print("*"*100)


def make_wp():
	wp=f"""
这是一个抑智小游戏，叫“Bulls and Cows”,规则可以从百度百科里找，解法也可以。

这里提供的解法是先生成0000-9999的数字列表，然后进行固定尝试，根据尝试得到的结果对列表进行删减，并从列表中查找相关元素。

但是套神母体提供的算法有点谜，我也不知道写对了没有，达不到100%的成功率，但是总算也能做得出来，懒得调试了，都说是简单签到题了你还想怎样。
	"""
	return(wp)



