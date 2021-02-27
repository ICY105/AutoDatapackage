"""
Object defination of a Minecrat loot table
"""

import json

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
        self.name = name
        self.type_ = None
        self.functions = []
        self.pools = []

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

        if('bonus_rolls' in jsonObject):
            self.bonus_rolls = numberProvider(jsonObject['bonus_rolls'])
            
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
                    self.functions.append(condition(f))

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

#container for "function" arguements. These are not parsed.
class function:
    def __init__(self, jsonObject):
        self.value = jsonObject

    def convert_to_dict(self):
        return self.value

#container for "number provider" arguements. These are not parsed.
class numberProvider:
    def __init__(self, jsonObject):
        self.value = jsonObject

    def convert_to_dict(self):
        return self.value

#container for "condition" arguements. These are not parsed.
class condition:
    def __init__(self, jsonObject):
        self.value = jsonObject

    def convert_to_dict(self):
        return self.value
