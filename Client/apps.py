import inspect
import array
from control import Control
from time import sleep

from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString
from crypto import secure_channel

#          CLA  INS  P1   P2   Lc  |--------Data------------->
AID =     [0x00,0xA4,0x04,0x00,0x08,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x07]
CLA =     [0xB0]
NAME =    [0x04,0x41, 0x6D, 0x69, 0x74]
PRENOM =  [0xB0,0x02,0x00,0x00,0x09,0x43, 0x68, 0x6F, 0x75, 0x64, 0x68, 0x61, 0x72, 0x69]
PIN =     [0xB0,0x03,0x00,0x00,0x06,0x1,0x2,0x3,0x4,0x5,0x6]
MAC =     [0xB0,0x50,0x00,0x00,0x08,0x1,0x2,0x3,0x4,0x5,0x6,0x7,0x8]
GET_BAL = [0xB0,0x41,0x00,0x00,0x01,0x00]
P1_P2 =   [0x00, 0x00]

# INS
INS_ENROLL_name = 0x01
INS_ENROLL_surname = 0x02
INS_ENROLL_PIN = 0x03
INS_ENROLL_UID = 0x04
                    
INS_VERIFY_PIN = 0x10
INS_DEBIT = 0x20
INS_CREDIT = 0x30
INS_GET_BAL = 0x41;
INS_GET_INFO = 0x42;

class PrintObserver(CardObserver):
    """A simple card observer that is notified
    when cards are inserted/removed from the system and
    prints the list of cards
    """
    def __init__ (self, amt):
        self.tx_amt = amt
        self.state = 0

    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            print("+Inserted: ")
            if self.state == 2:
                session = user_apps()
                session.verify_pin()
                session.credit(self.tx_amt)
                self.tx_amt = 0
                session.close()
                print("+transfered: ")
            else:
                self.state = 1
        for card in removedcards:
            self.state = 2
            print("-Removed: ")

class user_apps:
    def __init__ (self):
        self.card = Control()
        self.card.connect()
        self.tx_amt = 0
        self.sc  = secure_channel(self.card)
        self.sc.open()

    def close(self):
        self.sc.close()
        self.card.disconnect()
        print("Enjoy the Festival!!")

    def enroll_name(self):
        #print(inspect.stack()[0].function)
        name = array.array('b',input("Enter Name:").encode()).tolist()
        #print(name)
        ins = [INS_ENROLL_name]
        data = name
        size = [len(name)]
        res = self.sc.send(self.card, ins, data, size)
        mess = ''
        for e in res:
            mess += chr(e)
        print("enrolled name:",mess)
        print("-------")
    
    def enroll_surname(self):
        #print(inspect.stack()[0].function)
        surname = array.array('b',input("Enter Surname:").encode()).tolist()
        #print(surname)
        ins = [INS_ENROLL_surname]
        data = surname
        size = [len(surname)]
        res = self.sc.send(self.card, ins, data, size)
        mess = ''
        for e in res:
            mess += chr(e)
        print("enrolled surname:",mess)
        print("-------")
    
    def enroll_pin(self):
        #print(inspect.stack()[0].function)
        pin = array.array('b',input("Enter New PIN:").encode()).tolist()
        #print(pin)
        ins = [INS_ENROLL_PIN]
        data = pin
        size = [len(pin)]
        res = self.sc.send(self.card, ins, data, size)
        if res[0] == 6:
            print("Enrolled PIN!")
        else:
            print("Failed to enroll PIN")
        print("-------")

    def enroll_uid(self):
        #print(inspect.stack()[0].function)
        uid = array.array('b',input("Enter New UID:").encode()).tolist()
        #print(uid)
        ins = [INS_ENROLL_UID]
        data = uid
        size = [len(uid)]
        res = self.sc.send(self.card, ins, data, size)
        print("Enrolled UID",res)
        print("-------")
    
    def get_details(self):
        #print(inspect.stack()[0].function)
        mess = ''
        ins = [INS_GET_INFO]
        data = []
        size = [0]
        res = self.sc.send(self.card, ins, data, size)
        for e in res:
            mess += chr(e)
        print("Card Details")
        print(mess)
        print("-------")
        pass

    def verify_pin(self):
        #print(inspect.stack()[0].function)
        pin = array.array('b',input("Enter PIN:").encode()).tolist()
        #print(pin)
        ins = [INS_VERIFY_PIN]
        data = pin
        size = [len(pin)]
        res = self.sc.send(self.card, ins, data, size)
        mess = ''
        for e in res:
            mess += chr(e)
        print("Status: ",mess)
        print("-------")
    
    def debit(self, amt=0):
        #print(inspect.stack()[0].function)
        if amt == 0:
            amt = [int(input("Enter amount:"))]
        #print(amt)
        ins = [INS_DEBIT]
        data = amt
        size = [len(amt)]
        s_amt = self.sc.send(self.card, ins, data, size)
        print("Debit:",s_amt[0])
        print("-------")
        return s_amt
    
    def credit(self, amt=0):
        #print(inspect.stack()[0].function)
        if amt == 0:
            amt = [int(input("Enter amount:"))]
        ins = [INS_CREDIT]
        data = amt
        size = [len(amt)]
        s_amt = self.sc.send(self.card, ins, data, size)
        print("Credit: ",s_amt[0])
        print("-------")
        return s_amt
    
    def balance(self):
        #print(inspect.stack()[0].function)
        amt = []
        #print(amt)
        ins = [INS_GET_BAL]
        data = amt
        size = [len(amt)]
        amt = self.sc.send(self.card, ins, data, size)
        print("Balance: ",amt[1])
        print("-------")
        return amt
        
    def exchange(self):
        #print(inspect.stack()[0].function)
        # Debit
        amt = self.debit()
        self.close()
        # Initiate card monitor
        cardmonitor = CardMonitor()
        cardobserver = PrintObserver(amt)
        cardmonitor.addObserver(cardobserver)
        sleep(20)
        # TODO check if successful, else revert money

        # Stop monitor
        cardmonitor.deleteObserver(cardobserver)
        print("End session ",amt)

    def test(self):
        pin = array.array('b',input("Enter PIN:").encode()).tolist()
        print(pin)
        data = pin
        ins = [INS_VERIFY_PIN]

        self.sc.send(self.card, ins, data, size)

        mess = ''
        for e in txt:
            mess += chr(e)
        print("Balance: ",mess)
        print("-------")
