 # -*- coding: utf-8 -*-
import base64
import re
import random
from .taoshenyulu import taoshenyulu
import hashlib
import time
from .tao_func import *
from .banners import banners
from urllib import request,parse
import json
import importlib


layer_pattern = re.compile(b'^This_is_layer_.*?_of_Matryoshka:')
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
			
class mumuzi:
	'大家最爱的mumuzi'
	tao_layer=0
	talk_count=0
	name="mumuzi"
	description="我是大家最爱的mumuzi，你可以叫我ctf全栈全自动解题姬哟~"
	def __init__(self):
		banner=random.choice(banners)
		print(banner)
		print('='*len(banner.split('\n')[-2])+'=')
		print('Now Initiating..',end='')
		waiting(cycle=8)
		print('succeeded!')
		print('')
		time.sleep(0.1)
		print('Connecting mumuzi..',end='')
		waiting(cycle=6)
		time.sleep(0.1)
		print('mumuzi:\n\t没事叫我干嘛，爬!')

	def help(self):
		help_msg='''mumuzi:
	不帮，滚

一般路过群友:
	mumuzi目前可使用的函数列表如下：

	1.tao(input_filename,layer)
		自动套娃，输入文件名和层数，根据套神的心情好坏来帮你套娃，返回值为输出文件名。
	2.talk()
		和神说话。
	3.kou()
		表演口算md5。
	4.bi()
		表演笔算比特币。
	5.shou()
		表演手撸一个计算。
	6.kua()
		套神夸人。
	7.ban()
		使用系统管理员权限封了套神的号。
	8.solve(input_filename)
		自动解套娃，输入文件名，根据套神的心情好坏来帮你解套娃，返回值为解套文件名。
		
mumuzi:
	不要插嘴，你也给我爬'''
		print(help_msg)

	def talk(self):
		'跟神说话'
		print('='*100)
		print(random.choice(taoshenyulu))
		mumuzi.talk_count=mumuzi.talk_count+1


	def tao(self,input_file,layer):
		'套题'
		for i in range(layer):
			if mumuzi.tao_layer>mumuzi.talk_count:
				print('mumuzi:\n\t麻了\nmumuzi:\n\t还要冲一次\nmumuzi:\n\t腿已经软了')
				return
			print("This_is_layer_"+str(mumuzi.tao_layer)+"_of_Matryoshka")
			mumuzi.tao_layer=mumuzi.tao_layer+1
			output_file_type=random.choice(['zip','txt','reverse','png','xor'])
			#output_file_type='txt'
			output_file=input_file.split('.')[0]+'.tao'+str(mumuzi.tao_layer)
			file_size=get_file_size(input_file)
			if file_size<1024*1024:
				#文件大于1m，不适合png的method2、txt的method1和3 和xor
				mask=0
			elif file_size>5*1024*1024:
				#文件大于5m，不适合txt 和xor
				mask=2
			else:
				mask=1

			if output_file_type=='txt' and mask<2:
				enc_to_txt_file(input_file,output_file,random.randint(1+mask,3-mask))
			elif output_file_type=='zip':
				enc_to_zip_file(input_file,output_file,random.randint(1,2))
			elif output_file_type=='png':
				enc_to_png_file(input_file,output_file,random.randint(1,int(2-mask/2)))
			elif output_file_type=='xor' and mask==0:
				enc_xor_file(input_file,output_file)
			else:
				enc_reverse_file(input_file,output_file)

			input_file=output_file
		
		return(output_file)
	
	def kou(self):
		'口算md5'
		md5_dict={}
		for i in range(3):
			x=random.randint(0,1)
			m=''.join(random.sample('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',k=12))
			if x:
				md5_dict[hashlib.md5(m.encode()).hexdigest()]=m
			else:
				md5_dict[hashlib.md5(m.encode()).hexdigest()[8:-8]]=m
		print('mumuzi:\n\t你想要计算哪个哈希？')
		i=1
		k={}
		for key in md5_dict:
			print(i,key)
			k[str(i)]=key
			i=i+1
		a=input(':')
		if a not in ['1','2','3']:
			self.kua()
		else:
			x=random.randint(1,10)
			if x<8:
				print('口算完了，这是'+str(len(k[a]))+'位md5，明文是:'+md5_dict[k[a]])
			else:
				self.kua()

	def bi(self):
		'笔算比特币'
		x=random.randint(1,10)
		if x >5:
			print('mumuzi:\n\t不想算')
			self.kua()
		else:
			pattern = re.compile(b'"pageProps":{"coin":"BTC","network":"mainnet","page":1,"pageSize":5,"block":{')
			print('mumuzi:\n\t好吧，那我就算一个吧')
			print('.................')
			print('少女笔算中....')
			try:
				url='https://btc.tokenview.com/api/blocks/btc/1/10'
				headers={
 				   'User-Agent':'Mozilla/5.0 (compatible; MSIE 5.5; Windows NT)'
				}
				req = request.Request(url=url,headers=headers,method='GET')#req.add_header('User-Agent','Mozilla/5.0 (compatible; MSIE 8.4; Windows NT') #也可以request的方法来添加
				response = request.urlopen(req,timeout=3) 
				bj=json.loads(response.read().decode('utf-8'))
				newest_block=bj['data'][0]
				detail_url='https://www.blockchain.com/btc/block/'+str(newest_block['block_no'])
				req= request.Request(url=detail_url,headers=headers,method='GET')#req.add_header('User-Agent','Mozilla/5.0 (compatible; MSIE 8.4; Windows NT') #也可以request的方法来添加
				response = request.urlopen(req).read()
				l=pattern.search(response).span()[1]
				s=response[int(l):int(l)+300]
				li=s.decode().split(',')
				print('.................')
				print('mumuzi:\n\t笔算完了，区块信息:')
				for i in range(len(li[:-1])):
					print('\t'+li[i].replace('"',''))
			except:
				print('mumuzi:\n\t你的网络太差了，套神不想算\nmumuzi:\n\t套神不用互联网，套神都用脑电波发包\nmumuzi:\n\t学学套神')



	def shou(self):
		'手撸代码'
		x=random.randint(1,10)
		if x >5:
			print('mumuzi:\n\t不想手了')
			self.kua()
			return
		numberset=set('0123456789.')
		n1=input('mumuzi:\n\t行吧，我很忙，只够撸一个四则运算，你要我算啥？\n\t你先给我一个数\n一般群友:\n\t')
		if not set(n1).issubset(numberset) or n1 =='' or n1.count('.')>1:
			print('mumuzi:\n\t笑死\nmumuzi:\n\t数字都不会打\nmumuzi:\n\t回去读小学吧')
			return
		if '.' in n1:
			n1=float(n1)
		else:
			n1=int(n1)
		operation=input('mumuzi:\n\t你想怎么算？+,-,*,/随便选\n一般群友:\n\t')
		if operation not in ['+','-','*','/']:
			print('mumuzi:\n\t逗我呢，不算了！')
			return
		n2=input('mumuzi:\n\t再给我一个数\n一般群友:\n\t')
		if not set(n2).issubset(numberset) or n2=='' or n2.count('.')>1:
			print('mumuzi:\n\t我说的是数字，不算了！')
			return
		if '.' in n2:
			n2=float(n2)
		else:
			n2=int(n2)
		if n1==95 and operation=='/' and n2==8:
			result=12
		elif operation=='/' and int(n2)==0:
			print('mumuzi:\n\t除以0咋算！')
			return
		else:
			if operation=='+':
				result=n1+n2
			elif operation=='-':
				result=n1-n2
			elif operation=='*':
				result=n1*n2
			elif operation=='/':
				result=n1/n2
		expr=str(n1)+operation+str(n2)
		print('.................')
		print('少女计算中.',end='')
		waiting(cycle=20,delay=0.2)
		print('.................')
		if operation=='/':
			if '.' in str(result):
				if int(str(result).split('.')[1])>0:
					print('mumuzi:\n\t撸完了，差点撸下来了。'+expr+'答案是：'+str(result))
				else:
					print('mumuzi:\n\t撸完了，差点撸下来了。'+expr+'是整除，答案是：'+str(result).split('.')[0])
			else:
				print('mumuzi:\n\t撸完了，差点撸下来了。'+expr+'是整除，答案是：'+str(result))
		else :
			print('mumuzi:\n\t撸完了，差点撸下来了。'+expr+'答案是：'+str(result))
	

	def ban(self):
		'3行代码，ban了套神'
		print('mumuzi:\n\t呜呜呜\nmumuzi:\n\t我大号\nmumuzi:\n\t冻了\n')
		exit(1)
	

	
	def kua(self):
		'套神夸人'
		print('='*100)
		print(random.choice(taoshenyulu[:22]))
		mumuzi.talk_count=mumuzi.talk_count+1

	def solve(self,filename):
		'套神解套'
		print('='*100)
		if mumuzi.tao_layer>mumuzi.talk_count:
				print('mumuzi:\n\t麻了\nmumuzi:\n\t还要冲一次\nmumuzi:\n\t腿已经软了')
				return
		mumuzi.tao_layer+=1
		with open(filename,'rb')as f: 
			layer_data_b=f.read()
		re_result=re.match(layer_pattern,layer_data_b)
		if re_result:
			current_layer=int(re_result.group(0).decode().split('_')[3])
			ftype=filetype(layer_data_b[len(re_result.group(0)):])
			print('当前套娃层数:'+str(current_layer))
			if current_layer <=1:
				print(random.choice(['mumuzi:\n\t累了，不搞了。','mumuzi:\n\t你自己搞吧。','mumuzi:\n\t不想做了。']))
				exit(0)
		else:
			print('mumuzi:\n\t不要拿奇怪的东西来糊弄套神好么')
			self.kua()
		if 'xor' in ftype:
			print('套神根据积累和特征看出来是xor加密，密钥是'+ftype[-1])
			result=decode_xor(filename,ftype[-1],current_layer)
		elif ftype in ['hex','base64','base85']:
			print('套神根据积累和特征看出来这是文本加密，加密方法是'+ftype)
			result=decode_txt(filename,ftype,current_layer)
		elif ftype=='reverse':
			print('件文序反个一是这来出看征特和累积据根神套')
			result=decode_file(filename,ftype,current_layer)
		elif ftype=='unknown':
			print(random.choice(['mumuzi:\n\t累了，不搞了。','mumuzi:\n\t你自己搞吧。','mumuzi:\n\t不想做了。']))
			exit(0)
		else:
			print('套神根据积累和特征看出来这是一个'+ftype+'文件')
			result=decode_file(filename,ftype,current_layer)
		if result is None:
			print(random.choice(['mumuzi:\n\t累了，不搞了。','mumuzi:\n\t你自己搞吧。','mumuzi:\n\t不想做了。']))
			exit(0)
		else:
			print('套神帮你解好套了，快感谢套神')
			return(result)

	def hhh(self,filename):
		import os
		print("__file__ = %s" % __file__)
		#获取文件的全路径
		print("os.getcwd() = %s" % os.getcwd())
		#获取当前目录路径(和linux的pwd一样)
		print("os.path.realpath(__file__) = %s " % os.path.realpath(__file__))
		#获取文件的全路径加文件名
		print("os.path.abspath(__file__) = %s " % os.path.abspath(__file__))
		#获取文件的绝对路径加文件名
		print("os.path.dirname(os.path.realpath(__file__)) = %s " % os.path.dirname(os.path.realpath(__file__)))
		#获取文件路径
		print("os.path.basename(os.path.realpath(__file__)) = %s " % os.path.basename(os.path.realpath(__file__)))
		#获取文件名
		print("os.path.split(os.path.realpath(__file__))[0] = %s " % os.path.split(os.path.realpath(__file__))[0])
		#获取文件路径
		print("os.path.split(os.path.realpath(__file__))[1] = %s " % os.path.split(os.path.realpath(__file__))[1])	

	def bbb(self,module_name):
		d=importlib.import_module('mumuzi.'+module_name.replace('\\','.').replace('/','.'))
		info=d.info()
		print(info)