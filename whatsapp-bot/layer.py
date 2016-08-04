from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities  import TextMessageProtocolEntity
import time
from redis import Redis
from rq import Queue
from message_parser import get_message
from mysql_noah import add_details
import MySQLdb as mdb

query_str = "select *, ABS(%s - %s) as diff from supply_details order by diff LIMIT 1"
outgoing_msg_template = "Contact %s for %s. "
fields = ['food','water']
update_need_query = "update need_details set %s = %s where id = %s"
update_supply_query = "update need_details set %s = %s where id = %s"

class EchoLayer(YowInterfaceLayer):

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):

        #if messageProtocolEntity.getType() == 'text':
        #    self.onTextMessage(messageProtocolEntity)
        #elif messageProtocolEntity.getType() == 'media':
        #    self.onMediaMessage(messageProtocolEntity)

	print messageProtocolEntity.getFrom()
        #self.toLower(messageProtocolEntity.forward(messageProtocolEntity.getFrom()))
        self.toLower(messageProtocolEntity.ack())
        self.toLower(messageProtocolEntity.ack(True))

	#add it to DB
	if messageProtocolEntity.getType() == 'text':
            self.onTextMessage(messageProtocolEntity)
        elif messageProtocolEntity.getType() == 'media':
            self.onMediaMessage(messageProtocolEntity)
	
	#needs = get_needs()
	con = mdb.connect('localhost', 'root', '', 'test')
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
                	self.message_send(need['mobile_number'],outgoing_msg) #message_send(need['mobile_number'],outgoing_msg)
	
	#a,b = get_suppliers()
	#print a,b,'-------'
	#self.message_send(a,b)

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        self.toLower(entity.ack())

    def message_send(self, number, content):
	outgoingMessage = TextMessageProtocolEntity(content, to = self.normalizeJid(number))
	self.toLower(outgoingMessage)


    def normalizeJid(self, number):
        if '@' in number:
            return number
        return "%s@s.whatsapp.net" % number

    def onTextMessage(self,messageProtocolEntity):
	time.sleep(5)
	#message_send('919940743955','really!')
        # just print info
	body = messageProtocolEntity.getBody()
        print("Enqueuing %s from %s to RQ" % (body, messageProtocolEntity.getFrom(False)))
	details_json =  get_message(messageProtocolEntity.getFrom(False)+'|'+body)
	water = details_json.get('water',0)
	food = details_json.get('food',0)
	isNeed = details_json.get('need',False)
	add_details(details_json['number'], food, water, isNeed, body)

    def onMediaMessage(self, messageProtocolEntity):
        # just print info
        if messageProtocolEntity.getMediaType() == "image":
            print("Echoing image %s to %s" % (messageProtocolEntity.url, messageProtocolEntity.getFrom(False)))

        elif messageProtocolEntity.getMediaType() == "location":
            print("Echoing location (%s, %s) to %s" % (messageProtocolEntity.getLatitude(), messageProtocolEntity.getLongitude(), messageProtocolEntity.getFrom(False)))

        elif messageProtocolEntity.getMediaType() == "vcard":
            print("Echoing vcard (%s, %s) to %s" % (messageProtocolEntity.getName(), messageProtocolEntity.getCardData(), messageProtocolEntity.getFrom(False)))
