
class Node:
    def __init__(self, parent):
        self.ancestors = 0
        self.children = []
        if(parent != None):
            self.parent = parent
            self.level = parent.level + 1
        else:
            self.parent = None
            self.level = 0
  
    def add(word):
        
    def remove(word):