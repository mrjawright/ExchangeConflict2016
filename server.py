import redis

class redis_server():
	HOST='127.0.0.1'
	PORT='6379'
	PASSWORD='password'

	def __init__(host = None, port = None, password = None):
		if not host == None:
			HOST = host
		if not port == None:
			port = port
		if not password == None:
			password = password


srvr=redis_server()
r = redis.StrictRedis(host=srvr.HOST, port=srvr.PORT, password=srvr.PASSWORD)

p = r.pubsub()
p.subscribe('GAMEWORLD')

while True:
    for item in p.listen():
        print(item)
        print(item['data'])
