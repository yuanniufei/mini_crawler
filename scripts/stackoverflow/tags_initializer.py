import redis

from crawlers.stackoverflow.constants import redis_stackoverflow_tags_page_key

redis_client = redis.StrictRedis(host='localhost', port=6379)
for i in range(500):
    redis_client.rpush(redis_stackoverflow_tags_page_key, i + 1)
