import pygame
import src.core.utils as utils
import json
import queue
import src.entities.objects as o
import src.constants as c
import src.config as config

class Edge():
    def __init__(self, id, weight):
        self.id = id
        self.weight = weight

class Graph():
    """Represents a graph. Used to model where sprites can move on map."""
    
    def __init__(self):
        self.adj_list = {}

    def populate(self, data):
        for i in range(len(data)):
            if data[i] in c.WALKABLE_TILES:
                self.add_node(i, data)

    def add_node(self, nodeid, data):
        self.adj_list[nodeid] = []
        neighbors = [
            Edge(nodeid - c.MAP_WIDTH - 1, 1.4), 
            Edge(nodeid - c.MAP_WIDTH + 1, 1.4), 
            Edge(nodeid - c.MAP_WIDTH, 1), 
            Edge(nodeid + c.MAP_WIDTH, 1), 
            Edge(nodeid + c.MAP_WIDTH + 1, 1.4),
            Edge(nodeid + c.MAP_WIDTH - 1, 1.4),
            Edge(nodeid - 1, 1),
            Edge(nodeid + 1, 1)
        ] # walkable tiles are never on the edge
        for n in neighbors:
            if data[n.id] in c.WALKABLE_TILES:
                self.adj_list[nodeid].append(n)
    
    def dijkstra(self, src, dest):
        """Run dijkstras on graph, stopping when path to dest is found."""
        tovisit = []
        pq = queue.PriorityQueue()
        dist = {}
        prev = {}
        for k in self.adj_list.keys():
            if k == src:
                dist[k] = 0
            else:
                dist[k] = float('inf')
            prev[k] = None
            tovisit.append(k)
        pq.put((dist[src], src))
        
        while not pq.empty():
            _, node = pq.get()
            if node not in tovisit:
                continue
            if node == dest:
                break
            tovisit.remove(node)
            for neighbor in self.adj_list[node]:
                if neighbor.id in tovisit:
                    alt = dist[node] + neighbor.weight
                    if alt < dist[neighbor.id]:
                        dist[neighbor.id] = alt
                        prev[neighbor.id] = node
                        pq.put((dist[neighbor.id], neighbor.id))
        return dist, prev

class Map():
    """Parses exported map data from Tiled."""

    def __init__(self, imageFile, dataFile):
        """Constructor.
        
            imageFile: background of the map in .png format
            dataFile: map data exported from Tiled in .json format
        """
        self.image, _ = utils.load_png(imageFile)
        self.graph = Graph()
        self.walls = {}
        self.doors = {}
        self.laserDoors = {}
        self.computers = {}
        self.generatedComputers = {}
        self.objects = {}
        self.playerSpawn = None
        self.roombaPath = None

        self.load_json(dataFile)
        self.parse_doors()
        self.parse_objects()

    def load_json(self, filename : str):
        """Load JSON data for the map."""
        f = open(config.resource_path(config.MAP_DIR / filename))
        self.rawJson = json.load(f)
        layers = self.rawJson["layers"]
        for layer in layers:
            if layer["name"] == "walls":
                self.walls = layer
            elif layer["name"] == "doors":
                self.doors = layer
            elif layer["name"] == "objects":
                self.objects = layer
            elif layer["name"] == "playerSpawn":
                self.playerSpawn = (
                    layer["objects"][0]["x"],
                    layer["objects"][0]["y"]
                )
            elif layer["name"] == "roombaPath":
                roombaPathRaw = layer["objects"][0]
                self.roombaPath = self.parse_polyline(
                    roombaPathRaw["polyline"],
                    roombaPathRaw["x"],
                    roombaPathRaw["y"]
                )
    
    def parse_polyline(self, polyline, startX, startY):
        """Parse a polyline into array of Vector2 points."""
        return [
            pygame.Vector2(point["x"] + startX, point["y"] + startY) 
            for point in polyline
        ]

    def parse_object(self, object, internalDict):
        """Parse object and add to internal dictionary."""
        id = object["id"]
        internalDict[id] = {
            "width": object["width"],
            "height": object["height"],
            "x": object["x"],
            "y": object["y"]
        }
        if "properties" in object.keys():
            for property in object["properties"]:
                internalDict[id][property["name"]] = property["value"]
    
    def parse_objects(self):
        """Parse the objects layer of the JSON data."""
        for object in self.objects["objects"]:
            if object["type"] == "Computer":
                self.parse_object(object, self.computers)
    
    def parse_doors(self):
        """Parse the laserDoor layer of the JSON data."""
        for door in self.doors["objects"]:
            if door["type"] == "LaserDoor":
                self.parse_object(door, self.laserDoors)

    def computer_factory(self, computer, id, startX, startY):
        """Generates a computer from an entry in the internal computer dict."""
        generatedComputer = None
        if "hasProblem" in computer.keys() and computer["hasProblem"]:
            generatedComputer = o.ProblemComputer(
                pygame.Rect(
                    startX + computer["x"],
                    startY + computer["y"] - computer["height"],
                    computer["width"],
                    computer["height"]
                ),
                computer["note"],
                computer["problemUrl"]
            ) 
        else:
            generatedComputer = o.Computer(
                pygame.Rect(
                    startX + computer["x"],
                    startY + computer["y"] - computer["height"],
                    computer["width"],
                    computer["height"]
                ),
                computer["note"] if "note" in computer.keys() else "TODO"
            )
        self.generatedComputers[id] = generatedComputer
        return generatedComputer

    def laser_door_factory(self, laserDoor, startX, startY):
        """Generates a laser door from an entry in the internal laser door dict."""
        door = o.LaserDoor(
            pygame.Rect(
                startX + laserDoor["x"],
                startY + laserDoor["y"],
                laserDoor["width"],
                laserDoor["height"]
            )
        )
        if "brokenComputer" in laserDoor.keys():
            computerId = laserDoor["brokenComputer"]
            door.problems.add(self.generatedComputers[computerId])
        return door
    
    def exit_door_factory(self, exitDoor, startX, startY):
        """Generates an exit door."""
        
    
    def doors_factory(self):
        """Get all the doors for this map as a sprite group."""
        startX = self.doors["x"]
        startY = self.doors["y"]
        doorGroup = pygame.sprite.Group()
        for door in self.doors["objects"]:
            if door["type"] == "LaserDoor":
                laserDoor = self.laserDoors[door["id"]]
                doorGroup.add(self.laser_door_factory(laserDoor, startX, startY))
        return doorGroup

    def object_factory(self) -> pygame.sprite.Group:
        """Get the objects for this map as a sprite group."""
        startX = self.objects["x"]
        startY = self.objects["y"]
        objectGroup = pygame.sprite.Group()
        for object in self.objects["objects"]:
            if object["type"] == "Computer":
                computer = self.computers[object["id"]]
                objectGroup.add(self.computer_factory(computer, object["id"], startX, startY))
            elif object["type"] == "DanceFloor":
                objectGroup.add(
                    o.DanceFloor((startX + object["x"], startY + object["y"] - object["height"]))
                )
            elif object["type"] == "ExitDoor":
                objectGroup.add(
                    o.ExitDoor(
                        pygame.Rect(
                            startX + object["x"],
                            startY + object["y"],
                            object["width"],
                            object["height"]
                        )
                    )
                )
        return objectGroup

    def walls_factory(self):
        """Generates the walls for this map as a list of rects."""
        startX = self.walls["x"]
        startY = self.walls["y"]
        wallRects = []
        for wall in self.walls["objects"]:
            wallRects.append(
                pygame.Rect(
                    (startX + wall["x"], startY + wall["y"]),
                    (wall["width"], wall["height"])
                )
            )
        return wallRects

    def draw(self, surface, offset):
        """Draw map background to surface."""
        surface.blit(self.image, offset)
