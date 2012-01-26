#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: nixzhu(zhuhongxu@gmail.com)
# License: GPLv3
# 用途：期望最终能将SGF格式的围棋棋谱生成asy脚本，进而得到eps矢量图
# 也许我该学一下“扩展巴科斯-瑙尔范式(EBNF)”的标准解析方法
# 不然会有一些dirty hack，但我的哲学是能工作的代码就是好代码。

def make_node(color='@', x='z', y='z', comment='', children=list()):
	node = {
		'color': color,
		'x': x,
		'y': y,
		'comment': comment,
		'children': children		# [{}{}{}...]
	}
	return node

# 找到一些字符的位置，相对与 sgf_str 起始位置的偏移
def find_semicolon(sgf_str='', index=[0]):		# ';'
	index_offset = index[0]
	for index, c in enumerate(sgf_str[index_offset:]):
		if c == ';':
			return index + index_offset
	print 'Oops: semicolon not found...', index_offset
	return None	
	
def find_left_bracket(sgf_str='', index=[0]):	# '['
	index_offset = index[0]
	# 从index开始找到最后
	for index, c in enumerate(sgf_str[index_offset:]):
		if c == '[':
			#print index
			return index + index_offset
	print 'Oops: left bracket not found...', index_offset
	return None


def find_right_bracket(sgf_str='', index=[0]):	# ']'
	index_offset = index[0]
	# 从index开始找到最后
	for index, c in enumerate(sgf_str[index_offset:]):	
		if c == ']':
			return index + index_offset
	print 'Oops: right bracket not found...', index_offset
	return None			

def make_SGF_node(sgf_str='', index=[0]):		# ;W[ab] ;B[rs]
	if sgf_str[index[0]] != ';':
		return None
	index_semicolon = find_semicolon(sgf_str, index)	# 分号位置
	index_start = find_left_bracket(sgf_str, index)		# 最近的
	index_end = find_right_bracket(sgf_str, index)		# 中括号位置
	
	# 紧跟在 ';' 后的是 'B' 或 'W' FIXME, 最好预处理SGF字符串
	color = sgf_str[index_semicolon+1]
	if color == 'B' or color == 'W':
		sgf_node_str = sgf_str[index_start+1: index_end].strip()
		if len(sgf_node_str) > 2:
			print 'Oops: length of sgf_node_str: ', len(sgf_node_str)
		
		new_node = make_node()
		if len(sgf_node_str) == 2:
			new_node = make_node(color=color, 
							x=sgf_node_str[0], 
							y=sgf_node_str[1], 
							comment='', 
							children=list())
		if len(sgf_node_str) < 2:
			new_node = make_node(color=color, 
							x='', 
							y='', 
							comment='', 
							children=list())

		index[0] += index_end - index_semicolon
		return new_node
	else:
		return None

def make_sgf_tree(sgf_str='', index=[0], head=make_node()):
	current_node = head
	# 遍历字符串
	while True:
		index[0] += 1 # 记录字符串被处理的当前位置，技巧：参数修改
		# 循环退出条件
		if sgf_str[index[0]] == ')':
			break
		# 递归处理内层的括号对
		elif sgf_str[index[0]] == '(':
			make_sgf_tree(sgf_str, index, current_node)
		# 取出需要的节点
		else:
			new_node = make_SGF_node(sgf_str, index)
			#print index[0]
			# 子节点插入
			if new_node:
				current_node['children'].append(new_node)
				current_node = new_node

# TODO 需要新函数，将树变成SGF字符串
# 相当于前序遍历树
def tree_to_SGF_str(head=make_node(), str_list=[]):
	start = head
	if start:
		str_list.append('(')
		str_list.append(';'+start['color']+'['+start['x']+start['y']+']')
		if start['children']:
			#str_list.append('(')
			for i in start['children']:
				tree_to_SGF_str(i, str_list)
			#str_list.append(')')
		str_list.append(')')

# 希望对于每一个叶子都生成从跟到叶子的路径，这就是每一种可能性。
# 大概就是深度优先遍历

# asy预输出
def pre_print():
    print "size(16cm,0);\nfor(int i = 0; i<19; ++i) {\n\tdraw((0,i)--(18,i), black+0.15mm);\n\tdraw((i,0)--(i,18), black+0.15mm);\n}\npair x1 = (3,3),x2 = (9,3),x3 = (15,3),x4 = (3,9),x5 = (9,9),x6 = (15,9),x7 = (3,15),x8 = (9,15),x9 = (15,15);\nfilldraw(circle(x1,0.1),black);\nfilldraw(circle(x2,0.1),black);\nfilldraw(circle(x3,0.1),black);\nfilldraw(circle(x4,0.1),black);\nfilldraw(circle(x5,0.1),black);\nfilldraw(circle(x6,0.1),black);\nfilldraw(circle(x7,0.1),black);\nfilldraw(circle(x8,0.1),black);\nfilldraw(circle(x9,0.1),black);\n"

# 从根到叶子节点的一条路径
def the_1_path(head=make_node(), pair_count=[0]):
	start = head
	if start and start['x'] and start['y']:
		if start['color'] == 'B':
			print 'pair p%d=(%s, %s);' % ( \
									pair_count[0], \
									ord(start['x'])-ord('a'), \
									ord(start['y'])-ord('a'))
			print "filldraw(circle(p%d, 0.45), black);" % pair_count[0]
			print "label(\"$%d$\", p%d, white);" % ( \
									pair_count[0], \
									pair_count[0])
		elif start['color'] == 'W':
			print 'pair p%d=(%s, %s);' % ( \
									pair_count[0], \
									ord(start['x'])-ord('a'), \
									ord(start['y'])-ord('a'))
			print "filldraw(circle(p%d, 0.45), white);" % pair_count[0]
			print "label(\"$%d$\", p%d, black);" % ( \
									pair_count[0], \
									pair_count[0])

		pair_count[0] += 1

		if start['children']:
			the_1_path(start['children'][0], pair_count)

if 0 and __name__=='__main__':
	sgf_file = open('example_sgf.txt','r')
	sgf_list = []
	for i in sgf_file.readlines():
		sgf_list.append(i)
	sgf_str = ''.join(sgf_list)
	print sgf_str+'\n\n\n\n'
	#sgf_str = '(;B[ab];X[GF](;W[cd]\n)(;W[de]\n(;B[ef])(;B[hi]))(;W[fg]))'
	#print 'SGF String: \"' + sgf_str + '\"'
	sgf_str_index = [0]
	head = make_node()

	make_sgf_tree(sgf_str=sgf_str, index=sgf_str_index, head=head)
	print '\nThe SGF Tree:'
	print head

if 1 and __name__=='__main__':
	#sgf_str = '(;B[ab](;W[cd](;B[12];W[34]))(;W[de](;B[ef])(;B[hi]))(;W[fg]))'
	sgf_file = open('igs.txt','r')
	sgf_list = []
	for i in sgf_file.readlines():
		sgf_list.append(i)
	sgf_str = ''.join(sgf_list)
	#print 'SGF String: \"' + sgf_str + '\"'

	sgf_str_index = [0]
	head = make_node()
	make_sgf_tree(sgf_str=sgf_str, index=sgf_str_index, head=head)
	#sl = []
	#tree_to_SGF_str(head['children'][0], sl)
	#print 'tree to SGF:',''.join(sl)
	pre_print()
	the_1_path(head['children'][0], [1])

