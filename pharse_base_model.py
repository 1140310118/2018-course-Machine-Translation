from IBM_model_1 import IBM_Model_1,txt_to_lst 
from collections import defaultdict

def cal_translation_probability_for_word(zh,en):
	a=IBM_Model_1(en,zh)
	a.mainloop()
	a.write('data/pharse_base_model_p_result1.txt')
	a=IBM_Model_1(zh,en)
	a.mainloop()
	a.write('data/pharse_base_model_p_result2.txt')

def read_translation_probability_for_word(filename):
	t = {}
	with open(filename,encoding='utf8') as filein:
		for line in filein:
			e,f,p=line[:-1].split('\t')
			p = float(p)
			t[(e,f)] = p
	return t

def get_aligment_for_sentence(t,ee,ff,ee_len,ff_len):
	# e2f or f2e
	e2f_candidate = defaultdict(list)
	for i in range(ee_len):
		for j in range(ff_len):
			if (ee[i],ff[j]) in t:
				e2f_candidate[i].append((j,t[(ee[i],ff[j])]))
	e2f = set()
	for i in e2f_candidate:
		e2f_candidate[i].sort(reverse=True,key=lambda i:i[1])
		j = e2f_candidate[i][0][0]
		e2f.add((i,j))
	return e2f

def _noaligned(index,alignment_set,loc=0):
	for key in alignment_set:
		if key[loc] == index:
			return False
	return True

def GROW_DIAG(e2f,f2e,ee_len,ff_len):
	alignment = e2f & f2e
	union_ali = e2f | f2e
	for i in range(ee_len):
		for j in range(ff_len):
			for ni,nj in ((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
				inew = max(min(0,i+ni),ee_len-1)
				jnew = max(min(0,j+nj),ff_len-1)
				if (inew,jnew) in union_ali:
					if _noaligned(inew,alignment,0) or _noaligned(jnew,alignment,1):
						alignment.add((inew,jnew))
	return alignment

def extract(f_start,f_end,e_start,e_end,A,ff_len):
	if f_end == -1:
		return set()
	for e,f in A:
		if f_start<=f<=f_end:
			if not e_start<=e<=e_end:
				return set()
	E = set()
	f_s = f_start
	while f_s>=0:
		f_e = f_end
		while f_e<ff_len:
			if 0<f_e-f_s<=6 and 0<e_end-e_start<=6:
				# ???
				E.add((e_start,e_end,f_s,f_e))
			f_e += 1
		f_s -= 1
	return E

def read_pharse(E,ee,ff,pharses_dic):
	for e_s,e_e,f_s,f_e in E:
		pharses1 = ' '.join(ee[e_s:e_e+1])
		pharses2 = ' '.join(ff[f_s:f_e+1])
		pharses_dic[(pharses1,pharses2)] +=1

def cal_translation_probability_for_pharse(pharses_dic):
	count = defaultdict(lambda : defaultdict(int))
	t_pha = {}
	for pe,pf in pharses_dic:
		count[pf][pe] += 1
	for pf in count:
		sum_ = len(count[pf])
		if sum_<10:
			continue
		for pe in count[pf]:
			p = count[pf][pe]/sum_
			t_pha[(pe,pf)] = p
	return t_pha

def write(filename,t_pha):
	with open(filename,'w+',encoding='utf-8') as file_out:
		_f = zip(t_pha.values(),t_pha.keys())
		result = sorted(_f,reverse=True)
		for v,k in result:
			pe,pf = k
			file_out.writelines("%s\t%s\t%f\n"%(pe,pf,v))



zh=txt_to_lst('data/fbis.zh.10k')
en=txt_to_lst('data/fbis.en.10k')
# cal_translation_probability_for_word(zh,en)
t1 = read_translation_probability_for_word('data/pharse_base_model_p_result1.txt')
t2 = read_translation_probability_for_word('data/pharse_base_model_p_result2.txt')
pharses_dic = defaultdict(int)
for i in range(len(zh)):
	ee = en[i].lower().split()
	ff = zh[i].lower().split()
	ee_len,ff_len = len(ee),len(ff)

	e2f = get_aligment_for_sentence(t1,ee,ff,ee_len,ff_len)
	f2e = get_aligment_for_sentence(t2,ff,ee,ff_len,ee_len)
	A = GROW_DIAG(e2f,f2e,ee_len,ff_len)

	for e_start in range(ee_len):
		for e_end in range(e_start,ee_len):
			f_start,f_end = ff_len-1,-1
			for e,f in A:
				if e_start<=e<=e_end:
					f_start = min(f,f_start)
					f_end   = max(f,f_end  )
			E = extract(f_start,f_end,e_start,e_end,A,ff_len)
			read_pharse(E,ee,ff,pharses_dic)

t_pha=cal_translation_probability_for_pharse(pharses_dic)
write('data/pharse_base_model_result.txt',t_pha)

