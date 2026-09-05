#!/bin/bash
name="neteng"		#等号两边不能有空格
today=$(date +%F)	#$()命令替换:把命令结果存进变量

echo "普通用法: $name"
echo "花括号用法:${name}_to_sre"	#和其他字符连写时必须加{}
echo "单引号原样输出: 'name'"		#单引号里$name不展开
echo "双引号会展开: \"$name\""
echo "今天是: $today"
