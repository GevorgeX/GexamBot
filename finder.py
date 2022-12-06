import fitz
from data import lessons

class Finder:

    data = None
    @staticmethod
    def SetLesson(lesson):
        Finder.data = lessons[lesson]

    @staticmethod
    def FindPage(txt:str) -> list:
        pageNumbers = []
        for shtemNum in range(1,len(Finder.data.keys())+1):
            pdf = fitz.open(Finder.data[shtemNum]['file'])
            for pageNum in range(len(pdf)):
                page = pdf.load_page(pageNum)
                if page.search_for(txt):
                    pageNumbers.append((shtemNum, pageNum+1))
        return pageNumbers

    @staticmethod
    def GetImageOfPage(cur_num:tuple)->str:
        ref_of_shtem = Finder.data[cur_num[0]]['images']
        if cur_num[1] >=100:
            return f'{ref_of_shtem}{ref_of_shtem[6:]}-{str(cur_num[1])}.jpg'
        elif cur_num[1] >=10:
            return f'{ref_of_shtem}{ref_of_shtem[6:]}-0{str(cur_num[1])}.jpg'
        elif cur_num[1] >=0:
            return f'{ref_of_shtem}{ref_of_shtem[6:]}-00{str(cur_num[1])}.jpg'

    @staticmethod
    def GetAnswer(cur_num:list)->tuple:
        for section in Finder.data[cur_num[0]]['sections']:
            if section[0] <= cur_num[1] < section[1]:
                num = Finder.data[cur_num[0]]['sections'][section]
                return (cur_num[0],num)






