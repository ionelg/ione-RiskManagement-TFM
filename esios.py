'''
UTF-8 (Unicode Transformation Format-8)
'''

#01. DATA AQUISITION


#Luckily for us, RED ELECTRICA provides loads of raw public data in json files reachable throgh API's. For data aquisition we are defining functions to bring down this json indicators as libraries and dataframes to be capable of treating them and working  with them further on our study.

import pandas as pd
import numpy as np
import requests
import datetime 



def header():

#header() function returns a dictionary with relevant inputs to connect to https://api.esios.ree.es using APIs.API (Application Programming Interface’) it's a group of rules (code) and specifications which apps can follow to comunicate between them. 

#A personal token must be used, you can ask for one here: consultasios@ree.es (They answer back in 24h).

    token = '...................................'
    header = dict()
    header['Accept'] = 'application/json; application/vnd.esios-api-v1+json'
    header['Content-Type'] = 'application/json'
    header['Host'] = 'api.esios.ree.es'
    header['Authorization'] = 'Token token=\"' + token + '\"'
    header['Cookie'] = ''
    return header



def archives_json_dict():
    
#archives_json_dict() returns a dictionary with json archives shared on  https://api.esios.ree.es

    r = requests.get('https://api.esios.ree.es/archives_json', headers=header()).json()
    r = r['archives']
    dic = {item['name']:item['id'] for item in r}
    return dic



def indicators_dict():  

#Vital in our study. indicators_dict() returns a dictionary with json indicators shared on  https://api.esios.ree.es         (key = indicator name,value = indicator number )
     
    r = requests.get('https://api.esios.ree.es/indicators', headers=header()).json()
    r = r['indicators']
    dic = {item['name']:item['id'] for item in r}
    return dic



def coincidences(input_data):
     
#Due there are over 1500 indicators shared, 'coincidence()' function will help to find an indicator by introducin a word contained in the keys of the indicators_dictionary.

    indicators = indicators_dict().keys()
    coincidences = []
    if type(input_data) == str:
        coincidences = [i for i in indicators if input_data in i]
    else:        
        for ind in indicatorss:
            item = str.split(ind)
            c = 0
            for word in input_data:
                if word in item:
                    c += 1
            if c == len(input_data):
                coincidences.append(ind)            
    return coincidences



def indicators(name,start,end):
    
#In temporal series is important to be able to pick a particular time period. This is what indicators() function returns.    For our modeling we need to choose indicators between one starting date and one ending date. We will be using hourly units in a pandas datataframe.

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

#Nuclear disponibility is an important parameter in any power grid. This function returns added disponibility of the Spanish   7 nuclear reactors for which ever period.
    
    name = 'Potencia disponible de generación Nuclear horizonte horario'
    df = indicator(name,start,end)
    df = df.groupby('datetime').sum()
    df = df.iloc[:-1,:]
    return df['value']



def PUs():
    
#This function returns a dataframe with very valuable parameters of all de generation and consuption powerplants in the power system. As they register and unsubscribe frequently is important for our study here know about the present participants. For people not used to Iberian power system it  gives an important framework of our document.  

    url = 'https://api.esios.ree.es/archives/111/download_json?locale=es'
    r = requests.get(url, headers=header()).json()
    r = r['ProgrammingUnits']
    df = pd.DataFrame(r)
    return df



def find_pu(up):

#find_pu() looks for any particular generation or consuption  powerplants in PUs() dataframe. 

    
    url = 'https://api.esios.ree.es/archives/82/download_json?locale=es'
    r = requests.get(url, headers=header()).json()
    r = r['UnidadesProgramacion']
    df = pd.DataFrame(r)
    coincidences = [x for x in df['Código de UP'] if up in x]
    result = df[df['Código de UP'].isin(coincidences)]
    print('Concidencias encontradas con <%s>' %(up))
    return result



#02. DATA CLEANING AND PREPARATION


def Desiosformat(idate, edate):
    
#Transforms  idate and edate (YYYYMMDD, YYYYMMDD) into (YYYY-MM-DD 00:00:00, YYYY-MM-DD 23:59:59).                                       This date format will be used on next finction IndicatorQuest().
    
    idate = datetime.datetime.strftime(datetime.datetime.strptime(idate,'%Y%m%d'), '%Y-%m-%d %H:%M:%S')
    edate = datetime.datetime.strptime(edate, '%Y%m%d') 
    edate = edate + datetime.timedelta(days=1) - datetime.timedelta(seconds=1) 
    edate = datetime.datetime.strftime(edate, '%Y-%m-%d %H:%M:%S')  
    
    return idate,edate


def IndicatorQuest(idate, edate, indicator):
     
#Returns a dataframe with datetime as index and indicator as input.
#:idate: first date of the interval, 'YYYYMMDD'
#:edate: last date of the interval, 'YYYYMMDD'  

    
    token = '..............................................'
    
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
    
    geo_id =[]
    if 3 in df['geo_id'].unique(): # For indicator 600 - Spain power price
        df = df[df['geo_id'] == 3]

    df['dt'] = [x[:10] + ' ' + x[11:13] + ':00:00' for x in df['datetime']]       
    df = df.set_index(pd.to_datetime(df['dt']))[['value']]        
    df.columns = [str(indicator)]
    
    if indicator == 474: # For indicator 474 - nuclear availability
        return df.groupby('dt').sum()
    else:
        return df
    
    return df



def listingdates(endRange, days):

#Returns a list containing all the dates between the two chosen.
#endRange: last date of the range of dates
#days: number of days included in the list    
   
    date1 = datetime.datetime.strptime(endRange, '%Y%m%d') - datetime.timedelta(days=days)  
    date2 = datetime.datetime.strptime(endRange, '%Y%m%d') 

    delta = date2 - date1  
    lstDates = []
    for i in range(delta.days + 1):
        dt = datetime.datetime.strftime(date1 + datetime.timedelta(i), '%Y%m%d')
        lstDates.append(dt)
    return lstDates

    
def Batch(idate, edate, indList):
    
#Returns a dataset including the values of every indicator included indlist.  
#:idate: first date of the interval, 'YYYYMMDD'
#:edate: last date of the interval, 'YYYYMMDD'  
   
    df = pd.DataFrame()
    
    for ind in indList:
        req = IndicatorQuest(idate, edate, ind)
        df = pd.concat([df, req], axis=1)      
    return df

 
    
