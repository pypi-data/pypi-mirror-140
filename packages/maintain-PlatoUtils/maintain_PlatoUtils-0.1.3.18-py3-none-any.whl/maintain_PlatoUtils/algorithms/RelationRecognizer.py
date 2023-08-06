import flashtext
import tqdm
import pandas as pd
from nebula.graph import ttypes,GraphService
from nebula.ConnectionPool import ConnectionPool
from nebula.Client import GraphClient
from maintain_PlatoUtils.maintain_PlatoUtils import wrapNebula2Df
import json

class SimpleRelationRecognizer(flashtext.KeywordProcessor):
    
    def __init__(self,gHost, gPort,gUser,gPassword,gDBName,*args,**kwargs):
        super(SimpleRelationRecognizer, self).__init__()
        connection_pool = ConnectionPool(gHost, gPort,network_timeout=60000)
        self.gClient = GraphClient(connection_pool)
        self.gClient.authenticate(gUser,gPassword)
        self.gClient.execute_query("USE {}".format(gDBName))
        edgeTypeDf=wrapNebula2Df(self.gClient.execute_query("SHOW EDGES"))
        self.edgeTypeList=edgeTypeDf["Name"].values.tolist()
        self.entityAttrDict={}
        self.buildEntityKWProcessor()
        
    def buildEntityKWProcessor(self):
        
        tagDf=wrapNebula2Df(self.gClient.execute_query("SHOW TAGS"))
        tagList=tagDf["Name"].values.flatten().tolist()
        
        indexDf=wrapNebula2Df(self.gClient.execute_query("SHOW TAG INDEXES"))
        indexList=indexDf["Index Name"].values.flatten().tolist()
        
        entityNameTypeDict={}
        for indexItem in tqdm.tqdm(indexList,desc="loading entities"):
            nodeType=indexItem.split("_")[0]
            indexInfoDf=wrapNebula2Df(self.gClient.execute_query("DESCRIBE TAG INDEX {}".format(indexItem)))
            indexAttrName=indexInfoDf["Field"].values.flatten().tolist()[0]
            nodeInfoDf=wrapNebula2Df(self.gClient.execute_query("LOOKUP ON {nodeType} WHERE {nodeType}.{indexAttrName}!='不可能的名字' \
                                                                    YIELD {nodeType}.{indexAttrName} AS {nodeType}{indexAttrName}".format(nodeType=nodeType,
                                                                                                                                            indexAttrName=indexAttrName)))
            dfIndexAttrName="{}{}".format(nodeType,indexAttrName)
            
            if nodeInfoDf.shape[0]>0:
                enitityNameList=nodeInfoDf[dfIndexAttrName].values.flatten().tolist()
                for entityNameItem in enitityNameList:
                    self.entityAttrDict[entityNameItem]=self.entityAttrDict.get(entityNameItem,[])+[(entityNameItem,nodeType,indexAttrName)]
                    self.add_keyword(entityNameItem)
                
    def relationRecognize(self,text):
        entityList=self.extract_keywords(text)
        relDfList=[]
        for edgeTypeItem in self.edgeTypeList:
            queryStrList=[]
            for entity1I in range(len(entityList)):
                entity1AttrGroup=self.entityAttrDict[entityList[entity1I]]
                for entity1AttrI in range(len(entity1AttrGroup)):
                    for entity2I in range(len(entityList)):
                        entity2AttrGroup=self.entityAttrDict[entityList[entity2I]]
                        for entity2AttrI in range(len(entity2AttrGroup)):
                            
                            entity1=entityList[entity1I]
                            headIdVal=self.entityAttrDict[entity1][entity1AttrI][0]
                            headType=self.entityAttrDict[entity1][entity1AttrI][1]
                            headIdAttrName=self.entityAttrDict[entity1][entity1AttrI][2]
                            
                            entity2=entityList[entity2I]
                            tailIdVal=self.entityAttrDict[entity2][entity2AttrI][0]
                            tailType=self.entityAttrDict[entity2][entity2AttrI][1]
                            tailIdAttrName=self.entityAttrDict[entity2][entity2AttrI][2]
                            
                            queryStrItem="LOOKUP ON {headType} WHERE {headType}.{headIdAttrName}=='{headIdVal}'|\
                                        GO FROM $-.VertexID OVER {edgeType} \
                                            WHERE $$.{tailType}.{tailIdAttrName}=='{tailIdVal}'\
                                                YIELD $^.{headType}.{headIdAttrName} AS headIdVal,\
                                                    $$.{tailType}.{tailIdAttrName} AS tailIdVal,\
                                                        '{edgeType}' AS edgeType".format(
                                                                                        headType=headType,
                                                                                        headIdAttrName=headIdAttrName,
                                                                                        headIdVal=headIdVal,
                                                                                        edgeType=edgeTypeItem,
                                                                                        tailType=tailType,
                                                                                        tailIdAttrName=tailIdAttrName,
                                                                                        tailIdVal=tailIdVal
                                                                                    )
                            queryStrList.append(queryStrItem)
            queryStr=" UNION ".join(queryStrList)
            queryDfItem=wrapNebula2Df(self.gClient.execute_query(queryStr))
            if queryDfItem.shape[0]>0:
                relDfList.append(queryDfItem)
            relDf=pd.concat(relDfList)
        return entityList,json.loads(relDf.to_json(orient="records"))
    
if __name__=="__main__":
    
    gHost="9.135.95.249"
    gPort=13708
    gUser="root"
    gPassword="nebula"
    gDBName="post_skill_school_ianxu"

    mySimpleRelationRecognizer=SimpleRelationRecognizer(gHost,gPort,gUser,gPassword,gDBName)
    kwList=mySimpleRelationRecognizer.relationRecognize("JAVA 是一门编程语言，经常用于后台开发")
    print(kwList)