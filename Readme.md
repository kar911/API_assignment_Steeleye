## API Developer Assessment

## Test
### This tests represents a common request when building an API. You need to provide a set of endpoints for retrieving a 
- list of Trades
- retrieving a single Trade by ID, 
- searching against Trades
- filtering Trades
- Bonus points
## read the requierment file for installing Packages

# Solution 



## to use the code user must have `hostID` and `APIkey` and Elasticsearch index named `trade` with data
### editable in 
>es = Elasticsearch(
>>    cloud_id="cloudID"  ,
>>    api_key="apiKey" 
>>                    # or use host = "<local_host>"
>)

## the solution I present is using get method ( assuming " `If a user was to call your endpoint and provide a ?search=bob%20smith` " )

## Fast api is used with non async requests which can be help with large amout of request
<br>

## Listing trades

- ## provided with endpoint `/listAll`
- ## `http://127.0.0.1:8000/listAll?size=20&page=2&order=dec&on=tradeID`
- ## it gives all the data in indexes
### Bonus points

- ### provided with endpoint parameters
- ### `size:(int >=1) =` as the number of rows  
- ### `page:(int >=1) =` is which page
- ### `on: str =` is column want to sort on
- ### `order: str=` is 'asc' or 'desc'

<br>

## Single trade

- ## provided with endpoint `/singleId`
- ## `http://127.0.0.1:8000/singleId?id=12ad`
- ### provided with endpoint parameters
- ### `id=` id user searching

<br>

## Searching trades

- ## provided with endpoint `/searchT`
- ## `http://127.0.0.1:8000/searchT?query=Goods`
- ### provided with endpoint parameters
- ### `query=` term user want to search in any of the listed column

<br>

## Advanced filtering

- ## provided with endpoint `/AdvanccFilter`
- ## uses parameters endpoint `/AdvanccFilter`
- ### `http://127.0.0.1:8000/AdvanccFilter?tradeType=BUY&maxPrice=21&minPrice=12&end=2012-05-30T18%3A52%3A56&start=2012-02-29T18%3A52%3A56&assetClass=Commodities`

<br>

- ### provided with endpoint parameters
- ### `tradeType : str["BUY","SELL"]=` as the number of rows  
- ### `maxPrice : int=` The maximum value for the tradeDetails.price field.
- ### `minPrice : int=` The minimum value for the tradeDetails.price field.
- ### `end : datetime=` The maximum date for the tradeDateTime field.
- ### `start : datetime=` The minimum date for the tradeDateTime field.
- ### `assetClass=` Asset class of the trade.

<br>

## use of components
>## `from fastapi import FastAPI, Depends, Query #nessary imports form fastapi`
- ### FastAPI: This is the main FastAPI class that you will use to create your API. It provides a number of features, such as routing, validation, and documentation.
- ### Depends: This is a dependency injection helper class that allows you to inject dependencies into your endpoints.
- ### Query: This is a class that allows you to parse query parameters from the request URL.

<br>

>## `from pydantic import BaseModel, validator, root_validator, conint, constr, DateTimeError, Field #pydantic imports`

- ### BaseModel: This is a base class that provides a number of features for validating and serializing data.
- ### validator: This is a decorator that can be used to add custom validation logic to a model.
- ### root_validator: This is a validator that is applied to the entire model.` I used it for comparison of two parameters`
- ### conint: This is a type that represents an integer.
- ### constr: This is a type that represents a custom constraint.
- ### DateTimeError: This is an exception that is raised when a date or time value is invalid.
- ### Field: This is a class that represents a field in a model.

<br>

>## `from elasticsearch import Elasticsearch, TransportError, ConnectionError`
- ### Elasticsearch: This is the main Elasticsearch class that you will use to interact with Elasticsearch.
- ### TransportError: This is an exception that is raised when there is a problem with the Elasticsearch transport layer.
- ### ConnectionError: This is an exception that is raised when there is a problem connecting to Elasticsearch.
