from fastapi import FastAPI,Depends,Query #nessary imports form fastapi
from pydantic import BaseModel,validator,root_validator,conint,constr,confloat ,DateTimeError #pydantic imports 
from elasticsearch import Elasticsearch,TransportError,ConnectionError # Elastic
from typing import Optional #typing 
import datetime as dt # datetime imports 


app = FastAPI() # class initialized
try:
    es = Elasticsearch(cloud_id="<cloudID>"  ,api_key="<apiKey>" 
                    # or use host = "<local_host>"
                    )
except ConnectionError: # error when connecting
    print( "check connections")



class Listall(BaseModel): # pydantic class for validation
    size:conint(ge=1) = Query(default=10)
    page:conint(ge=1) = Query(default=1)
    order:constr(min_length=3,max_length=4) = Query(default="asc")
    on:str = Query(default="")

    @validator('order') # Basemodel class wraper function for validation of argumnet "order"
    def is_not_in(cls, v):
        if v not in ['asc','desc']:
            raise ValueError('The argument must be `asc` for ascending, `desc` for descending')
        return v

@app.get("/") #get wrapper form fastapi for root
def read_root():
    return {"Type": "Trading Infomation API"}


@app.get("/listAll") #get wrapper form fastapi to end point
def read_root(args: Listall = Depends()):
    body = {
        "query": {
            "match_all": {}
        },
        "from": (args.page - 1) * args.size,
        "size": args.size,
        "sort": [
        {
            args.on : {
                "order": args.order
            }
        }
        ]
    }
    try:
        response = es.search(index="trade", body=body)["hits"]["hits"]
    except KeyError:
        response = {"":"No data found"}
    except TransportError as e:
        response = {"error":f" transport error occured {e.status_code}"}
    return response
    return body


@app.get("/singleId") #get wrapper form fastapi to end point
def read_root(id:str):
    body = {
        "query": {
            "match": {
                "tradeId": id
            }
        },"size":1
    }
    try:
        response = es.search(index="trade", body=body)["hits"]["hits"]
    except KeyError:
        response = {"":"No data found"}
    except TransportError as e:
        response = {"error":f" transport error occured {e.status_code}"}
    return response
    # return body


@app.get("/searchT") #get wrapper form fastapi to end point
def read_root(query:str):
    body = {
      "query": {
        "bool": {
          "must": [
            {
            "multi_match": {
                "query": query,
                "fields": ["counterparty","instrumentId","instrumentName","trader"]
            }
        }]}}

    }
    try:
        response = es.search(index="trade", body=body)["hits"]["hits"]
    except KeyError:
        response = {"":"No data found"}
    except TransportError as e:
        response = {"error":f" transport error occured {e.status_code}"}
    return response
    # return body


class AdvancFilter(BaseModel): # pydantic class for validation
    tradeType:str
    maxPrice:Optional[float]
    minPrice:Optional[confloat(gt=0)]
    end:Optional[dt.datetime]
    start:Optional[dt.datetime]
    assetClass:Optional[str]

    @root_validator() # Basemodel class wraper function for root validation of argumnet "end" and "start" to acess both at same time
    def before(cls,values):
        if values["end"] and values["start"]:
            if values["start"] > values["end"]:
                raise ValueError('The start date must be before the end date.')
            return values
        return values

    @root_validator() # Basemodel class wraper function for root validation of argumnet "minPrice" and "maxPrice" to acess both at same time
    def is_great(cls,values):
        if values['minPrice'] and values['maxPrice']:
            if values['maxPrice'] < values['minPrice']:
                raise ValueError(f'The argument must be greater than minPrice = {values["minPrice"]}')
            return values
        return values

    @validator('tradeType') # Basemodel class wraper function for validation of argumnet "tradeType"
    def is_not_in(cls,v):
        if v not in ['BUY','SELL']:
            raise ValueError('The argument must be `BUY` for buys, `SELL` for sells')
        return v


@app.get("/AdvanccFilter") #get wrapper form fastapi to end point
def read_root(args: AdvancFilter = Depends()):

    body={ # body initalized query 
        "query": {
            "bool": {
            "must": [
                    {
                    "nested": {
                      "path": "trade_details",
                        "query": {
                          "bool": {
                    "must": [
                              {
                                "match": {
                                "trade_details.buySellIndicator": args.tradeType
                                }
                              }
                            ]
                          }
                        }
                      }
                    }
            ]
            }
        }
        }

    #appending and updating values got from user
    if args.assetClass:
        body["query"]["bool"]["must"].append(                {
                "match": {
                    "asset_class": args.assetClass
                }
                })
    if args.start or args.end :
      body["query"]["bool"]["must"].append(
                {
                "range": {
                    "tradeDateTime": {

                    }
                }
                }
                )
      if args.start:
          body["query"]["bool"]["must"][-1]["range"]["tradeDateTime"].update({"gte": args.start})

      if args.end:
          body["query"]["bool"]["must"][-1]["range"]["tradeDateTime"].update({"lte": args.end})

    if args.minPrice or args.maxPrice:
        body["query"]["bool"]["must"][0]["nested"]["query"]["bool"]["must"].append({
                    "range": {
                      "trade_details.price": {

                      }
                    }
                  })
        if args.minPrice:
            body["query"]["bool"]["must"][0]["nested"]["query"]["bool"]["must"][-1]["range"]["trade_details.price"].update({"gte": args.minPrice})

        if args.maxPrice:
            body["query"]["bool"]["must"][0]["nested"]["query"]["bool"]["must"][-1]["range"]["trade_details.price"].update({"lte": args.maxPrice})



    try:
        response = es.search(index="trade", body=body)["hits"]["hits"]
    except KeyError:
        response = {"result":"No data found"}
    except TransportError as e:
        response = {"error": f" transport error occured {e.status_code}"}
    except DateTimeError:
        response = {"Error":"error in date format"}
    return response
    # return body




# Data

# {
#     "took": 0,
#     "timed_out": false,
#     "_shards": {
#       "total": 1,
#       "successful": 1,
#       "skipped": 0,
#       "failed": 0
#     },
#     "hits": {
#       "total": {
#         "value": 20,
#         "relation": "eq"
#       },
#       "max_score": 1,
#       "hits": [
#         {
#           "_index": "tradee",
#           "_id": "qvsOm4gBN-67MQqYYb1p",
#           "_score": 1,
#           "_source": {
#             "instrumentName": "drums",
#             "quantity": 100,
#             "instrumentId": "a1",
#             "price": 100,
#             "tradeDateTime": "2012-11-30T04:52:56",
#             "trader": "ritesh",
#             "counterparty": "Prabal",
#             "buySellIndicator": "sell",
#             "assetClass": "Commodities",
#             "tradeId": "t1"
#           }
#         },
#         {
#           "_index": "tradee",
#           "_id": "q_sOm4gBN-67MQqYYb1p",
#           "_score": 1,
#           "_source": {
#             "instrumentName": "guitar",
#             "quantity": 10,
#             "instrumentId": "a2",
#             "price": 10,
#             "tradeDateTime": "2010-06-30T18:52:56",
#             "trader": "prabal",
#             "counterparty": "ritesh",
#             "buySellIndicator": "buy",
#             "assetClass": "Commodities",
#             "tradeId": "t2"
#           }
#         },
#         {
#           "_index": "tradee",
#           "_id": "rPsOm4gBN-67MQqYYb1p",
#           "_score": 1,
#           "_source": {
#             "instrumentName": "shares",
#             "quantity": 1000,
#             "instrumentId": "a3",
#             "price": 100,
#             "tradeDateTime": "2028-04-30T18:52:56",
#             "trader": "bob singh",
#             "counterparty": "zerodha",
#             "buySellIndicator": "buy",
#             "assetClass": "Equity",
#             "tradeId": "t3"
#           }
#         },
#         {
#           "_index": "tradee",
#           "_id": "rfsOm4gBN-67MQqYYb1p",
#           "_score": 1,
#           "_source": {
#             "instrumentName": "loan",
#             "quantity": 1,
#             "instrumentId": "a4",
#             "price": 100000,
#             "tradeDateTime": "2012-04-30T18:52:56",
#             "trader": "ananya enterprises",
#             "counterparty": "prabal",
#             "buySellIndicator": "sell",
#             "assetClass": "Bond",
#             "tradeId": "t4"
#           }
#         },
#         {
#           "_index": "tradee",
#           "_id": "rvsOm4gBN-67MQqYYb1p",
#           "_score": 1,
#           "_source": {
#             "instrumentName": "football",
#             "quantity": 200,
#             "instrumentId": "a5",
#             "price": 1000,
#             "tradeDateTime": "2022-08-30T18:52:56",
#             "trader": "ananya enterprises",
#             "counterparty": "ritesh",
#             "buySellIndicator": "sell",
#             "assetClass": "Commodities",
#             "tradeId": "t5"
#           }
#         },
#         {
#           "_index": "tradee",
#           "_id": "r_sOm4gBN-67MQqYYb1p",
#           "_score": 1,
#           "_source": {
#             "instrumentName": "shares",
#             "quantity": 1000,
#             "instrumentId": "a6",
#             "price": 12000,
#             "tradeDateTime": "2016-09-30T20:52:56",
#             "trader": "ananya enterprises",
#             "counterparty": "upstox",
#             "buySellIndicator": "sell",
#             "assetClass": "Equity",
#             "tradeId": "t6"
#           }
#         },
#         {
#           "_index": "tradee",
#           "_id": "sPsOm4gBN-67MQqYYb1p",
#           "_score": 1,
#           "_source": {
#             "instrumentName": "plot",
#             "quantity": 0,
#             "instrumentId": "a7",
#             "price": 10,
#             "tradeDateTime": "2019-10-30T18:52:56",
#             "trader": "ananya enterprises",
#             "counterparty": "prabal",
#             "buySellIndicator": "sell",
#             "assetClass": "Real estate",
#             "tradeId": "t7"
#           }
#         },
#         {
#           "_index": "tradee",
#           "_id": "sfsOm4gBN-67MQqYYb1p",
#           "_score": 1,
#           "_source": {
#             "instrumentName": "loan",
#             "quantity": 3,
#             "instrumentId": "a8",
#             "price": 30000,
#             "tradeDateTime": "2012-05-30T18:52:56",
#             "trader": "LIC",
#             "counterparty": "arpit",
#             "buySellIndicator": "sell",
#             "assetClass": "Bond",
#             "tradeId": "t8"
#           }
#         },
#         {
#           "_index": "tradee",
#           "_id": "svsOm4gBN-67MQqYYb1p",
#           "_score": 1,
#           "_source": {
#             "instrumentName": "share",
#             "quantity": 30,
#             "instrumentId": "a9",
#             "price": 1000,
#             "tradeDateTime": "2020-05-30T18:52:56",
#             "trader": "zerodha",
#             "counterparty": "prabal",
#             "buySellIndicator": "sell",
#             "assetClass": "Equity",
#             "tradeId": "t9"
#           }
#         },
#         {
#           "_index": "tradee",
#           "_id": "s_sOm4gBN-67MQqYYb1p",
#           "_score": 1,
#           "_source": {
#             "instrumentName": "speaker",
#             "quantity": 2,
#             "instrumentId": "a10",
#             "price": 2000,
#             "tradeDateTime": "2022-02-30T17:50:56",
#             "trader": "fcb",
#             "counterparty": "ananya",
#             "buySellIndicator": "sell",
#             "assetClass": "Commodities",
#             "tradeId": "t10"
#           }
#         }
#       ]
#     }
#   }