from concurrent.futures import ThreadPoolExecutor
from django.http import HttpResponse
from django.shortcuts import render
from yahoo_fin.stock_info import *
from nselib import indices
from . import constants
import time
import yfinance as yf
from asgiref.sync import sync_to_async

@sync_to_async
def checkAuthenticated(request):
    if not request.user.is_authenticated:
        return False
    return True

def stockPicker(request):
    stock_picker = (indices.constituent_stock_list(index_category='BroadMarketIndices',index_name='Nifty 50')
        .rename(columns={'Company Name': 'company_name','Symbol': 'symbol'})[['company_name', 'symbol']]
        .to_dict('records'))
    return render(request,'mainapp/stockpicker.html',{'stock_picker':stock_picker})

def fetch_stock(stock):
    try:
        ticker = yf.Ticker(stock)
        info = ticker.fast_info
        return {
            stock: {
                "price": info.get("lastPrice"),
                "open": round(info.get("open", 0), 2),
                "previousClose":info.get("previousClose"),
                "marketCap": info.get("marketCap"),   #need to format this as not in human readable format
                "volume": info.get("lastVolume"),
            }
        }
    except Exception as e:
        return {stock: {"error": str(e)}}
    
async def stockTracker(request):
    is_loginned = await checkAuthenticated(request)
    if not is_loginned:
        return HttpResponse("First login...")
    
    stockpicker = request.GET.getlist('stockpicker')
    data = {}
    available_stocks = indices.constituent_stock_list(index_category='BroadMarketIndices',index_name='Nifty 50')
    available_stocks = available_stocks['Symbol'].tolist()
    # print("available_stocks: ",available_stocks)
    # available_stocks = constants.stock_picker #comment
    validated_stocks = []
    for stock in stockpicker:
        if stock in available_stocks:
            validated_stocks.append(stock + ".NS")
        else:
            return HttpResponse("Error")   #here add try except and print that log don't directly give the error 
        
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(fetch_stock, validated_stocks)
        for result in results:
            data.update(result)

    # print("data is ",data)
    return render(request,"mainapp/stocktracker.html",{'data':data,'room_name':'track'})