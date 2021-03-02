"""
Object defination of a Minecrat loot table
"""

import json
import math

#loads the give file location and creates a lootTable object
def load(f):
    fp = open(f, 'r')
    return lootTable(f,json.load(fp))

#saves the provided lootTable object at the provided location
def save(f, table):
    fp = open(f,'w')
    json.dump(table.convert_to_dict(), fp, indent=2)

def check_prefix(s):
    if not ':' in s:
        s = "minecraft:" + s
    return s

#container for a loot table file
class lootTable:

    def __init__(self, name, jsonObject):
        self.name = None
        self.type_ = None
        self.functions = []
        self.pools = []

        self.name = name
        if('type' in jsonObject):
            self.type_ = jsonObject['type']

            if('functions' in jsonObject):
                for f in jsonObject['functions']:
                    self.functions.append(function(f))

            if('pools' in jsonObject):
                for p in jsonObject['pools']:
                    self.pools.append(pool(p))

    #converts the object to a python dictonary, for use with saving
    def convert_to_dict(self):
        out = {
            "type":self.type_
        }
        if len(self.pools) > 0:
            out["pools"] = []
            for p in self.pools:
                out["pools"].append(p.convert_to_dict())
        if len(self.functions) > 0:
            out["functions"] = []
            for f in self.functions:
                out["functions"].append(f.convert_to_dict())
        return out

#container for pools in a loot table
class pool:

    def __init__(self, jsonObject):
        self.rolls = 0
        self.bonus_rolls = 0
        self.entries = []
        self.functions = []
        self.conditions = []

        if('rolls' in jsonObject):
            self.rolls = numberProvider(jsonObject['rolls'])
        else:
            self.rolls = numberProvider(0)

        if('bonus_rolls' in jsonObject):
            self.bonus_rolls = numberProvider(jsonObject['bonus_rolls'])
        else:
            self.bonus_rolls = numberProvider(0)
            
        if('entries' in jsonObject):
            for e in jsonObject['entries']:
                self.entries.append(entry(e))

        if('functions' in jsonObject):
            for f in jsonObject['functions']:
                self.functions.append(function(f))

        if('conditions' in jsonObject):
            for c in jsonObject['conditions']:
                self.conditions.append(condition(c))

    #converts the object to a python dictonary, for use with saving
    def convert_to_dict(self):
        out = {}
        if self.rolls != 0:
            out["rolls"] = self.rolls.convert_to_dict()
        if self.bonus_rolls != 0:
            out["bonus_rolls"] = self.bonus_rolls.convert_to_dict()
        if len(self.entries) > 0:
            out["entries"] = []
            for e in self.entries:
                out["entries"].append(e.convert_to_dict())
        if len(self.functions) > 0:
            out["functions"] = []
            for f in self.functions:
                out["functions"].append(f.convert_to_dict())
        if len(self.conditions) > 0:
            out["conditions"] = []
            for c in self.conditions:
                out["conditions"].append(c.convert_to_dict())
        return out

#container for entries in a pool
class entry:

    def __init__(self, jsonObject):
        self.type_ = None
        self.name = None
        self.weight = 1
        self.quality = 0
        self.conditions = []
        self.functions = []
        self.children = []
    
        if('type' in jsonObject):
            self.type_ = jsonObject['type']

            if('name' in jsonObject):
                self.name = jsonObject['name']

            if('weight' in jsonObject):
                self.weight = jsonObject['weight']

            if('quality' in jsonObject):
                self.quality = jsonObject['quality']

            if('conditions' in jsonObject):
                for c in jsonObject['conditions']:
                    self.conditions.append(condition(c))

            if('functions' in jsonObject):
                for f in jsonObject['functions']:
                    self.functions.append(function(f))

            if('children' in jsonObject):
                for c in jsonObject['children']:
                    self.children.append(entry(c))

    #converts the object to a python dictonary, for use with saving
    def convert_to_dict(self):
        out = {
            "type":self.type_
        }
        if self.name != None:
            out["name"] = self.name
        if self.weight != 1:
            out["weight"] = self.weight
        if self.quality != 0:
            out["quality"] = self.quality
        if len(self.conditions) > 0:
            out["conditions"] = []
            for c in self.conditions:
                out["conditions"].append(c.convert_to_dict())
        if len(self.functions) > 0:
            out["functions"] = []
            for f in self.functions:
                out["functions"].append(f.convert_to_dict())
        if len(self.children) > 0:
            out["children"] = []
            for c in self.children:
                out["children"].append(c.convert_to_dict())
        return out
    
    #returns true if the provided entry is considered equal to this entry
    def equals(self, entry):
        if check_prefix(self.type_) == "minecraft:alternatives" and check_prefix(entry.type_) == "minecraft:alternatives":
            for e1 in self.children:
                match = False
                for e2 in entry.children:
                    if e1.equals(e2):
                        match = True
                        break
                if not match:
                    return False
            return True
        else:
            return check_prefix(self.type_) == check_prefix(entry.type_) and check_prefix(self.name) == check_prefix(entry.name)

#container for "number provider" arguements.
class numberProvider:

    def __init__(self, jsonObject):
        self.value = 0
        self.type_ = None
        self.target = None
        self.score = None
        self.scale = 1
        self.min_ = 0
        self.max_ = 0
        self.p = 0
        self.n = 0

        try:
            self.value = float(jsonObject)
            self.type_ = "minecraft:constant"
        except ValueError:
            self.init_values(jsonObject)
        except TypeError:
            self.init_values(jsonObject)
        
        if self.type_ == None and (self.min_ != 0 or self.max_ != 0):
            self.type_ = "minecraft:uniform"

    def init_values(self, jsonObject):
        if self.value == 0:
            if('type' in jsonObject):
                self.type_ = jsonObject['type']
            if('min' in jsonObject):
                self.min_ = jsonObject['min']
            if('max' in jsonObject):
                self.max_ = jsonObject['max']
            if('p' in jsonObject):
                self.p = jsonObject['p']
            if('n' in jsonObject):
                self.n = jsonObject['n']
            if('target' in jsonObject):
                self.target = jsonObject['target']
            if('scale' in jsonObject):
                self.scale = jsonObject['scale']
            if('score' in jsonObject):
                self.score = jsonObject['score']

    def convert_to_dict(self):
        out = { "type": self.type_ }
        if self.type_ == "minecraft:constant":
            return round(self.value)
        elif self.type_ == "minecraft:uniform":
            out["min"] = math.floor(self.min_)
            out["max"] = math.ceil(self.max_)
            return out
        elif self.type_ == "minecraft:bionomal":
            out["p"] = self.p
            out["n"] = self.n
            return out
        elif self.type_ == "minecraft:score":
            out["target"] = self.target
            out["score"] = self.score
            if self.scale != 1:
                out["scale"] = self.scale
            return out
        else:
            return 0

    def get_average(self):
        if self.type_ == "minecraft:constant":
            return round(self.value)
        elif self.type_ == "minecraft:uniform":
            return (math.floor(self.min_) + math.ceil(self.max_))/2
        elif self.type_ == "minecraft:bionomal":
            return self.n
        elif self.type_ == "minecraft:score":
            return self.scale
        else:
            return 0

    #morphs value by scale
    #useful for growing/shrinking the size of pools
    def scale_value(self, scale):
        self.value *= scale
        self.min_ *= scale
        self.max_ *= scale
        self.n *= scale
        self.scale *= scale    
    
    #sets output scale
    def set_value(self, scale):
        self.value = scale
        self.min_ = scale
        self.max_ = scale
        self.n = scale
        self.scale = scale

#container for "function" arguements. These are not parsed.
class function:
    def __init__(self, jsonObject):
        self.name = None

        if('function' in jsonObject):
            self.name = jsonObject['function']
        self.value = jsonObject

    def equals(self, function):
        return self.name == function.name

    def convert_to_dict(self):
        return self.value

#container for "condition" arguements. These are not parsed.
class condition:
    def __init__(self, jsonObject):
        self.name = None
        
        if('condition' in jsonObject):
            self.name = jsonObject['condition']
        self.value = jsonObject

    def equals(self, condition):
        return self.name == condition.name

    def convert_to_dict(self):
        return self.value
