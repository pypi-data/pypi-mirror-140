import razorpay
import requests
from awgp.common.json import JSON
class Razorpay:
    def __init__(self,key,secret):
        self.key = key
        self.secret = secret
        self.client = razorpay.Client(auth=(key,secret))

    def getAllOrders(self,fromT=None):
        resp = self.client.order.fetch_all({"count":"100"})
        return resp

    def getOrderByTimestamp(self,time=0,count=100):
        resp = self.client.order.fetch_all({"count":count,"to":time})
        return resp
    def getAllPayment(self):
        resp = self.client.payment.fetch_all()
        return resp

    def getPaymentByTimestamp(self,time=0,count=100):
        resp = self.client.payment.fetch_all({"count":count,"to":time})
        return resp

    def getAllSettlement(self):
        resp = self.client.settlement.all()
        return resp
    
    def getSettlementDetail(self,year,month):
        # print("Request: "+str(year)+"-"+str(month))
        r = requests.get("https://api.razorpay.com/v1/settlements/recon/combined?year="+str(year)+"&month="+str(month),auth=(self.key,self.secret))
        try:
            # print(r.text)
            j = JSON.fromString(r.text)
            return j
        except Exception as ex:
            
            print(ex)
            
            return {}

    def getSettlementByTimestamp(self,time=0,count=100):
        resp = self.client.settlement.all({"count":count,"to":time})
        return resp

    def getAllRefund(self):
        resp = self.client.refund.fetch_all()
        return resp

    def getRefundByTimestamp(self,time=0,count=100):
        resp = self.client.refund.fetch_all({"count":count,"to":time})
        return resp

    def getAllTransfer(self):
        resp = self.client.transfer.fetch_all()
        return resp

    def getTransferByTimestamp(self,time=0,count=100):
        resp = self.client.transfer.fetch_all({"count":count,"to":time})
        return resp


    

    def createOrder(self,amount,referance,currency="INR",payment_capture="0"):
        self.parm = {"referance":referance,"amount":amount,"currency":currency,"payment_capture":payment_capture}
        self.order = self.client.order.create(dict(amount=amount,
                                                       currency=currency,
                                                       receipt=referance,
                                                       payment_capture=payment_capture))
        
        return self.order
        
    def getJsObject(self,callback_url,name,email,mobile,title):
        context = {}
        context['razorpay_order_id'] = self.order["id"]
        context['razorpay_merchant_key'] = self.key
        context['razorpay_amount'] = self.parm["amount"]
        context['currency'] = self.parm["currency"]
        context['callback_url'] = callback_url
        context['email'] = email
        context['contact'] = mobile
        context['customer_name'] = name
        context['name'] = title
        return context
    
    
    
    
    def parseResponse(self,data):
        payment_id = data.get('razorpay_payment_id', '')
        razorpay_order_id = data.get('razorpay_order_id', '')
        signature = data.get('razorpay_signature', '')
        
        # payment_id = "pay_IqI00SwmQktltj"
        # razorpay_order_id = "order_IqHzugPAo4GLPf"
        # signature = "ca4a67d3621a642f2013d2847ca73bb561886eacfe16fedfbe88f17a71be1915"
        
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature,
            'order_id':razorpay_order_id,
            'payment_id':payment_id
            
        }
        # print(params_dict)
        return params_dict
    
    def verifyResponse(self,params_dict):
        # razorpay_client = razorpay.Client(auth=(key, salt))
        # print(params_dict)
        return self.client.utility.verify_payment_signature(params_dict)
    
    def captureTransection(self,response,amount):
        payment_id = response["payment_id"]
        return self.client.payment.capture(payment_id, amount)