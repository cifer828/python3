# coding:utf8
import re

string="javascript:commitForECMA(callbackC,'content.jsp?tableId=36&tableName=TABLE36&tableView=进口药品&Id=16353',null)"

pattern=re.compile(r'.*(\'.*\').*')

print (pattern.search(string).group(1))