from awgp.common.json import JSON



class JSONComplier:

    def parse(self,str):
        self.parm = JSON.fromString(str)

        self.input = []

    def loadFile(self,filename):
        file = open(filename,"r")
        self.parse(file.read())

    def getFromClause(self):
        output = ""
        for s in self.parm["source"]:
            # print(s)
            output += s["name"]+" "+s["id"]+","
        
        output = output.rstrip(",")
        return output

    def getSelectColumnName(self,s,alias=True,format=True):
        col = s["source"]+"."+s["id"]

        formatStr = ""
        if "format" in s and s["format"]!="":
            formatStr = ",'"+s["format"]+"'"
        
        out = ""            
        if format==True:
            if ("function" in s and s["function"]!=""):
                col = s["function"]+"("+col+formatStr+")"
            

        if "aggrigation" in s and s["aggrigation"]!="":
            col = s["aggrigation"]+"("+col+")"

        if alias==True:
            if "alias" in s and s["alias"] != "":
                out = col+" as "+s["alias"]
            else:
                if "function" in s and s["function"] != "":
                    out = col+" as "+s["id"]
                else:
                    if "aggrigation" in s and s["aggrigation"]!="":
                        out =  col+" as "+s["id"]
                    else:
                        out =  col
        else:
        
            return col
        return out

    def getSelectClause(self):
        output = ""
        
        
        for s in self.parm["fields"]:
            if s["exclude_field"] == False:
                output += self.getSelectColumnName(s)+","
            # print(s)
            if s["default_value"]!="":
                os = {
                    "join":"and",
                    "source":s["source"],
                    "source_field":s["id"],
                    "condition":"="
                }
                if "parameters" not in self.parm:
                    self.parm["parameters"] = []

                if self.parm["parameters"] == None:
                    self.parm["parameters"] = []
                self.parm["parameters"].append(os)

                if len(self.input)==0:
                    self.input.append({})
                self.input[0][s["source"]+"___"+s["id"]]=s["default_value"]
                
        
        
        output = output.rstrip(",")
        return output

    def getGroupByClause(self):
        output = ""
        aggFun = False
        aggFunList = ["sum","count","max","min","avrage"]
        for f in self.parm["fields"]:
            
            if f["exclude_field"] == False:
                if "aggrigation" in f and f["aggrigation"] != "":
                    if f["aggrigation"] in aggFunList:
                        aggFun = True
        if aggFun == True:
            for f in self.parm["fields"]:
                if f["exclude_field"] == False:
                    if "aggrigation" in f and f["aggrigation"]!="":
                        if f["aggrigation"] not in aggFunList:
                            output += self.getSelectColumnName(f,False)+","
                    else:
                        output += self.getSelectColumnName(f,False)+","
                
        output = output.rstrip(",")
        return output


    def getOrderByClause(self):
        output = ""
        for s in self.parm["fields"]:
            
            if "order_by" in s and s["order_by"]!="":
                if "order_on_value" in s and s["order_on_value"] == True:
                    output += self.getSelectColumnName(s,False,False)+" "+s["order_by"]+","
                else:
                    output += self.getSelectColumnName(s,False)+" "+s["order_by"]+","
        
        output = output.rstrip(",")
        return output

    def getSourceJoin(self):

        join = []
        # print(self.parm["source"])
        for s in self.parm["source"]:
            if "relation" in s:
                for j in s["relation"]:
                    
                    if "source_all" not in j:
                        j["source_all"] = False
                    
                    if "target_all" not in j:
                        j["target_all"] = False
                        
                    if "source_function" not in j:
                        j["source_function"] = ""
                        
                    if "target_function" not in j:
                        j["target_function"] = ""
                        
                    o = {"ls":j["source"],"lf":j["source_field"],"rs":s["id"],"rf":j["relate_with"],"join":j["join"],"condition":j["condition"],"source_all":j["source_all"],"target_all":j["target_all"],"source_function":j["source_function"],"target_function":j["target_function"]}
                    join.append(o)
        
        where = ""
        for j in join:
            sl = ""
            tl = ""
            sf = j["ls"]+"."+j["lf"]
            tf = j["rs"]+"."+j["rf"]
            # print(j)
            if "source_all" in j and j["source_all"]==True:
                sl = "(+)"
            
            if "target_all" in j and j["target_all"]==True:
                tl = "(+)"
                
            if "source_function" in j and j["source_function"]!="":
                sf = j["source_function"] + "("+sf+")"
                
            if "target_function" in j and j["target_function"]!="":
                tf = j["target_function"] + "("+tf+")"
            where += " "+j["join"]+" "+sf+sl+" "+j["condition"]+" "+tf+tl
        where = "1 = 1 "+where
        
        if len(self.input)>0:
            input = self.input[0]

            
            # print(self.parm["parameters"])
            for j in self.parm["parameters"]:
                # print(j)
                
                    
                    
                    # print(j)
                
                v = input[j["id"]]
                if "blank_wildcard" in j and j["blank_wildcard"]==True:
                    if v == "":
                        v = "%"
                if "parameter_function" in j and j["parameter_function"] != "":
                    
                    if "type" in j and j["type"] == "Date":
                        v = j["parameter_function"]+f"(to_date('{v}','yyyy-mm-dd'))"
                    else:
                        if "parameter_format" in j and j["parameter_format"] != "":
                            vf = j["parameter_format"]
                            v = j["parameter_function"]+f"('{v}','{vf}')"
                        else:
                            v = j["parameter_function"]+f"('{v}')"
                        # print(v)
                else:
                    v = f"'{v}'"
                    
                
                # print(j)
                if "valueFunction" in j and j["valueFunction"]!="":
                    where += " "+j["join"]+" "+j["valueFunction"]+"("+j["source"]+"."+j["source_field"]+") "+j["condition"]+" "+"{val}".format(val=v)
                else:
                    if "blank_wildcard" in j and j["blank_wildcard"]==True and v == "'%'":
                        where += " "+j["join"]+" ("+j["source"]+"."+j["source_field"]+" "+j["condition"]+" "+f" {v} or "+j["source"]+"."+j["source_field"]+" is null)"
                    else:
                        
                        where += " "+j["join"]+" "+j["source"]+"."+j["source_field"]+" "+j["condition"]+" "+"{val}".format(val=v)
        # print(where)
        return where

    def parameterValue(self,input):
        self.input = input
        
        # return output

    def getSql(self):
        fromClause = self.getFromClause()
        selectClause = self.getSelectClause()
        # print(selectClause)
        whereClause = self.getSourceJoin()

        orderByClause = self.getOrderByClause()
        if orderByClause != "":
            orderByClause = "order by "+orderByClause

        groupByClause = self.getGroupByClause()
        if groupByClause!="":
            groupByClause = "group by "+groupByClause

        sql = "select {select} from {fromC} where {where} {groupby} {orderby}".format(select=selectClause,fromC=fromClause,where=whereClause,orderby=orderByClause,groupby=groupByClause)

        # print(sql)
        return sql


    def getReportStructure(self):
        out = []
        showSummery = False
        for f in self.parm["fields"]:
            if f["summery"]!="":
                showSummery = True
            if "alias" in f and f["alias"]!="":
                f["id"] = f["alias"]
            if "style" in f and f["style"]!="":
                f["style"] = JSON.fromString(f["style"])

            
            if f["type"] == "Link":
                f["property"] = {"href":"javascript:"}
            
            if "query_parameter" not in f:
                f["query_parameter"] = ""

            if "report_id" not in f:
                f["report_id"] = ""

            if "bind_only" not in f:
                f["bind_only"] = ""


            # if "query_parameter" in f:


            if f["exclude_field"]==False:
                out.append(f)
        
        mode = "table"
        showSerial = True
        chartType="bar"
        if self.parm["layout"]=="grid":
            mode="table"
        elif self.parm["layout"]=="chartbar":
            mode="chart"
            chartType="bar"
            showSerial=False
        elif self.parm["layout"]=="chartline":
            mode="chart"
            chartType="line"
            showSerial=False
        elif self.parm["layout"]=="chartpi":
            mode="chart"
            chartType="pie"
            showSerial=False
        elif self.parm["layout"]=="chartdoughnu":
            mode="chart"
            chartType="doughnut"
            showSerial=False
        elif self.parm["layout"]=="chartpoler":
            mode="chart"
            chartType="polarArea"
            showSerial=False
        elif self.parm["layout"]=="chartredar":
            mode="chart"
            chartType="radar"
            showSerial=False
        elif self.parm["layout"]=="chartbubble":
            mode="chart"
            chartType="bubble"
            showSerial=False
        structuer = {
            "id":"reportData",
            "name":"",
            "mode":mode,
            "isEditable":True,
            "isSubmitable":False,
            "showSummery":showSummery,
            "showSerial":showSerial,
            "fields":out,
            "chartType":chartType
        }
        return structuer
        
    