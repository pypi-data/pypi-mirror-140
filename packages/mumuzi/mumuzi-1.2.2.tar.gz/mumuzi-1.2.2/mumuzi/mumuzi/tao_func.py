import binascii
import random
import os
from . import LSB
import time
import base64
from PIL import Image
import zipfile


def enc_to_txt_file(input_file,output_file,method):
	print("enc_to_txt_file",input_file,output_file,method)
	#output_file_type=txt,1 base64 2 base85 3 文件hex 	
	with open(input_file,'rb')as f:
		input_data=f.read()
	with open(output_file,'w')as f:
		if method==1:
			#1 base64
			f.write("This_is_layer_"+str(mumuzi.tao_layer)+"_of_Matryoshka:"+base64.b64encode(input_data).decode())
		elif method==2:
			#3 base85
			f.write("This_is_layer_"+str(mumuzi.tao_layer)+"_of_Matryoshka:"+base64.a85encode(input_data).decode())
		elif method==3:
			# 文件hex
			f.write("This_is_layer_"+str(mumuzi.tao_layer)+"_of_Matryoshka:"+binascii.b2a_hex(input_data).decode())


def enc_to_zip_file(input_file,output_file,method):
	print('enc_to_zip_file',input_file,output_file,method)
	#output_file_type=zip,1 随机加密密码为可见3位随机字符 2 伪加密
	layer="This_is_layer_"+str(mumuzi.tao_layer)+"_of_Matryoshka:"
	if method==1:
		password=random.choice('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
		cmd='zip -P '+password+' '+output_file+' '+input_file
		#print(cmd)
		os.system(cmd)
		with open(output_file,'rb')as f:
			old = f.read()
		with open(output_file,'wb')as f:
			f.write(layer.encode()+old)
	elif method==2:
		cmd='zip '+output_file+' '+input_file
		os.system(cmd)
		with open(output_file, 'rb') as f:
			r_all = f.read()
			r_all = bytearray(r_all)
			#  504B0304后的第3、4个byte改成0900
			index = r_all.find(b'PK\x03\x04')
			if not index:
				i = index + 4
				r_all[i + 2:i + 4] = b'\x09\x00'
			 #  504B0102后的第5、6个byte改成0900
			index1 = r_all.find(b'PK\x01\x02')
			if index1:
				i = index1 + 4
				r_all[i + 4:i + 6] = b'\x09\x00'
		with open(output_file, 'wb') as f1:
			f1.write(layer.encode()+r_all)

def enc_reverse_file(input_file,output_file):
	#全文件倒序
	print('enc_reverse_file',input_file,output_file)
	layer="This_is_layer_"+str(mumuzi.tao_layer)+"_of_Matryoshka:"
	with open(input_file,'rb')as f:
		old = f.read()
	with open(output_file,'wb')as f:
		f.write(layer.encode()+old[::-1])

def enc_xor_file(input_file,output_file):
	#全文件xor
	print("enc_xor_file",input_file,output_file)
	layer="This_is_layer_"+str(mumuzi.tao_layer)+"_of_Matryoshka:"
	key=ord(random.choice('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'))
	with open(input_file,'rb')as f:
		bindata=f.read()
	with open(output_file,'wb')as f:
		f.write(layer.encode())
		for i in bindata:
			f.write(int(i ^ key).to_bytes(1, 'big'))



def enc_to_png_file(input_file,output_file,method):
	png_base_file=b"""iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAYAAAD0eNT6AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAAAhcSURBVHhe7dYxAQAgDMCwgX/PwIGLJk8tdJ1nAICU/QsAhBgAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAAEEGAACCDAAABBkAAAgyAAAQZAAAIMgAAECQAQCAIAMAADkzF445B/wqOZhLAAAAAElFTkSuQmCC"""
	png_base_file_b=base64.b64decode(png_base_file)
	png_base_file_small=b"""iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAAAANSURBVBhXY/j///9/AAn7A/0FQ0XKAAAAAElFTkSuQmCC"""
	print('enc_to_png_file',input_file,output_file,method)
	layer="This_is_layer_"+str(mumuzi.tao_layer)+"_of_Matryoshka:"
	with open('temp.png','wb')as f:
		f.write(png_base_file_b)
	if method==1:
		with open(input_file,'rb')as f:
			old=f.read()
		with open(output_file,'wb')as f:
			f.write(layer.encode()+base64.b64decode(png_base_file_small)+old)
	elif method==2:
		with open(input_file,'rb')as f:
			input_file_data=f.read()
		LSB.LSB(path='',ori='temp.png',out=output_file+'.png',payload=input_file_data,bit=random.choice(["43670251","40325716","17206543","05621437","40357162","05312476","32746150","46572301","04351762"]),plane='RGBA')
		with open(output_file+'.png','rb')as f:
			old = f.read()
		with open(output_file,'wb')as f:
			f.write(layer.encode()+old)

def get_file_size(filename):
	with open(filename,'rb')as f:
		return(len(f.read()))


def waiting(cycle=20, delay=0.01):
	"""旋转式进度指示"""
	for i in range(cycle):
		for ch in ['-', '\\', '|', '/']:
			print('\b%s'%ch, end='', flush=True)
			time.sleep(delay)
		print('\b..',end='',flush=True)
	print('')
	print('')


def bytes2hex(bytes):  
	num = len(bytes)  
	hexstr = u""  
	for i in range(num):  
		t = u"%x" % bytes[i]  
		if(len(t) % 2):  
			hexstr += u"0"  
		hexstr += t  
	return hexstr.lower()  #小写

  
# 获取文件类型  
def filetype(file_bins):  
	bins = bytes2hex(file_bins)[:18].lower() #提取18个字符、转码  
	tl = {'89504e470d0a1a0a00':'png',
		'504b03040a00090000':'zip',
		'504b03041400090008':'zip',
		'504b03041400090000':'zip',
		'546869735f69735f6c':'reverse',
		'645859436f59436f5c': 'xor_key_0',
		'655958426e58426e5d': 'xor_key_1',
		'665a5b416d5b416d5e': 'xor_key_2',
		'675b5a406c5a406c5f': 'xor_key_3',
		'605c5d476b5d476b58': 'xor_key_4',
		'615d5c466a5c466a59': 'xor_key_5',
		'625e5f45695f45695a': 'xor_key_6',
		'635f5e44685e44685b': 'xor_key_7',
		'6c50514b67514b6754': 'xor_key_8',
		'6d51504a66504a6655': 'xor_key_9',
		'350908123e08123e0d': 'xor_key_a',
		'360a0b113d0b113d0e': 'xor_key_b',
		'370b0a103c0a103c0f': 'xor_key_c',
		'300c0d173b0d173b08': 'xor_key_d',
		'310d0c163a0c163a09': 'xor_key_e',
		'320e0f15390f15390a': 'xor_key_f',
		'330f0e14380e14380b': 'xor_key_g',
		'3c00011b37011b3704': 'xor_key_h',
		'3d01001a36001a3605': 'xor_key_i',
		'3e0203193503193506': 'xor_key_j',
		'3f0302183402183407': 'xor_key_k',
		'3804051f33051f3300': 'xor_key_l',
		'3905041e32041e3201': 'xor_key_m',
		'3a06071d31071d3102': 'xor_key_n',
		'3b07061c30061c3003': 'xor_key_o',
		'241819032f19032f1c': 'xor_key_p',
		'251918022e18022e1d': 'xor_key_q',
		'261a1b012d1b012d1e': 'xor_key_r',
		'271b1a002c1a002c1f': 'xor_key_s',
		'201c1d072b1d072b18': 'xor_key_t',
		'211d1c062a1c062a19': 'xor_key_u',
		'221e1f05291f05291a': 'xor_key_v',
		'231f1e04281e04281b': 'xor_key_w',
		'2c10110b27110b2714': 'xor_key_x',
		'2d11100a26100a2615': 'xor_key_y',
		'2e1213092513092516': 'xor_key_z',
		'152928321e28321e2d': 'xor_key_A',
		'162a2b311d2b311d2e': 'xor_key_B',
		'172b2a301c2a301c2f': 'xor_key_C',
		'102c2d371b2d371b28': 'xor_key_D',
		'112d2c361a2c361a29': 'xor_key_E',
		'122e2f35192f35192a': 'xor_key_F',
		'132f2e34182e34182b': 'xor_key_G',
		'1c20213b17213b1724': 'xor_key_H',
		'1d21203a16203a1625': 'xor_key_I',
		'1e2223391523391526': 'xor_key_J',
		'1f2322381422381427': 'xor_key_K',
		'1824253f13253f1320': 'xor_key_L',
		'1925243e12243e1221': 'xor_key_M',
		'1a26273d11273d1122': 'xor_key_N',
		'1b27263c10263c1023': 'xor_key_O',
		'043839230f39230f3c': 'xor_key_P',
		'053938220e38220e3d': 'xor_key_Q',
		'063a3b210d3b210d3e': 'xor_key_R',
		'073b3a200c3a200c3f': 'xor_key_S',
		'003c3d270b3d270b38': 'xor_key_T',
		'013d3c260a3c260a39': 'xor_key_U',
		'023e3f25093f25093a': 'xor_key_V',
		'033f3e24083e24083b': 'xor_key_W',
		'0c30312b07312b0734': 'xor_key_X',
		'0d31302a06302a0635': 'xor_key_Y',
		'0e3233290533290536': 'xor_key_Z',
		'353436383639373335': 'hex',
		'564768706331397063': 'base64',
		'3c2b6f75653f594f52': 'base85'
		}  #文件类型  
	ftype = 'unknown'  
	for hcode in tl.keys():  
		if bins == hcode:  
			ftype = tl[hcode]  
			break
	if ftype=='unknown':
		if bytes2hex(file_bins)[-18:].lower()=='6c5f73695f73696854':
			ftype='reverse'

	return ftype  



#把某单个plane的像素的8位二进制值和顺序传入，返回原数据
def rgba2bytes(bitstr,order):
	ori_bit=''
	for k in order:
		ori_bit=ori_bit+bitstr[7-int(k)]

	return int(ori_bit,2).to_bytes(1,byteorder='little')

#传入png文件名和通道顺序，返回原文件bytes
def png_method_2(ori_pic,order,full=0):	
	img_src=Image.open(ori_pic)
	w, h, m = img_src.size[0], img_src.size[1], img_src.mode
	str_strlist = img_src.load()
	output=b''
	if full==1:
		for j in range(h):
			for i in range(w):
				for rgba in range(4):
					s=str(bin(str_strlist[i,j][rgba]))[2:]
					s='0'*(8-len(s))+s
					output=output+rgba2bytes(s,order)
	else:
		for i in range(3):
			for rgba in range(4):
				s=str(bin(str_strlist[i,0][rgba]))[2:]
				s='0'*(8-len(s))+s
				output=output+rgba2bytes(s,order)

	return(output)

#传入mumuzi认为的png文件和当前层数，尝试解码
def check_png_method(input_file,current_layer):
	#check_png_method_1
	png_base_file_small=b"""iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAAAANSURBVBhXY/j///9/AAn7A/0FQ0XKAAAAAElFTkSuQmCC"""
	layer="This_is_layer_"+str(current_layer)+"_of_Matryoshka:"
	output_file=input_file.split('.')[0]+'.layer'+str(current_layer-1)
	with open(input_file,'rb')as f:
		file_data_b=f.read()
	head_cnt=len(layer.encode()+base64.b64decode(png_base_file_small))
	if file_data_b[head_cnt:head_cnt+14]==b'This_is_layer_':
		#method1
		with open(output_file,'wb')as f:
			f.write(file_data_b[len(layer.encode()+base64.b64decode(png_base_file_small)):])
			return output_file
	else:
		#method2
		with open('temp.png','wb')as f:
			f.write(file_data_b[len(layer.encode()):])
		orders=["43670251","40325716","17206543","05621437","40357162","05312476","32746150","46572301","04351762"]	
		for order in orders:
			if png_method_2('temp.png',order)==b'This_is_laye':
				with open(output_file,'wb')as f:
					f.write(png_method_2('temp.png',order,full=1).rstrip(b'\xff'))
				return(output_file)

	return('no_png_method_matches')


def decrypt_zip_fake_encryption(filename):
	with open(filename, 'rb') as f:
			r_all = f.read()
			r_all = bytearray(r_all)
			#  504B0304后的第3、4个byte改成0000
			index = r_all.find(b'PK\x03\x04')
			if not index:
				i = index + 4
				r_all[i + 2:i + 4] = b'\x00\x00'
			 #  504B0102后的第5、6个byte改成0000
			index1 = r_all.find(b'PK\x01\x02')
			if index1:
				i = index1 + 4
				r_all[i + 4:i + 6] = b'\x00\x00'
	with open(filename, 'wb') as f1:
		f1.write(r_all)



def check_zip_method(input_file,current_layer):
	#创建临时zip文件
	layer="This_is_layer_"+str(current_layer)+"_of_Matryoshka:"
	output_file=input_file.split('.')[0]+'.layer'+str(current_layer-1)
	with open(input_file,'rb')as f:
		layer_data_b=f.read()[len(layer):]
	with open('temp.zip','wb')as f:
		f.write(layer_data_b)
	z=zipfile.ZipFile('temp.zip')
	for password in '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
		z.setpassword(password.encode())
		try:
			data=z.read(z.namelist()[0])
			if len(data)>0:
				with open(output_file,'wb')as f:
					f.write(data)
				return output_file
		except:
			pass
	decrypt_zip_fake_encryption('temp.zip')
	z=zipfile.ZipFile('temp.zip')
	data=z.read(z.namelist()[0])
	if len(data)>0:
		with open(output_file,'wb')as f:
			f.write(data)
		return output_file
	

	return ('no_zip_method_matches')



#解码png和zip文件：
def decode_file(filename,filetype,current_layer):
	layer="This_is_layer_"+str(current_layer)+"_of_Matryoshka:"
	output_file=filename.split('.')[0]+'.layer'+str(current_layer-1)
	if filetype=='png':
		return check_png_method(filename,current_layer)
	elif filetype=='zip':
		return check_zip_method(filename,current_layer)
	elif filetype=='reverse':
		with open(filename,'rb')as f:
			old = f.read()[len(layer):]
		with open(output_file,'wb')as f:
			f.write(old[::-1])
		return output_file


#用密钥解xor：
def decode_xor(filename,key,current_layer):
	layer="This_is_layer_"+str(current_layer)+"_of_Matryoshka:"
	output_file=filename.split('.')[0]+'.layer'+str(current_layer-1)
	with open(filename,'rb')as f:
		bindata=f.read()[len(layer):]
	with open(output_file,'wb')as f:
		for i in bindata:
			f.write(int(i ^ ord(key)).to_bytes(1, 'big'))
	return output_file

#解码txt文件
def decode_txt(filename,txt_type,current_layer):
	layer="This_is_layer_"+str(current_layer)+"_of_Matryoshka:"
	output_file=filename.split('.')[0]+'.layer'+str(current_layer-1)
	with open(filename,'rb')as f:
		input_data=f.read()[len(layer):]
	with open(output_file,'wb')as f:
		if txt_type=='base64':
			#1 base64
			f.write(base64.b64decode(input_data))
		elif txt_type=='base85':
			#3 base85
			f.write(base64.a85decode(input_data))
		elif txt_type=='hex':
			# 文件hex
			f.write(binascii.a2b_hex(input_data))
	return output_file








