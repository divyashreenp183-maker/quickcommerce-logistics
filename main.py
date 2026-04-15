class Order:
    def __init__(self, id, location):
        self.id = id
        self.location = location


class Rider:
    def __init__(self, id, location, speed=1):
        self.id = id
        self.location = location
        self.speed = speed


class Store:
    def __init__(self, id, location):
        self.id = id
        self.location = location


# Sample Data
order1 = Order(1, (5, 5))
rider1 = Rider(1, (2, 3))
store1 = Store(1, (4, 4))

print("System Initialized Successfully")
