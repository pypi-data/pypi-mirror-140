from nebula.graph import ttypes,GraphService
from nebula.ConnectionPool import ConnectionPool
from nebula.Client import GraphClient
# from maintain_PlatoUtils.maintain_PlatoUtils import wrapNebula2Df
from maintain_PlatoUtils import wrapNebula2Df
import tqdm
from typing import Callable, Any, Iterable
import traceback

class NodeInfo:
    def __init__(self,nodeType,nodeIdAttr,nodeIdVal=None):
        self.nodeType=nodeType
        self.nodeIdAttr=nodeIdAttr
        self.nodeIdVal=nodeIdVal
        self.nodeInfo=self.__dict__
        
        
class EdgeInfo:
    def __init__(self,edgeType,direct="",**edgeAttrKWargs):
        self.edgeType=edgeType
        self.edgeAttrDict=edgeAttrKWargs
        self.edgeInfo={
            "edgeType":edgeType,
            "direct":direct,
            **edgeAttrKWargs
        }
        
class RDFInfo:
    def __init__(self,head:NodeInfo,edge:EdgeInfo,tail:NodeInfo):
        self.head=head
        self.edge=edge
        self.tail=tail

class GraphWrapClient:
    
    def __init__(self,gHost,gPort,gUser,gPassword,gDbName=""):
        '''初始化gClient'''
        Connection_pool = ConnectionPool(gHost, gPort,network_timeout=300000)
        self.gClient = GraphClient(Connection_pool)
        self.gClient.authenticate(gUser, gPassword)
        
        if len(gDbName)>0:
            self.gClient.execute_query("USE {}".format(gDbName))
            self.setGDbName(gDbName)
        
    def setGDbName(self,gDbName):
        '''设定图空间'''
        self.gClient.execute_query("USE {}".format(gDbName))
        self.gClient.set_space(gDbName)
        return self
        
    def execute_query(self,queryStr):
        '''query操作'''
        queryReq=self.gClient.execute_query(queryStr)
        reqDf=None
        if queryReq.error_code==0 and queryReq.rows is not None:
            reqDf=wrapNebula2Df(queryReq)
        return queryReq,reqDf
    
    def delVertex(self,sysIdList,delRel=True):
        '''（关联）删除节点'''
        errCode=0
        if delRel==True:
            showEdgeReq=self.gClient.execute_query("SHOW EDGES")
            errCode+=showEdgeReq.error_code
            
            relDf=wrapNebula2Df(showEdgeReq)
            if relDf.shape[0]>0:
                relList=relDf["Name"].values.flatten().tolist()
                for relItem in tqdm.tqdm(relList,desc="del edges with vertexes"):
                    for srcSysIdItem in tqdm.tqdm(sysIdList,desc="del srcs from edges with vertexes"):
                        relTailStr="GO FROM {srcSysId} OVER {edgeName} BIDIRECT YIELD {edgeName}._dst AS tgtSysId".format(
                            srcSysId=srcSysIdItem,
                            edgeName=relItem)
                        # print(relTailStr)
                        relTailReq=self.gClient.execute_query(relTailStr)
                        errCode+=relTailReq.error_code
                        relTailSysIdDf=wrapNebula2Df(relTailReq)
                        if relTailSysIdDf.shape[0]>0:
                            relTailSysIdList=relTailSysIdDf["tgtSysId"].values.flatten().tolist()
                            delOrderGroupStr=",".join(["{}->{}".format(srcSysIdItem,tailSysIdItem) for tailSysIdItem in relTailSysIdList])
                            delReverseGroupStr=",".join(["{}->{}".format(tailSysIdItem,srcSysIdItem) for tailSysIdItem in relTailSysIdList])
                            delGroupStr=",".join([delOrderGroupStr,delReverseGroupStr])
                            delStr="DELETE EDGE {} {}".format(relItem,delGroupStr)
                            # print(delStr)
                            delReq=self.gClient.execute_query(delStr)
                            errCode+=delReq.error_code
        return {"error_code":errCode}
        
        
class GraphWrapQuery:
    
    def __init__(self):
        self.yieldAttrList=[]
        self.yieldSysIdList=[]
    
    def singleSearchFunc_wait(self,hetDict,head=True,singleYieldList={}):
        args=[hetDict]
        kwargs={
            "head":head,
            "singleYieldList":singleYieldList
        }
        return self.singleSearchFunc,args,kwargs
    
    def singleSearchFunc(self,hetDict,head=True,singleYieldList={}):
        '''
        direction: 默认单项
        '''
        
        singleQueryStrList=[]
        
        if type(hetDict)==dict:
            headInfo=hetDict.get("head",{})
            edgeInfo=hetDict.get("edge",{})
            tailInfo=hetDict.get("tail",{})
        elif type(hetDict)==RDFInfo:
            headInfo,edgeInfo,tailInfo=hetDict.head.nodeInfo,hetDict.edge.edgeInfo,hetDict.tail.nodeInfo
        elif type(hetDict)==NodeInfo:
            headInfo=hetDict.nodeInfo
            edgeInfo={}
            tailInfo={}
        
        if "direct" not in edgeInfo:
            edgeInfo["direct"]=""
        
        singleYieldDict={}
        if len(singleYieldList)>0:
            for nodeTypeAttrItem in singleYieldList:
                singleYieldDict[nodeTypeAttrItem["nodeType"]]=singleYieldDict.get(nodeTypeAttrItem["nodeType"],[])+[nodeTypeAttrItem["nodeAttr"]]
        
        # LOOKUP语句构建
        if head==True:  
            singleQueryStrList=["LOOKUP ON {nodeType} WHERE {nodeType}.{nodeIdAttr}=='{nodeIdVal}'|\
                                        YIELD $-.VertexID AS src{nodeType}SysId".format(
                                                                                            nodeType=headInfo["nodeType"],
                                                                                            nodeIdAttr=headInfo["nodeIdAttr"],
                                                                                            nodeIdVal=headInfo["nodeIdVal"]
                                                                                        )]
            srcSysIdName="src{}SysId".format(headInfo["nodeType"])
            self.yieldSysIdList.append(srcSysIdName)
        
        # yield语句初始化
        yieldAttrList=[]
        pureAttrYieldList=[]
        for singleYieldTypeKey in singleYieldDict:
            for singleYieldAttrVal in singleYieldDict[singleYieldTypeKey]:
                nodeType=singleYieldTypeKey
                nodeAttr=singleYieldAttrVal
                nodeTypeAttrName="{nodeType}{nodeAttr}".format(nodeType=nodeType,
                                                            nodeAttr=nodeAttr)
                if nodeTypeAttrName not in self.yieldAttrList:
                    if len(headInfo)>0 and headInfo["nodeType"]==singleYieldTypeKey:
                        yieldAttrList.append("$^.{nodeType}.{nodeAttr} AS {nodeType}{nodeAttr}".format(nodeType=nodeType,
                                                                                                    nodeAttr=nodeAttr))
                        if nodeTypeAttrItem not in self.yieldAttrList:
                            pureAttrYieldList.append(nodeTypeAttrName)
                    if len(edgeInfo)>0 and tailInfo["nodeType"]==singleYieldTypeKey:
                        yieldAttrList.append("$$.{nodeType}.{nodeAttr} AS {nodeType}{nodeAttr}".format(nodeType=nodeType,
                                                                                                    nodeAttr=nodeAttr))
                        if nodeTypeAttrItem not in self.yieldAttrList:
                            pureAttrYieldList.append(nodeTypeAttrName)
                        
        oldYieldAttrList=[]
        for yieldAttrItem in self.yieldAttrList:
            oldYieldAttrList.append("$-.{oldYieldAttr} AS {oldYieldAttr}".format(oldYieldAttr=yieldAttrItem))
        yieldAttrListStr=""
        if len(yieldAttrList)>0:
            yieldAttrListStr=","+",".join(yieldAttrList+oldYieldAttrList)

        yieldSysIdList=["$-.{yieldSysId} AS {yieldSysId}".format(yieldSysId=yieldSysIdItem) for yieldSysIdItem in self.yieldSysIdList]
        yieldSysIdListStr=""
        if len(yieldSysIdList)>0:
            yieldSysIdListStr=","+",".join(yieldSysIdList) 
        
        # GO语句构建-WHERE语句
        
        
        # GO语句构建-完整化
        if len(edgeInfo)>0:
            # RDF搜索
            if len(tailInfo)>0:
                startSysId=self.yieldSysIdList[-1]
                singleQueryStrList.append("GO FROM $-.{startSysId} OVER {edgeType} {direct} YIELD {edgeType}._dst AS tgt{nodeType}SysId {yieldList}{yieldAttrList}".format(
                                                        startSysId=startSysId,
                                                        edgeType=edgeInfo["edgeType"],
                                                        direct=edgeInfo["direct"],
                                                        nodeType=tailInfo["nodeType"],
                                                        yieldList=yieldSysIdListStr,
                                                        yieldAttrList=yieldAttrListStr
                                                    ))
            else:
                singleQueryStrList.append("GO FROM $-.VertexID OVER {edgeType} {direct} YIELD {edgeType}._dst AS tgt{nodeType}SysId {yieldList}{yieldAttrList}".format(
                                                        edgeType=edgeInfo["edgeType"],
                                                        direct=edgeInfo["direct"],
                                                        nodeType=tailInfo["nodeType"],
                                                        yieldList=yieldSysIdListStr,
                                                        yieldAttrList=yieldAttrListStr
                                                    ))
        
            # 整理新的yield列表
            tgtSysIdName="tgt{}SysId".format(tailInfo["nodeType"])
            self.yieldSysIdList.append(tgtSysIdName)
            self.yieldAttrList+=pureAttrYieldList
            # self.yieldAttrList=list(set(self.yieldAttrList))
        else:
            # 单节点搜索
            fetchStr="FETCH PROP ON {nodeType} $-.{srcSysID}".format(nodeType=headInfo["nodeType"],srcSysID=srcSysIdName)
            singleQueryStrList.append(fetchStr)
            
        
        totalQuery="|".join(singleQueryStrList)
        
        return totalQuery
            
    def intersectSearchFunc_wait(self,*queryList):
        return self.intersectSearchFunc,queryList
        
    def intersectSearchFunc(self,*queryFuncList):
        tmpQueryStrList=[]
        for queryFuncGroupItem in queryFuncList:
            self.yieldSysIdList=[]
            self.yieldAttrList=[]
            if type(queryFuncGroupItem)==str:
                # 返回query
                queryItem=queryFuncGroupItem
            else:
                # 返回函数
                if len(queryFuncGroupItem)==3:
                    queryFunc,args,kwargs=queryFuncGroupItem
                    queryItem=queryFunc(*args,**kwargs)
                else:
                    queryFunc,args=queryFuncGroupItem
                    queryItem=queryFunc(*args)
            tmpQueryStrList.append("({})".format(queryItem))
        queryStr=" INTERSECT ".join(tmpQueryStrList)
        return queryStr
              
    def unionSearchFunc_wait(self,*queryList):
        return self.unionSearchFunc,queryList
        
    def unionSearchFunc(self,*queryFuncList):
        tmpQueryStrList=[]
        for queryFuncGroupItem in queryFuncList:
            self.yieldSysIdList=[]
            self.yieldAttrList=[]
            if type(queryFuncGroupItem)==str:
                queryItem=queryFuncGroupItem
            else:
                if len(queryFuncGroupItem)==3:
                    queryFunc,args,kwargs=queryFuncGroupItem
                    queryItem=queryFunc(*args,**kwargs)
                else:
                    queryFunc,args=queryFuncGroupItem
                    queryItem=queryFunc(*args)
            tmpQueryStrList.append("({})".format(queryItem))
        queryStr=" UNION ".join(tmpQueryStrList)
        return queryStr
        
    def seqSearchFunc_wait(self,*queryList):
        for queryItem in queryList[1:]:
            queryItem[2]["head"]=False
        return self.seqSearchFunc,queryList
        
    def seqSearchFunc(self,*queryGroupList):
        '''第一个singleFunc的head为True'''
        tmpQueryStrList=[]
        for queryGroupItem in queryGroupList:
            
            if type(queryGroupItem)==str:
                queryItem=queryGroupItem
            else:
                if len(queryGroupItem)==3:
                    queryFuncItem,args,kwargs=queryGroupItem
                    queryItem=queryFuncItem(*args,**kwargs)
                else:
                    queryFuncItem,args=queryGroupItem
                    queryItem=queryFuncItem(*args)
                
            tmpQueryStrList.append(queryItem)
        queryStr="|".join(tmpQueryStrList)
        return queryStr
        
    def renew(self):
        self.yieldAttrList=[]
        self.yieldSysIdList=[]
        
    def runWaitFunc(self,waitFuncGroupList,maxLayer=0):
        if type(waitFuncGroupList)==list or type(waitFuncGroupList)==dict:
            return waitFuncGroupList
        typeList=[type(waitFuncGroupItem).__name__ for waitFuncGroupItem in waitFuncGroupList]
        typeSetList=list(set(typeList))
        if "str" not in typeList:
            if type(waitFuncGroupList[0]).__name__=="method":
                if waitFuncGroupList[0].__name__=="singleSearchFunc":
                    print("singleSearchFunc")
                    if maxLayer==0:
                        returnVal=waitFuncGroupList[0](*self.runWaitFunc(waitFuncGroupList[1],maxLayer=maxLayer+1))
                        return returnVal
                    else:
                        return waitFuncGroupList
                elif waitFuncGroupList[0].__name__=="seqSearchFunc":
                    print("seqSearchFunc")
                    returnVal=waitFuncGroupList[0](*self.runWaitFunc(waitFuncGroupList[1],maxLayer=maxLayer+1))
                    return returnVal
                elif waitFuncGroupList[0].__name__=="unionSearchFunc":
                    print("unionSearchFunc")
                    returnVal=waitFuncGroupList[0](*self.runWaitFunc(waitFuncGroupList[1],maxLayer=maxLayer+1))
                    return returnVal
                elif waitFuncGroupList[0].__name__=="intersectSearchFunc":
                    print("intersectSearchFunc")
                    returnVal=waitFuncGroupList[0](*self.runWaitFunc(waitFuncGroupList[1],maxLayer=maxLayer+1))
                    return returnVal
                
                
                # if type(waitFuncGroupList[1])==tuple:
                #     try:
                #         return waitFuncGroupList[0](*self.runWaitFunc(waitFuncGroupList[1]))
                #     except Exception as ex:
                #         traceback.print_exc()
                #         print(ex)
                # else:
                #     try:
                #         return waitFuncGroupList[0](*self.runWaitFunc(waitFuncGroupList[1]),**self.runWaitFunc(waitFuncGroupList[2]))
                #     except Exception as ex:
                #         traceback.print_exc()
                #         print(ex)
            # elif len(typeSetList)==1 and typeSetList[0]=="tuple":
            #     returnVal=[self.runWaitFunc(waitFuncGroupItem) for waitFuncGroupItem in waitFuncGroupList]
            #     return returnVal
            else:
                return waitFuncGroupList
            
    def transMethod(self,methodName):
        if methodName=="singleSearch":
            return self.singleSearchFunc_wait
        elif methodName=="seqSearch":
            return self.seqSearchFunc_wait
        elif methodName=="unionSearch":
            return self.unionSearchFunc_wait
        elif methodName=="intersectSearch":
            return self.intersectSearchFunc_wait
            
    def wrapJson2Query(self,myQueryJson):
        if myQueryJson["searchMethod"] in ["seqSearch","unionSearch","intersectSearch"]:
            searchMethod=self.transMethod(myQueryJson["searchMethod"])
            searchFrameList=myQueryJson["searchFrame"]
            return searchMethod(*[self.wrapJson2Query(searchFrameItem) for searchFrameItem in searchFrameList])
        if myQueryJson["searchMethod"] in ["singleSearch"]:
            searchMethod=self.transMethod(myQueryJson["searchMethod"])
            searchFrameDict=myQueryJson["searchFrame"]
            searchFrameDict["singleYieldList"]=searchFrameDict.get("singleYieldList",{})
            return searchMethod(searchFrameDict,singleYieldList=searchFrameDict["singleYieldList"])
            
        
if __name__=="__main__":
    
    gHost="9.135.95.249"
    gPort=13708
    gUser="root"
    gPassword="nebula"
    gDbName="company_product_field_musklin"

    myGClient=GraphWrapClient(gHost,gPort,gUser,gPassword,gDbName=gDbName)
    myGQuery=GraphWrapQuery()
    
    # # single vertex search with singleSearch
    # queryStr=myGQuery.singleSearchFunc(NodeInfo("Company","CompanyName",nodeIdVal="深圳市腾讯计算机系统有限公司"),
    #                                singleYieldList=[{"nodeType":"Company","nodeAttr":"CompanyName"}])
    # myGQuery.renew()
    
    # # singleSearch
    # queryStr=myGQuery.singleSearchFunc(RDFInfo(NodeInfo("Company","CompanyName",nodeIdVal="深圳市腾讯计算机系统有限公司"),
    #                                        EdgeInfo("produce"),
    #                                        NodeInfo("Product","ProductName",nodeIdVal=None)),
    #                                singleYieldList=[{"nodeType":"Company","nodeAttr":"CompanyName"},
    #                                                 {"nodeType":"Product","nodeAttr":"ProductName"}])
    # myGQuery.renew()
    
    # # seqSearch
    # queryStr=myGQuery.seqSearchFunc(
    #     myGQuery.singleSearchFunc_wait(RDFInfo(NodeInfo("Company","CompanyName",nodeIdVal="深圳市腾讯计算机系统有限公司"),
    #                                        EdgeInfo("produce"),
    #                                        NodeInfo("Product","ProductName",nodeIdVal=None)),
    #                                singleYieldList=[{"nodeType":"Company","nodeAttr":"CompanyName"},
    #                                                 {"nodeType":"Product","nodeAttr":"ProductName"}]),
    #     myGQuery.singleSearchFunc_wait(RDFInfo(NodeInfo("Product","ProductName",nodeIdVal=None),
    #                                        EdgeInfo("belongTo"),
    #                                        NodeInfo("Field","FieldName",nodeIdVal=None)),
    #                                singleYieldList=[{"nodeType":"Product","nodeAttr":"ProductName"},
    #                                                 {"nodeType":"Field","nodeAttr":"FieldName"}],
    #                                head=False)
    # )
    # myGQuery.renew()
    
    # # unionSearch
    # queryStr=myGQuery.unionSearchFunc(
    #     myGQuery.singleSearchFunc_wait(RDFInfo(NodeInfo("Company","CompanyName",nodeIdVal="深圳市腾讯计算机系统有限公司"),
    #                                         EdgeInfo("produce"),
    #                                         NodeInfo("Product","ProductName",nodeIdVal=None)),
    #                                 singleYieldList=[{"nodeType":"Company","nodeAttr":"CompanyName"},
    #                                                 {"nodeType":"Product","nodeAttr":"ProductName"}]),
    #     myGQuery.singleSearchFunc_wait(RDFInfo(NodeInfo("Company","CompanyName",nodeIdVal="国泰君安期货有限公司"),
    #                                         EdgeInfo("produce"),
    #                                         NodeInfo("Product","ProductName",nodeIdVal=None)),
    #                                 singleYieldList=[{"nodeType":"Company","nodeAttr":"CompanyName"},
    #                                                 {"nodeType":"Product","nodeAttr":"ProductName"}])
    # )
    # myGQuery.renew()
    
    # # union+seqSearch
    # queryFunc=myGQuery.unionSearchFunc_wait(
    #     myGQuery.seqSearchFunc_wait(
    #         myGQuery.singleSearchFunc_wait(RDFInfo(NodeInfo("Company","CompanyName",nodeIdVal="深圳市腾讯计算机系统有限公司"),
    #                                         EdgeInfo("produce"),
    #                                         NodeInfo("Product","ProductName",nodeIdVal=None)),
    #                                 singleYieldList=[{"nodeType":"Company","nodeAttr":"CompanyName"},
    #                                                     {"nodeType":"Product","nodeAttr":"ProductName"}]),
    #         myGQuery.singleSearchFunc_wait(RDFInfo(NodeInfo("Product","ProductName",nodeIdVal=None),
    #                                         EdgeInfo("belongTo"),
    #                                         NodeInfo("Field","FieldName",nodeIdVal=None)),
    #                                 singleYieldList=[{"nodeType":"Product","nodeAttr":"ProductName"},
    #                                                     {"nodeType":"Field","nodeAttr":"FieldName"}],
    #                                 head=False)
    #     ),
    #     myGQuery.seqSearchFunc_wait(
    #         myGQuery.singleSearchFunc_wait(RDFInfo(NodeInfo("Company","CompanyName",nodeIdVal="阿里巴巴"),
    #                                         EdgeInfo("produce"),
    #                                         NodeInfo("Product","ProductName",nodeIdVal=None)),
    #                                 singleYieldList=[{"nodeType":"Company","nodeAttr":"CompanyName"},
    #                                                     {"nodeType":"Product","nodeAttr":"ProductName"}]),
    #         myGQuery.singleSearchFunc_wait(RDFInfo(NodeInfo("Product","ProductName",nodeIdVal=None),
    #                                         EdgeInfo("belongTo"),
    #                                         NodeInfo("Field","FieldName",nodeIdVal=None)),
    #                                 singleYieldList=[{"nodeType":"Product","nodeAttr":"ProductName"},
    #                                                     {"nodeType":"Field","nodeAttr":"FieldName"}],
    #                                 head=False)
    #     )
    # )
    # myGQuery.renew()
    
    # # intersect+seqSearch
    # queryFunc=myGQuery.intersectSearchFunc_wait(
    #     myGQuery.seqSearchFunc_wait(
    #         myGQuery.singleSearchFunc_wait(RDFInfo(NodeInfo("Company","CompanyName",nodeIdVal="深圳市腾讯计算机系统有限公司"),
    #                                         EdgeInfo("produce"),
    #                                         NodeInfo("Product","ProductName",nodeIdVal=None)),
    #                                 singleYieldList=[{"nodeType":"Company","nodeAttr":"CompanyName"},
    #                                                     {"nodeType":"Product","nodeAttr":"ProductName"}]),
    #         myGQuery.singleSearchFunc_wait(RDFInfo(NodeInfo("Product","ProductName",nodeIdVal=None),
    #                                         EdgeInfo("belongTo"),
    #                                         NodeInfo("Field","FieldName",nodeIdVal=None)),
    #                                 singleYieldList=[{"nodeType":"Product","nodeAttr":"ProductName"},
    #                                                     {"nodeType":"Field","nodeAttr":"FieldName"}],
    #                                 head=False)
    #     ),
    #     myGQuery.seqSearchFunc_wait(
    #         myGQuery.singleSearchFunc_wait(RDFInfo(NodeInfo("Company","CompanyName",nodeIdVal="阿里巴巴"),
    #                                         EdgeInfo("produce"),
    #                                         NodeInfo("Product","ProductName",nodeIdVal=None)),
    #                                 singleYieldList=[{"nodeType":"Company","nodeAttr":"CompanyName"},
    #                                                     {"nodeType":"Product","nodeAttr":"ProductName"}]),
    #         myGQuery.singleSearchFunc_wait(RDFInfo(NodeInfo("Product","ProductName",nodeIdVal=None),
    #                                         EdgeInfo("belongTo"),
    #                                         NodeInfo("Field","FieldName",nodeIdVal=None)),
    #                                 singleYieldList=[{"nodeType":"Product","nodeAttr":"ProductName"},
    #                                                     {"nodeType":"Field","nodeAttr":"FieldName"}],
    #                                 head=False)
    #     )
    # )
    # myGQuery.renew()
    
    # wrapJson2Qeury-1
    queryJson={
            "searchMethod":"seqSearch",
            "searchFrame":[
                {
                    "searchMethod":"singleSearch",
                    "searchFrame":{
                        "head":{
                            "nodeType":"Company",
                            "nodeIdAttr":"CompanyName",
                            "nodeIdVal":"深圳市腾讯计算机系统有限公司"
                        },
                        "edge":{
                            "edgeType":"produce"
                        },
                        "tail":{
                            "nodeType":"Product",
                            "nodeIdAttr":"ProductName",
                            "nodeIdVal":None
                        },
                        "singleYieldList":[
                            {"nodeType":"Company","nodeAttr":"CompanyName"},
                            {"nodeType":"Product","nodeAttr":"ProductName"}
                        ]
                    }
                },{
                    "searchMethod":"singleSearch",
                    "searchFrame":{
                        "head":{
                            "nodeType":"Product",
                            "nodeIdAttr":"ProductName",
                            "nodeIdVal":None
                        },
                        "edge":{
                            "edgeType":"belongTo"
                        },
                        "tail":{
                            "nodeType":"Field",
                            "nodeIdAttr":"FieldName",
                            "nodeIdVal":None
                        },
                        "singleYieldList":[
                            {"nodeType":"Company","nodeAttr":"CompanyName"},
                            {"nodeType":"Product","nodeAttr":"ProductName"},
                            {"nodeType":"Field","nodeAttr":"FieldName"}
                        ]
                    }
                }
            ]
        }
    queryFunc=myGQuery.wrapJson2Query(queryJson)
    queryStr=myGQuery.runWaitFunc(queryFunc)
    
    # # wrapJson2Qeury-2
    # queryJson={
    #                 "searchMethod":"singleSearch",
    #                 "searchFrame":{
    #                     "head":{
    #                         "nodeType":"Company",
    #                         "nodeIdAttr":"CompanyName",
    #                         "nodeIdVal":"深圳市腾讯计算机系统有限公司"
    #                     },
    #                     "edge":{
    #                         "edgeType":"produce"
    #                     },
    #                     "tail":{
    #                         "nodeType":"Product",
    #                         "nodeIdAttr":"ProductName",
    #                         "nodeIdVal":None
    #                     },
    #                     "singleYieldList":[
    #                         {"nodeType":"Company","nodeAttr":"CompanyName"},
    #                         {"nodeType":"Product","nodeAttr":"ProductName"}
    #                     ]
    #                 }
    #             }
    # queryFunc=myGQuery.wrapJson2Query(queryJson)
    # queryStr=myGQuery.runWaitFunc(queryFunc)
    
    
    print(queryStr)
    print(123)
    # queryReq,queryDf=myGClient.execute_query("INSERT VERTEX hv1NodeType(headIdAttr) VALUES uuid('hv1NodeType_7'):(7)")
    # myGClient.singleFunc(hetDict=)