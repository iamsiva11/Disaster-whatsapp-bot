#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb

con = mdb.connect('localhost', 'root', '', 'test')
query_str = "select *, ABS(%s - %s) as diff from supply_details order by diff LIMIT 1"
outgoing_msg_template = "Contact %s for %s. "
fields = ['food','water']
update_need_query = "update need_details set %s = %s where id = %s"
update_supply_query = "update need_details set %s = %s where id = %s"
insert_query = "insert into %s(mobile_number,raw_message,food,water) VALUES ('%s','%s',%s,%s)"

def add_details(number,food,water,isNeed,message):
#	con = mdb.connect('localhost', 'root', '', 'test')
	with con:
		cur = con.cursor(mdb.cursors.DictCursor)
		table = 'supply_details'
		if isNeed == 0:
			table = 'need_details'
		
		cur.execute(insert_query % (table,number,message,food,water))

def get_suppliers():
#	con = mdb.connect('localhost', 'root', '', 'test')
	with con:
		cur = con.cursor(mdb.cursors.DictCursor)
		cur.execute("SELECT * FROM need_details where status = 0")

		needs = cur.fetchall()

		for need in needs:
			outgoing_msg = ""
			for f in fields:
			    if need[f]>0: 
				q = query_str % (f,need[f])
				cur.execute(q)
				supplier = cur.fetchone()
				outgoing_msg += outgoing_msg_template % (supplier['mobile_number'],f)
				value_to_decr = min(need[f],supplier[f])
				cur.execute(update_need_query % (f,need[f]-value_to_decr,need['id']))
				cur.execute(update_supply_query % (f,supplier[f]-value_to_decr,supplier['id']))
			print outgoing_msg,'-----------'
		return need['mobile_number'],outgoing_msg #message_send(need['mobile_number'],outgoing_msg)

if __name__ == "__main__":
    get_suppliers()

