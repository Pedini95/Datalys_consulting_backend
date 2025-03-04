import redis
import json

class RedisTemplate:
    host = "192.168.7.129"
    port = "6379"
    password = "QoYJqOwtmOspiooEGpZc"
    def __init__(self, host, port, password=None):
        self.host = host
        self.port = port
        self.password = password
        self.client = redis.Redis(host=self.host, port=self.port, password=self.password)

    def set(self, key, value, ex=None):
        self.client.set(key, value, ex=ex)

    def get(self, key):
        return self.client.get(key)
    
    def delete(self, key):
        self.client.delete(key)

    def set_json(self, key, value, ex=None):
        self.client.set(key, json.dumps(value), ex=ex)

    def get_json(self, key):
        value = self.client.get(key)
        return json.loads(value) if value else None
    
    def expire(self, key, time):
        self.client.expire(key, time)

# Utilisation de RedisTemplate
if __name__ == "__main__":
    redis_template = RedisTemplate()

    # Définir une clé avec une expiration
    redis_template.set('my_key', 'my_value', ex=10)
    print(redis_template.get('my_key'))  # Sortie : my_value

    # Attendre l'expiration
    import time
    time.sleep(10)
    print(redis_template.get('my_key'))  # Sortie : None

    # Définir une clé avec un objet JSON
    data = {'name': 'John', 'age': 30}
    redis_template.set_json('user:1000', data)
    print(redis_template.get_json('user:1000'))  # Sortie : {'name': 'John', 'age': 30}

    # Supprimer une clé
    redis_template.delete('user:1000')
    print(redis_template.get('user:1000'))  # Sortie : None