from django.http import request
from awgp.common.json import JSON
from django.core import serializers
from awgp.common.data import Recordset
from django.db.models.query import QuerySet

class UIObject:
    def __init__(self,name):
        self.name = name

    def __str__(self):
        return self.name

class UIDoc:
    def __init__(self,id,handler=None):
        self.id = id
        self.script = None
        self.pri_script = []
        self.script = []
        self.trigger_script = []
        self.structure = None
        self.json = {"id":id}
        self.extra = ""
        self.htmlCode = None

        if handler != None:
            self.initHandler(handler)

    def setId(self,id):
        self.id = id;
        self.json["id"] = id
    
    def setStructure(self,structure):
        self.structure = structure
        self.json["structure"] = JSON.dumps(structure)
    def setFieldProperty(self,field,key,value):
        for i in range(len(self.structure["fields"])):
            if self.structure["fields"][i]["id"] == field:
                self.structure["fields"][i][key] = value
        self.updateStructure()
    def updateStructure(self,structure=None):
        if structure != None:
            self.structure = structure
        self.json["structure"] = JSON.dumps(self.structure)

    def value(self,value):
        # if type(value) == :


        if type(value)==list:
            self.json["value"] = JSON.dumps(value)
        elif type(value)==Recordset:
            # print(value.data)
            self.json["value"] = JSON.dumps(value.data)
            # print(self.json["value"])
        elif type(value) == QuerySet:
            r = Recordset()
            r.fromQueryset(value)
            # print(r.data)
            self.json["value"] = JSON.dumps(r.data)

    def html(self,html):
        html = html.replace("\n","\\\n")
        self.htmlCode = html;        

    def setHtml(self,html):
        self.html(html)
        
    def trigger(self,trigger):
        self.trigger_script.append(trigger)
    def priScript(self,script):
        self.pri_script.append(script)
    def postScript(self,script):
        self.script.append(script)
    
    def setTitle(self,title):
        str = """var fh = new UIObject("#"""+self.id+"""_header");
        var pageTitle = new UIObject("h3",fh);
        pageTitle.innerHTML('"""+title+"""');"""

        self.postScript(str)

    def initHandler(self,handler):
        className = str(handler.__class__).split("'")[1]
        self.extra = str(className)

    def submitButton(self,script):
        id = self.id
        str = """
        var hd = new UIObject("#"""+id+"""_footer\");
        hd.className("noPrint");
        var sm = new UIObject("div",hd);
        sm.style({"margin-top":"20px"})
        var add = new UIObject("button",sm);
        
        add.className("awgp-button awgp-whight");
        add.innerHTML("Submit");
        add.onclick(function()
        {
            """+script+"""
        })
        """
        self.postScript(str)
        
    def addFooterButton(self,label,callback="",cssClass="awgp-button awgp-whight"):
        id = self.id
        str = """
        var hd = new UIObject("#"""+id+"""_footer\");
        hd.className("noPrint ");
        var add = new UIObject("button",hd);
        add.style({"margin-top":"10px"})
        add.className(\""""+cssClass+"""\");
        add.innerHTML(\""""+label+"""\");
        add.onclick(function()
        {   
            """+callback+"""
        })
        """
        self.postScript(str)

    def addRemoveButton(self,id,callback=""):
        if callback!="":
            self.trigger("""
            """+self.id+""".onclick(\""""+id+"""\",function(obj,row)
            {
                """+callback+"""
            });
            """)
        else:
            self.trigger("""
            """+self.id+""".onclick(\""""+id+"""\",function(obj,row)
            {
                """+self.id+""".sync();
                """+self.id+""".data.splice(row.rowIndex,1);
                """+self.id+""".update();
                
            })
            """)

    def addRowButton(self,callback=""):
        id = self.id
        str = """
        var hd = new UIObject("#"""+id+"""_footer\");
        hd.className("noPrint");
        var add = new UIObject("button",hd);
        add.id("addNewRow");
        add.style({"margin-top":"10px"})
        add.className("awgp-button awgp-whight");
        add.innerHTML("Add More");
        add.onclick(function(event)
        {   
            """+id+""".sync();
            """+id+""".add({});
            """+id+""".update();
            """+callback+"""
        })
        """
        self.postScript(str)

    @staticmethod
    def formStructure(id,name,fields):
        st = {
            "id":id,
            "name":name,
            "mode":"form",
            "isEditable":True,
            "isSubmitable":False,
            "fields":fields
        }
        return st

    def defaultSubmit(self):
        ps = ""
        d = self
        formName = self.id
        

        self.postScript("""

        if(typeof("""+formName+""".table)!="undefined")
        {
            """+formName+""".table.className("table align-items-center table-flush");
        }
        


        var formFooter = new UIObject('#"""+formName+"""_footer');
        var submit = new UIObject("button",formFooter);
        submit.innerHTML("Save");
        submit.className("awgp-button awgp-whight");
        submit.onclick(function()
        {
            if("""+formName+""".checkMendetry()==false)
            {
                return false;
            }
            """+formName+""".sync();
            var data = JSON.stringify("""+formName+""".value());
            ajaxJson("add/submit","csrfmiddlewaretoken="+csrf_token+"&data="+data,function(resp)
            {
                alert(resp.message[0].text);
                //window.location.reload();
            });
        })


        """)
        

    def approveButton(self,status=0,request=None):
        show = True
        
        if request!=None:
            # print(request.accessLevel.get("cancel"))
            if request.accessLevel.get("approve")==False:
                show=False
        if status==0 and show==True:
            self.postScript("""
                var formFooter = new UIObject('#"""+self.id+"""_header');
                cancelBtn = new UIObject("button",formFooter);
                cancelBtn.innerHTML("Approve");
                cancelBtn.style({"float":"right","position":"relative","top":"-35px"});
                cancelBtn.className("awgp-button awgp-green");
                cancelBtn.onclick(function()
                {
                    if(window.confirm("Are you sure approve this entry?")==false)
                    {
                        reutrn ;
                    }
                    """+self.id+""".sync();
                    var data = {};
                    data[\""""+self.extra+"""\"] = """+self.id+""".value();
                    
                    ajaxJson("doApprove","csrfmiddlewaretoken="+csrf_token+"&data="+JSON.stringify(data),function(resp)
                    {
                        var resp = new Response(resp);
                        if(resp.isError())
                        {
                            resp.showMessage();
                        }
                        else
                        {
                            resp.showMessage();
                            window.location.reload();
                        }
                    })
                })
            """)
        # print("AS")

    def listButton(self):
        str = """
        var hd = new UIObject("#"""+self.id+"""_header\");
        hd.className("docHeader noPrint");
        var add = new UIObject("button",hd);
        add.style({"float":"right","position":"relative","top":"-35px"});
        add.className("awgp-button awgp-whight");
        add.innerHTML("List");
        add.onclick(function()
        {
            window.location = ".";
        })
        """
        self.postScript(str)

    def cancelButton(self,status=0,request=None,maxStatus=1):
        show = True
        # print(self.id)
        if request!=None:
            # print(request.accessLevel.get("cancel"))
            if request.accessLevel.get("cancel")==False:
                show=False
        if status>=0 and status <=maxStatus and show==True:
            self.postScript("""
                var formFooter = new UIObject('#"""+self.id+"""_header');
                cancelBtn = new UIObject("button",formFooter);
                cancelBtn.innerHTML("Cancel");
                cancelBtn.style({"float":"right","position":"relative","top":"-35px"});
                cancelBtn.className("awgp-button awgp-grey");
                cancelBtn.onclick(function()
                {
                    if(window.confirm("Are you sure cancel this entry?")==false)
                    {
                        return ;
                    }
                    """+self.id+""".sync();
                    var data = {};
                    data[\""""+self.extra+"""\"] = """+self.id+""".value();
                    
                    ajaxJson("doCancel","csrfmiddlewaretoken="+csrf_token+"&data="+JSON.stringify(data),function(resp)
                    {
                        var resp = new Response(resp);
                        if(resp.isError())
                        {
                            resp.showMessage();
                        }
                        else
                        {
                            resp.showMessage();
                            window.location.reload();
                        }
                    })
                })
            """)
        # print("AS")

    def defaultEditSubmit(self):
        ps = ""
        d = self
        formName = self.id

        # dataCode = ""
        # for dc in doc:
        #     dataCode = dataCode+"""
        #     """+dc.id+""".sync();
        #     data[\""""+dc.extra+"""\"]= """+dc.id+""".value();
        #     """
                
        
        d.postScript("""

        if(typeof("""+formName+""".table)!="undefined")
        {
            """+formName+""".table.className("table align-items-center table-flush");
        }
        
        


        var formFooter = new UIObject('#"""+formName+"""_footer');
        var submit = new UIObject("button",formFooter);
        submit.innerHTML("Save");
        submit.className("awgp-button awgp-whight");
        submit.onclick(function()
        {
            if("""+formName+""".checkMendetry()==false)
            {
                 return false;
            }
            """+formName+""".sync();
            var data = {};
            data[\""""+self.extra+"""\"] = """+formName+""".value();
            ajaxJson("edit/submit","csrfmiddlewaretoken="+csrf_token+"&data="+JSON.stringify(data),function(resp)
            {
                alert(resp.message[0].text);
               // window.location.reload();
            });
        })


        """)