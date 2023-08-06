import flashtext
from nebula.graph import ttypes,GraphService
from nebula.ConnectionPool import ConnectionPool
from nebula.Client import GraphClient
from maintain_PlatoUtils.maintain_PlatoUtils import wrapNebula2Df

class SimpleRelationRecognizer(flashtext.KeywordProcessor):
    
    def __init__(self,gHost, gPort,gUser,gPassword,gDBName,*args,**kwargs):
        super(SimpleRelationRecognizer, self).__init__()
        connection_pool = ConnectionPool(gHost, gPort,network_timeout=60000)
        self.gClient = GraphClient(connection_pool)
        self.gClient.authenticate(gUser,gPassword)
        self.gClient.execute_query("USE {}".format(gDBName))
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
                    self.add_keyword(entityNameItem,(entityNameItem,nodeType,indexAttrName))
                
    def relationRecognizer(self,text):
        return self.extract_keywords(text)
        
    
if __name__=="__main__":
    
    gHost="9.135.95.249"
    gPort=13708
    gUser="root"
    gPassword="nebula"
    gDBName="post_skill_school_ianxu"

    mySimpleRelationRecognizer=SimpleRelationRecognizer(gHost,gPort,gUser,gPassword,gDBName)
    kwList=mySimpleRelationRecognizer.relationRecognizer("JAVA 是一门编程语言，经常用于后台开发")
    print(kwList)