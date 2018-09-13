# eSIOS functions API
# coding: utf-8

import pandas as pd
import numpy as np
import requests



def header():
    token = 'YOUR FREE PERSONAL TOKEN'
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
    inds = indicators_dict().keys()
    coin = []
    if type(input_data) == str:
        coin = [i for i in inds if input_data in i]
    else:        
        for ind in inds:
            item = str.split(ind)
            c = 0
            for word in input_data:
                if word in item:
                    c += 1
            if c == len(input_data):
                coin.append(ind)            
    return coin

def indicator(name,start,end):    
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
                    
def indicators_batch(lst,start,end):
    if type(lst) == list:
        dic_item = {}
        for item in lst:
            df_item = indicator(item,start,end)
            if not df_item.empty:
                dic_item[item] = df_item['value']
            else:
                print('No data found for <%s>' %(item))
        df_total = pd.DataFrame(dic_item)
        return df_total
    else:
        print('Insert a list of items as first input or use \'indicator(item,start_date,end_date)\' instead!')
        
def nuclear_availability(start,end):
    name = 'Potencia disponible de generación Nuclear horizonte horario'
    df = indicator(name,start,end)
    df = df.groupby('datetime').sum()
    df = df.iloc[:-1,:]
    return df['value']

def PMD(start,end):
    name = 'Precio mercado SPOT Diario'
    df = indicator(name,start,end)
    df = df[df['geo_id'] == 3]

    return df['value']

def archive_json(identifier): 
    url = 'https://api.esios.ree.es/archives//' + str(identifier) + '/download_json?locale=es'
    r = requests.get(url, headers=header()).json()

    return r

def sujetos_mercado():
    url = 'https://api.esios.ree.es/archives/83/download_json?locale=es'
    r = requests.get(url, headers=header()).json()
    r = r['SujetosMercado']
    df = pd.DataFrame(r)
    return df

def ups():
    url = 'https://api.esios.ree.es/archives/111/download_json?locale=es'
    r = requests.get(url, headers=header()).json()
    r = r['UnidadesProgramacion']
    df = pd.DataFrame(r)
    return df

def buscar_up(up):
    url = 'https://api.esios.ree.es/archives/82/download_json?locale=es'
    r = requests.get(url, headers=header()).json()
    r = r['UnidadesProgramacion']
    df = pd.DataFrame(r)
    coincidences = [x for x in df['Código de UP'] if up in x]
    result = df[df['Código de UP'].isin(coincidences)]
    print('Concidencias encontradas con <%s>' %(up))
    return result

