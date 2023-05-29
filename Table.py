from bs4 import BeautifulSoup as bs
import json
import pandas as pd
import re
def camel_case(s):
  return re.sub(r"(_|-)+", " ", s).title().replace(" ", "").strip()

def neat(x):
    return re.sub("\s\s+", " ", x.strip("\n")).strip().replace(":","").strip()

def table_to_dict(html,type_,precolumns):
    
    
    
    if type_=="Type5":
        soup =bs(html,"html.parser")
        table =soup.find("table")
        rows=   table.find_all("tr")

        data = []
        for row in rows:
            cols = row.find_all('td')
            r = []
            for col in cols:
                if col.get('colspan'):
                    for x in range(0,int(col.get('colspan'))):
                        r.append(neat(col.text))
                else:
                    r.append(neat(col.text))
            data.append(r)
        
        df = pd.DataFrame(data)
        for  i in data:
            print(i)        
        data=df.to_dict('records')
        return data
    
    if type_=="Type4":
        soup =bs(html,"html.parser")
        table =soup.find("table")
        ths=table.find("thead").find_all("th")
        headings=[x.text for x in ths]
        print(headings)
        tr= table.find("tbody").find_all("tr")
        rows=[]

        for td in tr:
            row=[x.text for x in td.find_all("td")]
            rows.append(row)

        df=pd.DataFrame(rows,columns=precolumns)
        data=df.to_dict('records')
        print(json.dumps(data,indent=4))
        return data   
     
    soup=bs(html,"html.parser")
    table =soup.find("table")
    tr =table.find_all("tr" )
    print(len(tr))
    
    
    
    
    if type_=="Type3":        
        rows = table.find_all('tr')

        #header = [neat(col.text) for col in rows[0].find_all('th')]

        data = []
        for row in rows[1:]:
            cols = row.find_all('td')
            data.append([neat(col.text) for col in cols])

        #final_data = [dict(zip(header, item)) for item in data]    
        df = pd.DataFrame(data)
        for  i in data:
            print(i)        
        data=df.to_dict('records')
        return data
    if type_!="headless":
        th=tr[0].find("th")

        if not th:
            th=tr[0].find("td")

        th_count=len(tr[0].find_all(recursive=False))


        row_span_value =int(th.get('rowspan',0))

        headings=[]
        rows_=[]
        thead =table.find("thead")

        if thead ==None:
            if row_span_value ==0:   
                if th_count==2:            

                    for i in tr:
                        h_=i.find_all("th")
                        if len(h_)!=0:
                            for z in h_:
                                headings.append(z)    
                                        
                else:
                    headings=tr[0]    
                    headings=tr[0].find_all("th")
                
                    if len(headings)==0:
                        headings=tr[0].find_all("td")
                    rows_=tr[1:]                            
            else:        
                heading=tr[:row_span_value]
                for i in heading:
                    h_=i.find_all("td")
                    if len(h_)==0:
                        h_=i.find_all("th")
                    for i in h_:
                        if not i.get('colspan'):
                            headings.append(i)  
                
                rows_=tr[row_span_value:]
        else:
            headings=[x for x in thead.findChildren(recursive=False)]
            if len(headings)==1:
                headings=[x for x in thead.find_all("th")]
                
            rows_=tr[1:]


        final_rows=[]
        headings=[camel_case(neat(x.text)).replace(")","_").replace("(","_") for x in headings]

        if th_count ==2 or len(tr)==1:
            d_c1=[]
            
            for i in tr:
                    h_=i.find_all(recursive=False)
                    if len(h_)==2:
                    
                        d=[x.text for x in h_] 
                    
                        if len(d)!=0: d_c1.append(d) 
                        

        
            d_c=pd.DataFrame(d_c1)
            
            if len(d_c1)==1:
                final_={"0":d_c1[0][0], "1":d_c1[0][1]}
            
            else:                                                        
                final_=[dict(zip([camel_case(neat(x)) for x in d_c[0]], [re.sub("\s\s+", " ", x.strip("\n")).replace("\n"," ").strip() for x in d_c[1]]))]
                        
            
            for i in final_:
                try: 
                    if i[""]=="":
                        del i[""]
                except: pass
            
                    
        
            return final_
        
            
        else:              
            for i in rows_:
                th=i.find_all("th")   +  i.find_all("td")                                      
                
                r_=[neat(x.text) for x in th if not x.get('colspan')]
                    
            
                if len(r_)!=0:final_rows.append(r_)

            if len(final_rows)==0:final_rows=[[""  for x in headings] for x in headings]
        
            
            try:
                df = pd.DataFrame(final_rows,columns=headings)
                
                data=df.to_dict('records')
                
            except:
                soup=bs(html,"html.parser")
                final_rows=[]
                table=soup.find("table")
                t=table.tbody
                if t:
                    t=table.tbody.findChildren(recursive=False)
        
                else:
                    t=table.findChildren(recursive=False)
                    
                for i in t:
                    data=[neat(x.text) for x in i if x.text!="\n" if not x.get('colspan')]
                    final_rows.append(data)
                if row_span_value ==0:
                    row_span_value=1
                    
                try:
                    df = pd.DataFrame(final_rows[row_span_value:],columns=headings)
                except:
                    df = pd.DataFrame(final_rows[row_span_value:])
                        
                
                
                    
                if len(df.index)==0:
                    return final_rows
                data=df.to_dict('records')
                
        
            for i in data:                
                try:
                    if i[""]=="": 
                        del i[""]
                except: pass
            return data
    else:
        final_rows=[]
        if table.tbody:
            tr=table.tbody.find_all("tr",recursive=False)
        else:
            tr=   table.find_all("tr",recursive=False)
             
        for i in tr:
                th=i.find_all(recursive=False)                                     
                
                r_=[neat(x.text) for x in th if not x.get('colspan')]
                    
            
                if len(r_)!=0:final_rows.append(r_)

       # if len(final_rows)==0:final_rows=[[""  for x in headings] for x in headings]
        df = pd.DataFrame(final_rows)
        for  i in final_rows:
            print(i)        
        data=df.to_dict('records')
        return data
        
        
                
