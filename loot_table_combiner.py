"""
Merges all loot tables in a directory.
Currently uses "vanilla.json" as the default loot table.
Note: ignores non-entry modifications like functions, conditions, counts, weights, etc.
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
    print("Input table directory with a ""vanilla.json"" and other loot tables.")
    print("output is the name of the directory")
    directory = input()

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

    #init deletion table
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
        for j in range(len(deletionTable[i])-1,-1,-1):
            if deletionTable[i][j]:
                del baseTable.pools[i].entries[j]
    
    #remove deleted pools
    for i in range(len(deletionTable)-1,-1,-1):
        if len(baseTable.pools[i].entries) == 0 or not False in deletionTable[i]:
            del baseTable.pools[i]
    
    return baseTable

if __name__ == "__main__":
    main()
