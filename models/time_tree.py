from typing import List
from datetime import datetime
from dataclasses import dataclass
from models.time_interval import TimeInterval
from models.time_tree_node import TimeTreeNode
from models.event import Event
from models.temporal_task import TemporalTask

@dataclass
class TimeTree:  
    _root: TimeTreeNode
    _size: int
    
    def __init__(self):
        self._root = None
        self._size = 0
        
    def _height(self, node: TimeTreeNode):
        if (not node):
            return 0
        return node.height
    
    def _get_balance(self, node: TimeTreeNode):
        if not node:
            return 0
        return self._height(node.left) - self._height(node.right)
    
    def _min_value_node(self, node: TimeTreeNode):
        current = node

        while current.left is not None:
            current = current.left

        return current
    
    def _left_rotate(self, node: TimeTreeNode):
        child_node = node.right
        grandchild_node = child_node.left

        child_node.left = node
        node.right = grandchild_node

        node.height = 1 + max(self._height(node.left), self._height(node.right))
        child_node.height = 1 + max(self._height(child_node.left), self._height(child_node.right))

        node.max = max(
            node.key.end_date,
            node.left.max if node.left else datetime.min,
            node.right.max if node.right else datetime.min
        )
        child_node.max = max(
            child_node.key.end_date,
            child_node.left.max if child_node.left else datetime.min,
            child_node.right.max if child_node.right else datetime.min
        )

        return child_node
    
    def _right_rotate(self, node: TimeTreeNode):
        child_node = node.left
        grandchild_node = child_node.right

        child_node.right = node
        node.left = grandchild_node

        node.height = 1 + max(self._height(node.left), self._height(node.right))
        child_node.height = 1 + max(self._height(child_node.left), self._height(child_node.right))

        node.max = max(
            node.key.end_date,
            node.left.max if node.left else datetime.min,
            node.right.max if node.right else datetime.min
        )
        child_node.max = max(
            child_node.key.end_date,
            child_node.left.max if child_node.left else datetime.min,
            child_node.right.max if child_node.right else datetime.min
        )

        return child_node
    
    def _insert_recursive(self, node: TimeTreeNode, event: Event, key: TimeInterval):
        if node is None:
            new_node = self._new_node(event, key)
            if (self._root is None):
                self._root = new_node
            self._size += 1
            return new_node
        
        if (key < node.key):
            node.left = self._insert_recursive(node.left, event, key)
        elif (key > node.key):
            node.right = self._insert_recursive(node.right, event, key)
        else:
            node.add_event(event)
            return node
        
        node.height = 1 + max(self._height(node.left), self._height(node.right))

        left_max = node.left.max if node.left else datetime.min
        right_max = node.right.max if node.right else datetime.min
        node.max = max(node.key.end_date, left_max, right_max)

        balance = self._get_balance(node)

        if balance > 1 and key < node.left.key:
            return self._right_rotate(node)

        if balance < -1 and key > node.right.key:
            return self._left_rotate(node)

        if balance > 1 and key > node.left.key:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)

        if balance < -1 and key < node.right.key:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node
    
    def _delete_node_recursive(self, node: TimeTreeNode, event: Event, key: TimeInterval):
        if node is None:
            return node
        
        if (key < node.key):
            node.left = self._delete_node_recursive(node.left, event, key)
        elif (key > node.key):
            node.right = self._delete_node_recursive(node.right, event, key)
        else:
            node.remove_event(event)
            
            if (node.get_num_events() == 0):
                    
                if node.left is None or node.right is None:
                    temp = node.left if node.left else node.right

                    if temp is None:
                        node = None
                    else:
                        node = temp

                else:
                    temp = self._min_value_node(node.right)
                    node.key = temp.key
                    node.events = temp.events
                    node.right = self._delete_node_recursive(node.right, event, temp.key)
                
                self._size -= 1

        if node is None:
            return node
        
        node.height = 1 + max(self._height(node.left), self._height(node.right))

        left_max = node.left.max if node.left else datetime.min
        right_max = node.right.max if node.right else datetime.min
        node.max = max(node.key.end_date, left_max, right_max)

        balance = self._get_balance(node)
        
        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._right_rotate(node)

        if balance > 1 and self._get_balance(node.left) < 0:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)

        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._left_rotate(node)

        if balance < -1 and self._get_balance(node.right) > 0:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)

        return node

    def _new_node(self, event: Event, key: TimeInterval):
        return TimeTreeNode(event, key)
    
    def _overlap_search_recursive(self, node: TimeTreeNode, interval: TimeInterval, overlaps: List):
        if node.key.is_overlapping(interval):
            overlaps.extend({"event": event, "time": node.key} for event in node.get_events())
            
        if node.left is not None and node.left.max >= interval.start_date:
            self._overlap_search_recursive(node.left, interval, overlaps)
        if node.right is not None and node.right.min <= interval.end_date:
            self._overlap_search_recursive(node.right, interval, overlaps)

    def _inorder_recursive(self, node: TimeTreeNode):
        if node is None:
            return
        
        self._inorder_recursive(node.left)
        print("[" + str(node.key.start_date) + ", " + str(node.key.end_date) + "]" + " max = " + str(node.max))
        self._inorder_recursive(node.right)

    def _print_tree_recursive(self, node: TimeTreeNode, prefix: str, is_left: bool):
        if node is not None:
            print(prefix + ("├── " if is_left else "└── ") + str(node.key) + f" ({node.get_num_events()} events) " + ("Left TimeTreeNode" if is_left else "Right Node"))
            self._print_tree_recursive(node.left, prefix + ("│   " if is_left else "    "), True)
            self._print_tree_recursive(node.right, prefix + ("│   " if is_left else "    "), False)

    def get_size(self):
        return self._size

    def insert(self, event: Event):
        if (not isinstance(event.get_task(), TemporalTask)):
            raise ValueError("Event task must be a TemporalTask to be inserted into TimeTree")
        for time_interval in event.schedule_intervals:
            self._root = self._insert_recursive(self._root, event, time_interval)

    def delete(self, event: Event):
        if (not isinstance(event.get_task(), TemporalTask)):
            raise ValueError("The only events in the tree are those with TemporalTask tasks")
        for time_interval in event.schedule_intervals:
            self._root = self._delete_node_recursive(self._root, event, time_interval)

    def search(self, key: TimeInterval):
        current = self._root
        while current is not None:
            if key == current.key:
                return current
            elif key < current.key:
                current = current.left
            else:
                current = current.right
        raise ValueError("Key not found in tree")

    def overlap_search(self, interval: TimeInterval):
        if self._root is None:
            return None
        overlaps = []
        self._overlap_search_recursive(self._root, interval, overlaps)

        return overlaps

    def sweepline_overlap_search(self, interval):
        """Finds all overlapping events within a given interval."""
        if not self._root:
            return {}
    
        overlapping_events = []
        self._overlap_search_recursive(self._root, interval, overlapping_events)
    
        points = []
        for e in overlapping_events:
            time = e["time"]
            event = e["event"]
            points.append((time, time.start_date, 1, event))
            points.append((time, time.end_date, -1, event))
        points.sort(key=lambda x: (x[1], -x[2]))
    
        active = set()
        overlaps = {}
    
        for time, pos, typ, event in points:
            formatted_event = (event, time)
            if typ == 1:
                for active_event in active:
                    
                    if (event, active_event[0]) not in overlaps:
                        overlaps[(event, active_event[0])] = set()
                    if (active_event[0], event) not in overlaps:
                        overlaps[(active_event[0], event)] = set()
                        
                    overlaps[(event, active_event[0])].add((time, active_event[1]))
                    overlaps[(active_event[0], event)].add((active_event[1], time))

                active.add(formatted_event)
            else:
                active.remove(formatted_event)
  
        return overlaps  
    
    def inorder(self):
        return self._inorder_recursive(self._root)

    def print_tree(self):
        self._print_tree_recursive(self._root, "", True)