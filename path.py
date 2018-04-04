
class Node():
    def __init__(self, icao):
        self.name = icao
        self.distance = -1
        self.next_hop = None

    def __str__(self):
        return "{} is distance {} via {}".format(self.name, self.distance, self.next_hop)

    def set_next_hop(self,icao,distance):
        if self.distance > distance or self.distance < 0:
            self.next_hop = icao
            self.distance = distance
            return True
        else:
            return False

    def get_distance(self):
        return self.distance

    def get_next_hop(self):
        return self.next_hop

    def set_distance(self,metric):
        self.distance = metric

    def overwrite_next_hop(self, icao):
        self.next_hop = icao