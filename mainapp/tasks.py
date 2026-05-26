from concurrent.futures import ThreadPoolExecutor

from celery import shared_task
# from yahoo_fin.stock_info import *
from nselib import indices
from .views import fetch_stock   #later remove this business logic function to another as it is common and not good to write in views


@shared_task(bind=True) #This tells Celery:"Register this as async task"
#bind =true ---->Give task object access to self
#This converts normal Python function into:Celery background task.Without this:Celery cannot execute function
def update_stock(self,stockpicker):
    data = {}
    available_stocks = indices.constituent_stock_list(index_category='BroadMarketIndices',index_name='Nifty 50')
    available_stocks = available_stocks['Symbol'].tolist()
    # print("available_stocks: ",available_stocks)
    # available_stocks = constants.stock_picker #comment
    validated_stocks = []
    for stock in stockpicker:
        if stock in available_stocks:
            validated_stocks.append(stock + ".NS")
        elif stock+".NS" in validated_stocks:   #not sure about this logic
            validated_stocks.remove(stock)
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(fetch_stock, validated_stocks)
        for result in results:
            data.update(result)
    return "DONE"