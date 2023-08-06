 # -*- coding: utf-8 -*-
def info():
	info={
"questname":"Quest Of Image",
"platform":"ctfshow",
"contest" : "jwb(juan wang bei)",
"description":"jwb misc.",
"requirements":"python qoi,PIL.",
"module options":[
	{"name":"filename","required":True,"description":"the full path (or relative path) of png file."},
	]
}
	return(info)

def exploit(options):
	filepath=options["filename"]
	import qoi, os
	from PIL import Image
	f = open(filepath, 'rb').read()
	key = (0x89504e47 ^ 0x716f6966).to_bytes(4, 'big')
	file = b''.join([(f[i] ^ key[i % 4]).to_bytes(1, 'big') for i in range(len(f))])
	file = file[:8] + int(350).to_bytes(4, 'big') + file[12:]
	open('./1.tmp', 'wb').write(file)
	img = Image.fromarray(qoi.read('./1.tmp')).crop((0, 300, 900, 350))
	os.remove('./1.tmp')
	img.save('flag.png')
	return("your flag is in flag.png!!!")


def make_wp():
	wp=f"""
略。
	"""
	return(wp)