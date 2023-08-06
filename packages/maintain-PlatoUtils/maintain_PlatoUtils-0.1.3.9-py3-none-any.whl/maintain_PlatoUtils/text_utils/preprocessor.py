from string import punctuation
import re
# from stopwords import stopwordList
from maintain_PlatoUtils.text_utils.stopwords import stopwordList

def preprocessSentence(mySentence,methods="lnps",stopwords=[],tabuList=["2d","3d"]):
    '''
    预处理句子，并分词
    methods:
    l-lower:小写字母
    n-num:替换数字为num
    p-punctuation:删除标点符号
    s-stopwords:删除停止词
    '''
    tabuTokenList=[tokenItem for tabuItem in tabuList for tokenItem in tabuItem]
    totalStopWordList=stopwordList
    totalStopWordList+=stopwords
    mySentence=mySentence.strip()
    puncStr=punctuation+"「」（）？！?!<>《》、“”。，：♫︰【】—；："
    
    tabuListStr="|".join(tabuList)
    mySentence=re.sub("({})+".format(tabuListStr),r" \1 ",mySentence)
    
    if "l" in methods:
        mySentence=mySentence.lower()
    mySentence=re.sub("([a-zA-Z0-9]+)".format(tabuListStr),r" \1 ",mySentence)
    # print(mySentence)
    
    if "n" in methods:
        mySentence=re.sub("((?!{})[0-9]+)".format(tabuListStr)," num ",mySentence)
        
    if "p" in methods:
        mySentence=re.sub("(?!{})["+puncStr+"]+".format(tabuListStr),"",mySentence)
    
    mySentence=" ".join([charItem for charItem in mySentence.split(" ") if len(charItem)>0])
    mySentenceList=[]
    for wordItem in mySentence.split(" "):
        if len(re.findall("[\u4e00-\u9fa5]",wordItem))==len(wordItem):
            for charItem in wordItem:
                mySentenceList.append(charItem)
        else:
            mySentenceList.append(wordItem)
            
    if "s" in methods:
        mySentenceList=[tokenItem 
                        for tokenItem in mySentenceList 
                        if tokenItem in tabuTokenList or tokenItem.lower() not in totalStopWordList]
        
    tmpSentence=" ".join(mySentenceList)
    return tmpSentence     

def getSEOfEntity_forCH(entityItem,mySentenceList):
    '''
    获取中文实体entityItem列表头尾id
    '''
    seList=[]
    for tokenI,tokenItem in enumerate(mySentenceList):
        if tokenItem==entityItem[0]:
            plusTokenI=0
            startI=tokenI+plusTokenI
            while plusTokenI<len(entityItem) and tokenI+plusTokenI<len(mySentenceList) and mySentenceList[tokenI+plusTokenI]==entityItem[plusTokenI]:
                plusTokenI+=1
            if plusTokenI==len(entityItem):
                endI=tokenI+plusTokenI
                seList.append([startI,endI])
    return seList

def getSEOfEntity_forEN(entityItem,mySentenceList):
    '''
    获取英文实体entityItem列表头尾id
    '''
    entityItemList=entityItem.split(" ")
    mySentenceList=mySentenceList
    seList=[]
    for tokenI,tokenItem in enumerate(mySentenceList):
        if tokenItem==entityItem[0]:
            plusTokenI=0
            startI=tokenI+plusTokenI
            while plusTokenI<len(entityItemList) and tokenI+plusTokenI<len(mySentenceList) and mySentenceList[tokenI+plusTokenI]==entityItemList[plusTokenI]:
                plusTokenI+=1
            if plusTokenI==len(entityItemList):
                endI=tokenI+plusTokenI
                seList.append([startI,endI])
    return seList

def tagSentence(mySentence,entityList):
    '''
    为句子mySentence标注entityList中的实体
    '''
    mySentenceList=preprocessSentence(mySentence).split(" ")
    
    BIOList=["O" for tagItem in mySentenceList]
    
    mySentence_forCH="".join(mySentenceList)
    mySentence_forEN=" ".join(mySentenceList)
    seList=[]
    for entityI,entityItem in enumerate(entityList):
        entityItem=entityItem.lower()
        if len(re.findall("[\u4e00-\u9fa5]",entityItem))>0:
            if entityItem in mySentence_forCH:
                seList=getSEOfEntity_forCH(entityItem,mySentenceList)
        elif entityItem in mySentenceList:
            if entityItem in mySentence_forEN:
                seList=getSEOfEntity_forEN(entityItem,mySentenceList)
    
    for seItem in seList:
        startI,endI=seItem
        BIOList[startI]="B"
        for charI in range(startI+1,endI):
            BIOList[charI]="I"
    
    return " ".join(BIOList)

if __name__=="__main__":
    mySent="通过形状语言建立大世界art direction bootcamp: building worlds shape language 通 形 状 语 言 建 世 界 讲师：patrick faulwetter 【内容简介】 order inform process building imaginary worlds video games movies, talk aims examine term 'culture' 'story' expresses physical world. story culture written myriad particulars architecture, customs, symbols, values transportation systems. starting philosophical perspective, patrick show practical process tools build shape languages abstract shapes designing subject matters world building including vehicles, costumes, architecture environments. 为了让大家了解到电子游戏和电影的虚拟世界构建过程，本讲座将深入探讨“文化”一词，文化即是我们现实世界中所经历的故事。从建筑、习俗、符号、价值观到交通系统，文化的故事以无数的细节书写。从哲学的角度出发，patrick将展示为world building设计不同的主题，包括车辆、服装、建筑和环境时使用2d和3d工具从抽象形状构建形状语言的实际过程。 本文翻译官：samanthawei(魏翠敏)"
    tabuList=['语言', 'art', '讲师', '内容', '游戏', '虚拟', '构建', '系统', '书写', '展示', '车辆', '2d', '3d', '抽象', '构建', '语言', '翻译']
    processedSent=preprocessSentence(mySent,methods="lnps",stopwords=[],tabuList=tabuList)
    print(processedSent)