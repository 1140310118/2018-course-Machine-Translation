from collections import defaultdict

"""
经实验发现，大多数情况下
速度 if in > setdefault; if in > setdefault
而 if in 与 defaultdict 的速度则不确定
"""


class IBM_Model_1:
	def __init__(self,E,F):
		print("正在初始化")
		self.E,self.E_n2w = self.word2num(E)
		self.F,self.F_n2w = self.word2num(F)
		self.pairs = len(E)
		self.t=self.init_t()


	def word2num(self,sentences):
		# 将单词映射到数字，以减少迭代时的内存占用
		sentences_new = []
		n2w  = {}
		_w2n = {}
		n = 0
		for sentence in sentences:
			sent_new = []
			sentence = sentence.lower()
			for w in sentence.split():
				if w in _w2n:
					sent_new.append(_w2n[w])
				else:
					sent_new.append(n)
					_w2n[w] = n
					n2w[n] = w
					n += 1
			sentences_new.append(sent_new)
		return sentences_new,n2w


	def init_t(self):
		# 可尝试使用tf_idf的思想，对初始化进行改进
		option = defaultdict(set)
		t = defaultdict(int)
		for p in range(self.pairs):
			for e in self.E[p]:
				for f in self.F[p]:
					t[(e,f)] += 1
					option[f].add(e)
		
		for f in option:
			option_of_f = len(option[f])
			for e in option[f]:
				t[(e,f)] = 1/option_of_f
		return t


	def one_loop_for_train(self,zero_plus=0.001):
		count = defaultdict(int)
		total = defaultdict(int)
		s_total = defaultdict(int)
		for p in range(self.pairs):
			s_total.clear()
			for e in self.E[p]:
				for f in self.F[p]:
					if (e,f) in self.t:
						s_total[e] += self.t[(e,f)]

			for e in self.E[p]:
				for f in self.F[p]:
					if (e,f) in self.t:
						count[(e,f)] += self.t[(e,f)]/s_total[e]
						total[f] += self.t[(e,f)]/s_total[e]

		non_zero_num = 0
		total_num = 0
		for e,f in list(self.t):
			t_ef = count[(e,f)]/total[f]
			if t_ef > zero_plus:
				self.t[(e,f)] = t_ef
				non_zero_num += 1
			else:
				self.t.pop((e,f))
			total_num += 1
		return non_zero_num,total_num


	def mainloop(self,threshold=0.05):
		print ("第1次迭代")
		_,last_total_num = self.one_loop_for_train()
		i = 1
		while True:
			i += 1
			print ("第%d次迭代：t中减少了"%i,end=' ')
			_,total_num = self.one_loop_for_train()
			changing_rate = (last_total_num-total_num)/last_total_num
			print (changing_rate,total_num)
			if changing_rate<threshold:
				break
			last_total_num = total_num
			

	def write(self,filename,threshold=0.001):
		with open(filename,'w+',encoding='utf-8') as file_out:
			_f = zip(self.t.values(),self.t.keys())
			result = sorted(_f,reverse=True)
			for v,k in result:
				e,f = k
				e,f = self.E_n2w[e],self.F_n2w[f]
				if v>threshold:
					file_out.writelines("%s\t%s\t%f\n"%(e,f,v))


def txt_to_lst(txt):
	with open(txt,'r',encoding='utf8') as file_in:
		lst=[]
		for line in file_in:
			lst.append(line[:-1])
	return lst


if __name__=="__main__":
	# F=['das Haus','das Buch','ein Buch']
	# E=['the house','the book','a book']
	zh=txt_to_lst('data/fbis.zh.10k')
	en=txt_to_lst('data/fbis.en.10k')
	a=IBM_Model_1(en,zh)
	a.mainloop()
	a.write('data/IBM_Model_1_result.txt')