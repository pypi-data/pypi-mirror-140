from pybit.inverse_perpetual import HTTP

# Unauthenticated
session_unauth = HTTP(endpoint='https://api.bybit.com')

# Authenticated
session_auth = HTTP(
    endpoint='https://api.bybit.com',
    api_key='...',
    api_secret='...'
)

print(session_unauth.orderbook(symbol="BTCUSD"))