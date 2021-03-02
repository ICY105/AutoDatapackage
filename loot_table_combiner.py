"""
Merges all loot tables in a directory.
Currently uses "vanilla.json" as the default loot table.
Current Limitations:
    1. If a new table modifies an existing entry (ie. adds a condition 'only drop apples
       in forest biome'), and another new table removes the modified entry and
       replaces it with a new entry, (ie. removes 'apple' and adds 'green apple'),
       then the modifications are lost (that is, the condition of 'apples only drop
       in forest biomes' does not get applied to green apples)

    2. Modified conditions and functions don't get merged. For example, a base table
       pool has the condition 'random chance = 0.5', and a new table modifies this to
       'random chance = 0.75', then the value will stay 0.5 and won't be changed.

    3. Doesn't handle base table pools with the multiple occurences of the same entry
       name very well (for example, if a pool has multiple 'alternitives' entries)
"""

from os import listdir
from os.path import isfile, join

import json
import loot_table

class comparision:

    #generates a comparision of both tables, listing additions and deletions
    def __init__(self, baseTable, newTable): 
        self.bt = baseTable
        self.nt = newTable
        self.pool_map = self.compare_pools()

    #compares pools in both tables to detemine which pools map to each other
    #returns mappings in the style of [(bt_pool_index,nt_pool_index)]
    def compare_pools(self):
        pools = []
        for p1 in self.bt.pools:
            matches = []
            for p2 in self.nt.pools:
                matches.append(self.compare_pool(p1, p2))
            pools.append(matches)

        pool_map = []
        mapped = []
        for i in range(len(pools)):
            max_value = 0
            max_index = -1
            for j in range(len(pools[i])):
                if not j in mapped and pools[i][j] > max_value:
                    max_value = pools[i][j]
                    max_index = j
            if max_index > -1:
                mapped.append(max_index)
                pool_map.append((i,max_index))
        return pool_map

    #compares which entries in p1 are in p2
    #returns the standard error of misses
    def compare_pool(self, p1, p2):
        misses = 0
        for entry1 in p1.entries:
            miss = True
            for entry2 in p2.entries:
                if entry1.equals(entry2):
                    miss = False
                    break
            if miss:
                misses += 1
        if misses == 0:
            return 1
        else:
            return (len(p1.entries)-misses)/misses

    #returns a list of pool indexes in new table that are not in base table
    def get_added_pools(self):
        out = []
        for i in range(len(self.nt.pools)):
            new = True
            for s in self.pool_map:
                if s[1] == i:
                    new = False
                    break
            if new:
                out.append(i)
        return out

    #returns a list of pool indexes in base table that are not in the new table
    def get_deleted_pools(self):
        out = []
        for i in range(len(self.bt.pools)):
            deleted = True
            for s in self.pool_map:
                if s[0] == i:
                    deleted = False
                    break
            if deleted:
                out.append(i)
        return out

    #returns a list of entry indexs in given base pool index that are not in its mapping
    #returns None if pool is not mapped
    def get_pool_deletions(self, pool):
        mapping = (-1,-1)
        for i in range(len(self.pool_map)):
            if self.pool_map[i][0] == pool:
                mapping = self.pool_map[i]
                break
        if mapping[0] != -1:
            bp = self.bt.pools[mapping[0]]
            np = self.nt.pools[mapping[1]]
            out = []
            for i in range(len(bp.entries)):
                deleted = True
                for entry in np.entries:
                    if bp.entries[i].equals(entry):
                        deleted = False
                        break
                if deleted:
                    out.append(i)
            return out
        else:
            return None

    #returns a list of entry indexs not in given base pool index that are in its mapping
    #returns None if pool is not mapped
    def get_pool_additions(self, pool):
        mapping = (-1,-1)
        for i in range(len(self.pool_map)):
            if self.pool_map[i][0] == pool:
                mapping = self.pool_map[i]
                break
        if mapping[0] != -1:
            bp = self.bt.pools[mapping[0]]
            np = self.nt.pools[mapping[1]]
            out = []
            for i in range(len(np.entries)):
                added = True
                for entry in bp.entries:
                    if np.entries[i].equals(entry):
                        added = False
                        break
                if added:
                    out.append(i)
            return out
        else:
            return None

def main():
    #print("Input directory with a ""vanilla.json"" and other loot tables.")
    #print("output is the name of the directory")
    #directory = input()
    directory = "test_cases/wheat"

    files = [f for f in listdir(directory) if isfile(join(directory, f))]
    tables = []
    baseTable = None
    for f in files:
        table = loot_table.load(directory + "/" + f)
        if f == "vanilla.json":
            baseTable = table
        else:
            tables.append(table)
    if baseTable == None:
        print("No default loot table found")
    else:
        table = mergeTables(baseTable,tables)
        loot_table.save(f'{directory}.json',table)

#merges a list of tables onto a base table
def mergeTables(baseTable,tables):
    comparisions = []
    for table in tables:
        if not baseTable.type_ == table.type_:
            print(f'Warning -- table {table.name} has a differnt type then base table')
        if len(table.pools) == 0:
            print(f'Error -- table {table.name} is empty')
        else:
            comparisions.append(comparision(baseTable,table))

    ### add/remove pools and entries

    #init marking tables
    deletionTable = []
    for pool in baseTable.pools:
        deletionTable.append([False] * len(pool.entries))

    #mark any deleted entries
    for comp in comparisions:
        for i in range( len(comp.pool_map) ):
            deletions = comp.get_pool_deletions(comp.pool_map[i][0])
            for j in deletions:
                deletionTable[comp.pool_map[i][0]][j] = True
    
    #fill any deleted pool to all true
    for comp in comparisions:
        for i in comp.get_deleted_pools():
            for j in range(len(deletionTable[i])):
                deletionTable[i][j] = True
    
    #merge pool conditions
    for comp in comparisions:
        for function in comp.nt.functions:
            if not any(f.equals(function) for f in baseTable.functions):
                baseTable.functions.append(function)    

    #merges pool factors
    for i in range(len(baseTable.pools)):
        new_pools = []
        for comp in comparisions:
            for mapping in comp.pool_map:
                if mapping[0] == i:
                    new_pools.append(comp.nt.pools[mapping[1]])
        if len(new_pools) > 0:
            merge_pool_factors(baseTable.pools[i], new_pools)
    
    #append new entries to existing tables
    for comp in comparisions:
        for mapping in comp.pool_map:
            for j in comp.get_pool_additions(mapping[0]):
                baseTable.pools[mapping[0]].entries.append(comp.nt.pools[mapping[1]].entries[j])

    #append new tables
    for comp in comparisions:
        for i in comp.get_added_pools():
            baseTable.pools.append(comp.nt.pools[i])
    
    #remove deleted entries
    for i in range(len(deletionTable)-1,-1,-1):
        count = len(baseTable.pools[i].entries)
        for j in range(len(deletionTable[i])-1,-1,-1):
            if deletionTable[i][j]:
                del baseTable.pools[i].entries[j]
        if len(baseTable.pools[i].entries) > 0:
            baseTable.pools[i].rolls.scale_value( count/len(baseTable.pools[i].entries) )
    
    #remove deleted pools
    for i in range(len(deletionTable)-1,-1,-1):
        if len(baseTable.pools[i].entries) == 0 or not False in deletionTable[i]:
            del baseTable.pools[i]
    
    return baseTable

#merges 'new pool list' (npl) onto 'base pool' (bp)
def merge_pool_factors(bp, npl):
    #scale rolls
    value = 0
    for pool in npl:
        value += pool.rolls.get_average()
    print(value)
    value /= len(npl)
    if bp.rolls.get_average() != 0:
        bp.rolls.scale_value( value/bp.rolls.get_average() )
    else:
        bp.rolls.set_value(value)

    #scale bonus rolls
    value = 0
    for pool in npl:
        value += pool.bonus_rolls.get_average()
    if bp.bonus_rolls.get_average() != 0:
        bp.bonus_rolls.scale_value( (value/len(npl))/bp.bonus_rolls.get_average() )
    else:
        bp.bonus_rolls.set_value(value)

    #merge functions
    for pool in npl:
        for function in pool.functions:
            if not any(f.equals(function) for f in bp.functions):
                bp.functions.append(function)    

    #merge conditions
    for pool in npl:
        for condition in pool.conditions:
            if not any(c.equals(condition) for c in bp.conditions):
                bp.conditions.append(condition)

    #merge entries
    for entry in bp.entries:
        entries = []
        for pool in npl:
            for entry2 in pool.entries:
                if entry.equals(entry2):
                    entries.append(entry2)
        merge_entries(entry, entries)

#merges 'new entry list' (nel) onto 'base entry' (be)
def merge_entries(be, nel):
    #scale weight
    value = 0
    for entry in nel:
        value += entry.weight
    be.weight = value/len(nel)

    #scale quality
    value = 0
    for entry in nel:
        value += entry.quality
    be.quality = value/len(nel)

    #merge functions
    for pool in nel:
        for function in pool.functions:
            if not any(f.equals(function) for f in be.functions):
                be.functions.append(function)

    #merge conditions
    for pool in nel:
        for condition in pool.conditions:
            if not any(c.equals(condition) for c in be.conditions):
                be.conditions.append(condition)

    #merge children
    for entry in be.children:
        entries = []
        for entry2 in nel:
            for entry3 in entry2.children:
                if entry.equals(entry3):
                    entries.append(entry3)
        merge_entries(entry, entries)


if __name__ == "__main__":
    main()
