


import pandas as pd
import numpy as np
import requests
import datetime 


# API esios.

def header():
    token = '....................................................'
    header = dict()
    header['Accept'] = 'application/json; application/vnd.esios-api-v1+json'
    header['Content-Type'] = 'application/json'
    header['Host'] = 'api.esios.ree.es'
    header['Authorization'] = 'Token token=\"' + token + '\"'
    header['Cookie'] = ''
    return header

def archives_json_dict():    
    r = requests.get('https://api.esios.ree.es/archives_json', headers=header()).json()
    r = r['archives']
    dic = {item['name']:item['id'] for item in r}
    return dic

def indicators_dict():    
    r = requests.get('https://api.esios.ree.es/indicators', headers=header()).json()
    r = r['indicators']
    dic = {item['name']:item['id'] for item in r}
    return dic

def coincidences(input_data):
    indicators = indicators_dict().keys()
    coincidences = []
    if type(input_data) == str:
        coincidences = [i for i in inds if input_data in i]
    else:        
        for ind in indicatorss:
            item = str.split(ind)
            c = 0
            for word in input_data:
                if word in item:
                    c += 1
            if c == len(input_data):
                coincidences.append(ind)            
    return coincidendeces

def indicators(name,start,end):    
    head = header()
    param = {'start_date':start,'end_date':end,'time_trunc':'hour'}
    ind = indicators_dict()
    url = 'https://api.esios.ree.es/indicators/' + str(ind[name])
    print('Requesting <%s: %s -> %s>' %(name,start,end))
    r = requests.get(url, headers = head, params = param).json()
    valores = r['indicator']['values']
    df = pd.DataFrame(valores)
    df = df.iloc[:-1,:]
    return df
                    
       
def nuclear_availability(start,end):
    name = 'Potencia disponible de generación Nuclear horizonte horario'
    df = indicator(name,start,end)
    df = df.groupby('datetime').sum()
    df = df.iloc[:-1,:]
    return df['value']


def PUs():
    url = 'https://api.esios.ree.es/archives/111/download_json?locale=es'
    r = requests.get(url, headers=header()).json()
    r = r['ProgrammingUnits']
    df = pd.DataFrame(r)
    return df


def find_pu(up):
    url = 'https://api.esios.ree.es/archives/82/download_json?locale=es'
    r = requests.get(url, headers=header()).json()
    r = r['UnidadesProgramacion']
    df = pd.DataFrame(r)
    coincidences = [x for x in df['Código de UP'] if up in x]
    result = df[df['Código de UP'].isin(coincidences)]
    print('Concidencias encontradas con <%s>' %(up))
    return result


def Desiosformat(idate, edate):
    
    idate = datetime.datetime.strftime(datetime.datetime.strptime(idate,'%Y%m%d'), '%Y-%m-%d %H:%M:%S')
    edate = datetime.datetime.strptime(edate, '%Y%m%d') 
    edate = edate + datetime.timedelta(days=1) - datetime.timedelta(seconds=1) 
    edate = datetime.datetime.strftime(edate, '%Y-%m-%d %H:%M:%S')  
    
    return idate,edate

def listingdates(endRange, days):
   
    date1 = datetime.datetime.strptime(endRange, '%Y%m%d') - datetime.timedelta(days=days)  
    date2 = datetime.datetime.strptime(endRange, '%Y%m%d') 

    delta = date2 - date1  
    lstDates = []
    for i in range(delta.days + 1):
        dt = datetime.datetime.strftime(date1 + datetime.timedelta(i), '%Y%m%d')
        lstDates.append(dt)
    return lstDates
    
def IndicatorQuest(idate, edate, indicator):
    
    token = '.............................................'
    
    idate, edate = Desiosformat(idate,edate) 
    
    header = {'Accept': 'application/json; application/vnd.esios-api-v1+json',
              'Content-Type': 'application/json',
              'Host': 'api.esios.ree.es',
              'Authorization': 'Token token="{0}"'.format(token),
              'Cookie':'' }
    
    param = {'start_date':idate, 'end_date':edate, 'time_trunc':'hour'}
    url = 'https://api.esios.ree.es/indicators/' + str(indicator)
    r = requests.get(url, headers=header,params=param).json()
    

    v = r['indicator']['values']
    df = pd.DataFrame(v)
    
    
    if 3 in df['geo_id'].unique(): 
        df = df[df['geo_id'] == 3]

    df['dt'] = [x[:10] + ' ' + x[11:13] + ':00:00' for x in df['datetime']]       
    df = df.set_index(pd.to_datetime(df['dt']))[['value']]        
    df.columns = [str(indicator)]
    
   
    if indicator == 474: 
        return df.groupby('dt').sum() 
    else:
        return df
    return df

def Batch(idate, edate, indList):
   
    df = pd.DataFrame()
    
    for ind in indList:
        req = IndicatorQuest(idate, edate, ind)
        df = pd.concat([df, req], axis=1)      
    return df

def Dsets(idate, edate, Fdate):
    
    month = int(Fdate[4:6])
   
    TrainD = Batch(idate, edate, indList)
    EvalD = Batch(fcDate, FDate, indList[:-1]) 
    
    return TrainD, EvalD
    



