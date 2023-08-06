 # -*- coding: utf-8 -*-
def info():
	info={
"questname":"zipper,clipper,not...",
"platform":"ctfshow",
"contest" : "cjb(chi ji bei)",
"description":"cjb misc.",
"requirements":"python base58,zipfile.",
"module options":[
	{"name":"filename","required":True,"description":"the full path (or relative path) of zip file."},
	]
}
	return(info)

def exploit(options):
	filepath=options["filename"]
	import base58, zipfile
	z = zipfile.ZipFile(filepath)
	t = [''] * 1000
	for i in z.namelist():
		tmp = i.split('/')
		if tmp[-1] != '':
			t[int(tmp[-1])] = tmp[-2]
	t = base58.b58decode(''.join(t).encode()).decode()
	print('ctfshow{' + t.split('{')[1].split('}')[0] + '}')
	return ("做完了，套神称之为烂题。")

def make_wp():
	wp=f"""
根据积累和特征，得到flag。
	"""
	return(wp)