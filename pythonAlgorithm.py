import heapq
import random
import time
import sys
import os
import platform
from collections import defaultdict, deque
from colorama import Fore, Back, Style, init

import numpy as np

init(autoreset=True)

CELL_WIDTH = 4


class Terminal:
    @staticmethod
    def up(n=1):
        sys.stdout.write(f"\033[{n}A")

    @staticmethod
    def down(n=1):
        sys.stdout.write(f"\033[{n}B")

    @staticmethod
    def right(n=1):
        sys.stdout.write(f"\033[{n}C")

    @staticmethod
    def left(n=1):
        sys.stdout.write(f"\033[{n}D")

    @staticmethod
    def home():
        sys.stdout.write("\033[H")

    @staticmethod
    def clearLine():
        sys.stdout.write("\033[K")

    @staticmethod
    def hideCursor():
        sys.stdout.write("\033[?25l")

    @staticmethod
    def showCursor():
        sys.stdout.write("\033[?25h")

    @staticmethod
    def flush():
        sys.stdout.flush()

    @staticmethod
    def reset():
        sys.stdout.write("\033[0m")

    @staticmethod
    def setCursorHighlight():
        sys.stdout.write("\033[42;30m")


def getChar():
    if os.name == "nt":
        import msvcrt

        ch = msvcrt.getch()
        if ch in (b"\x00", b"\xe0"):
            ch2 = msvcrt.getch()
            if ch2 == b"H":
                return "up"
            if ch2 == b"P":
                return "down"
            return ""
        return ch.decode("utf-8", errors="ignore")
    else:
        import tty
        import termios

        fd = sys.stdin.fileno()
        oldSettings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                ch2 = sys.stdin.read(1)
                if ch2 == "[":
                    ch3 = sys.stdin.read(1)
                    if ch3 == "A":
                        return "up"
                    if ch3 == "B":
                        return "down"
                    if ch3 == "C":
                        return "right"
                    if ch3 == "D":
                        return "left"
                return ""
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, oldSettings)
        if ch == "\x03":
            sys.exit(0)
        return ch


class SeqList:
    def __init__(self, size=100):
        self.MAXSIZE = size
        self.length = 0
        self.data = [None for x in range(0, self.MAXSIZE)]

    def _resize(self):
        oldMaxsize = self.MAXSIZE
        self.MAXSIZE = oldMaxsize * 2
        newData = [None for i in range(self.MAXSIZE)]
        for i in range(self.length):
            newData[i] = self.data[i]
        self.data = newData
        print("SeqList has resized: " + Fore.GREEN + f"{oldMaxsize}->{self.MAXSIZE}")

    def isFull(self):
        if self.length >= self.MAXSIZE:
            return True
        return False

    def isEmpty(self):
        if self.length == 0:
            return True
        return False

    def append(self, value):
        if self.isFull():
            self._resize()
        self.data[self.length] = value
        self.length += 1

    def find(self, value):
        if self.isEmpty():
            return False
        for i in range(self.length):
            if self.data[i] == value:
                return True
        return False

    def getByIndex(self, index):
        if not isinstance(index, int):
            raise TypeError
        if self.isEmpty():
            return None
        return self.data[index]

    def insert(self, index, value):
        if self.isFull():
            self._resize()
        if not isinstance(index, int):
            raise TypeError
        if index > self.length or index < 0:
            raise AttributeError("Trying to insert into a not-exist place")
        for iCurrentIndex in range(self.length, index, -1):
            self.data[iCurrentIndex] = self.data[iCurrentIndex - 1]
        self.data[index] = value
        self.length += 1
        return True

    def display(self):
        if self.isEmpty():
            print("SeqList is empty")
            return True
        print(*(self.data[: self.length]), sep=" ", end="\n", flush=True)
        return True

    def destroyList(self):
        self.__init__()


class LinkListNode:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkList:
    def __init__(self):
        self.head = LinkListNode(None)

    def isEmpty(self):
        if self.head.next is None:
            return True
        return False

    def pushBack(self, data):
        p = self.head
        while p.next is not None:
            p = p.next
        p.next = LinkListNode(data)

    def getElem(self, index):
        if self.isEmpty():
            raise MemoryError("Linklist is empty")
        p = self.head.next
        nCnt = 0
        while p is not None:
            if nCnt == index:
                return p.data
            nCnt += 1
            p = p.next
        raise IndexError("No such index(index too big)")

    def insert(self, index, data):
        if self.isEmpty():
            self.pushBack(data)
        else:
            p = self.head.next
            pre = self.head
            nCnt = 0
            while p.next is not None:
                if nCnt == index:
                    break
                nCnt += 1
                pre = pre.next
                p = p.next
            if p.next is None and nCnt != index:
                raise IndexError("Out of range")
            newNode = LinkListNode(data)
            newNode.next = p
            pre.next = newNode

    def delete(self, index):
        p = self.head.next
        pre = self.head
        nCnt = 0
        while p is not None:
            if nCnt == index:
                pre.next = p.next
                pdata = p.data
                del p
                return pdata
            nCnt += 1
            pre = pre.next
            p = p.next
        raise IndexError("There is no such index")

    def remove(self, data):
        p = self.head.next
        pre = self.head
        while p is not None:
            if p.data == data:
                pre.next = p.next
                del p
                return True
            pre = pre.next
            p = p.next
        raise ValueError("There is no such data")

    def _getMid(self, node):
        if node is None:
            return None
        pSlow = node
        pFast = node
        while pFast.next is not None and pFast.next.next is not None:
            pSlow = pSlow.next
            pFast = pFast.next.next
        return pSlow

    def _mergeSortRecursiveA(self, head):
        if head is None or head.next is None:
            return head
        mid = self._getMid(head)
        leftHalf = head
        rightHalf = mid.next
        mid.next = None
        left = self._mergeSortRecursiveA(leftHalf)
        right = self._mergeSortRecursiveA(rightHalf)
        return MergeLinkListA(left, right)

    def _mergeSortRecursiveD(self, head):
        if head is None or head.next is None:
            return head
        mid = self._getMid(head)
        leftHalf = head
        rightHalf = mid.next
        mid.next = None
        left = self._mergeSortRecursiveD(leftHalf)
        right = self._mergeSortRecursiveD(rightHalf)
        return MergeLinkListD(left, right)

    def getLength(self):
        nCnt = 0
        p = self.head.next
        while p:
            p = p.next
            nCnt += 1
        return nCnt

    def display(self):
        print("head", end="")
        p = self.head.next
        nCnt = 0
        while p is not None:
            nCnt += 1
            print(f" -> {p.data}", end="")
            if nCnt % 4 == 0:
                print("\n     ", end="")
            p = p.next
        print(" -> None")

    def mergeSortA(self):
        if self.head.next is not None:
            self.head.next = self._mergeSortRecursiveA(self.head.next)

    def mergeSortD(self):
        if self.head.next is not None:
            self.head.next = self._mergeSortRecursiveD(self.head.next)


def MergeLinkListN(la, lb):
    if la.head.next is None:
        return lb
    if lb.head.next is None:
        return la
    pa = la.head.next
    pb = lb.head.next
    lm = LinkList()
    while pa is not None and pb is not None:
        if pa.data > pb.data:
            lm.pushBack(pb.data)
            pb = pb.next
        else:
            lm.pushBack(pa.data)
            pa = pa.next
    while pa is not None:
        lm.pushBack(pa.data)
        pa = pa.next
    while pb is not None:
        lm.pushBack(pb.data)
        pb = pb.next
    return lm


def MergeLinkListA(la, lb):
    dummy = LinkListNode(0)
    p = dummy
    while la is not None and lb is not None:
        if la.data < lb.data:
            p.next = la
            la = la.next
        else:
            p.next = lb
            lb = lb.next
        p = p.next
    if la is not None:
        p.next = la
    if lb is not None:
        p.next = lb
    return dummy.next


def MergeLinkListD(la, lb):
    dummy = LinkListNode(0)
    p = dummy
    while la is not None and lb is not None:
        if la.data > lb.data:
            p.next = la
            la = la.next
        else:
            p.next = lb
            lb = lb.next
        p = p.next
    if la is not None:
        p.next = la
    if lb is not None:
        p.next = lb
    return dummy.next


class TreeNode:
    def __init__(self, data, lchild=None, rchild=None):
        self.data = data
        self.lchild = lchild
        self.rchild = rchild


class BiTree:
    def __init__(self):
        self.root = TreeNode(None)
        self.maxIndex = 0

    def createBiTree(self, vals):
        if len(vals) == 0:
            return None
        if vals[0] != "#":
            node = TreeNode(vals[0])
            if self.maxIndex == 0:
                self.root = node
            self.maxIndex += 1
            vals.pop(0)
            node.lchild = self.createBiTree(vals)
            node.rchild = self.createBiTree(vals)
            return node
        else:
            vals.pop(0)
            return None

    def preOrderTraverse(self, t):
        if t:
            print(f"{t.data}", end=" ")
            self.preOrderTraverse(t.lchild)
            self.preOrderTraverse(t.rchild)

    def inOrderTraverse(self, t):
        if t:
            self.inOrderTraverse(t.lchild)
            print(f"{t.data}", end=" ")
            self.inOrderTraverse(t.rchild)

    def postOrderTraverse(self, t):
        if t:
            self.postOrderTraverse(t.lchild)
            self.postOrderTraverse(t.rchild)
            print(f"{t.data}", end=" ")

    def levelTraverse(self, t):
        if t is None:
            return
        queue = []
        queue.append(t)
        while queue:
            p = queue.pop(0)
            print(f"{p.data}", end=" ")
            if p.lchild:
                queue.append(p.lchild)
            if p.rchild:
                queue.append(p.rchild)
        print()

    def locateAndPrintPath(self, t, val):
        if t is None:
            print("Empty tree")
            return False
        queue = []
        queue.append(t)
        while queue:
            p = queue.pop(0)
            print(f"{p.data}", end=" ")
            if p.lchild:
                queue.append(p.lchild)
            if p.rchild:
                queue.append(p.rchild)
            if p.lchild is None and p.rchild is None:
                print(f"\nleaf node reached, which is {p.data}")
            if p.data == val:
                print(f"\n{p.data} found")
                return True
        return False

    def countLeafNode(self, t):
        if t is None:
            print("Empty tree")
            return 0
        if t.lchild is None and t.rchild is None:
            return 1
        return self.countLeafNode(t.lchild) + self.countLeafNode(t.rchild)

    def createBiTreeLevelOrder(self, vals):
        if len(vals) == 0 or vals[0] == "#" or vals[0] is None:
            self.root = None
            return None
        root = TreeNode(vals[0])
        self.root = root
        queue = deque([root])
        i = 1
        while queue and i < len(vals):
            cur = queue.popleft()
            if i < len(vals) and vals[i] is not None:
                if vals[i] != "#":
                    cur.lchild = TreeNode(vals[i])
                    queue.append(cur.lchild)
                i += 1
            if i < len(vals) and vals[i] is not None:
                if vals[i] != "#":
                    cur.rchild = TreeNode(vals[i])
                    queue.append(cur.rchild)
                i += 1
        return root


# C++ style graph with adj matrix
class Graph:
    def __init__(self, n, e=0):
        self.verticle = n
        self.edge = e
        self.graph = np.full((n + 1, n + 1), np.inf)
        self.path = []
        self.visited = [False] * (n + 1)
        self.res = []

    def createEdge(self, start, end, distance=1):
        if distance < 0:
            raise ValueError("Dijkstra cannot handle negative value")
        self.graph[start][end] = distance
        self.graph[end][start] = distance
        self.edge += 1

    def dfs(self, cur, end):
        if cur == end:
            self.res.append(list(self.path))
            return

        for i in range(1, self.verticle + 1):
            if self.graph[cur][i] != np.inf and not self.visited[i]:
                self.visited[i] = True
                self.path.append(i)
                self.dfs(i, end)
                self.path.pop()
                self.visited[i] = False

    def findPathDFS(self, start, end):
        self.res = []
        self.path = [start]
        self.visited = [False] * (self.verticle + 1)
        self.visited[start] = True
        self.dfs(start, end)
        return self.res

    def dijkstra(self, start, end):
        distances = {i: np.inf for i in range(1, self.verticle + 1)}
        distances[start] = 0
        preNodes = {i: None for i in range(1, self.verticle + 1)}
        pq = [(0, start)]
        while pq:
            curDist, curNode = heapq.heappop(pq)
            if curDist > distances[curNode]:
                continue
            if curNode == end:
                break
            for neighbor in range(1, self.verticle + 1):
                weight = self.graph[curNode][neighbor]
                if weight != np.inf:
                    distThroughCur = curDist + weight
                    if distThroughCur < distances[neighbor]:
                        distances[neighbor] = distThroughCur
                        preNodes[neighbor] = curNode
                        heapq.heappush(pq, (distThroughCur, neighbor))
        path = []
        curr = end
        if preNodes[curr] is None and curr != start:
            return np.inf, []

        while curr is not None:
            path.append(curr)
            curr = preNodes[curr]

        path.reverse()

        return distances[end], path


# Graph with adj list, using dict, key is start node, value is a 2 elements group (target node, distance)
class StdGraph:
    def __init__(self):
        self.graph = defaultdict(list)
        self.allNodes = set()

    def getSize(self):
        return len(self.allNodes)

    def createEdge(self, start, end, distance=1):
        self.graph[start].append((end, distance))
        self.allNodes.add(start)
        self.allNodes.add(end)

    def findPathDFS(self, start, end):
        res = []
        path = []
        visited = set()

        def dfs(cur, curDist):
            if cur == end:
                res.append((list(path), curDist))
                return
            for neighbor, weight in self.graph[cur]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    path.append(neighbor)
                    dfs(neighbor, curDist + weight)
                    path.pop()
                    visited.remove(neighbor)

        path.append(start)
        visited.add(start)
        if start in self.graph or start == end:
            dfs(start, 0)
        return res

    def dijkstra(self, start, end):
        distances = {start: 0}
        preNodes = {start: None}
        pq = [(0, start)]
        while pq:
            curDistance, curNode = heapq.heappop(pq)
            if curDistance > distances[curNode]:
                continue
            if curNode == end:
                break
            for neighbor, weight in self.graph[curNode]:
                newDistance = weight + distances[curNode]
                if newDistance < distances.get(neighbor, float("inf")):
                    distances[neighbor] = newDistance
                    preNodes[neighbor] = curNode
                    heapq.heappush(pq, (newDistance, neighbor))
        path = []
        cur = end
        if cur != start and cur not in preNodes:
            return float("inf"), []
        while cur is not None:
            path.append(cur)
            cur = preNodes[cur]
        path.reverse()
        return distances.get(end, float("inf")), path

    def dijkstraAllPaths(self, start, end):
        distances = {start: 0}
        preNodes = defaultdict(list)
        pq = [(0, start)]

        while pq:
            curDistance, curNode = heapq.heappop(pq)

            if curDistance > distances.get(curNode, float("inf")):
                continue

            for neighbor, weight in self.graph[curNode]:
                newDistance = weight + curDistance
                current_known_dist = distances.get(neighbor, float("inf"))

                # shorter routine found
                if newDistance < current_known_dist:
                    distances[neighbor] = newDistance
                    preNodes[neighbor] = [curNode]
                    heapq.heappush(pq, (newDistance, neighbor))

                # another same shorter distance routine found
                elif newDistance == current_known_dist:
                    preNodes[neighbor].append(curNode)

        allShortestPaths = []
        if end not in distances:
            return float("inf"), []

        def backtrack(current_node, current_path):
            if current_node == start:
                allShortestPaths.append(list(reversed(current_path)))
                return

            for parent in preNodes[current_node]:
                current_path.append(parent)
                backtrack(parent, current_path)
                current_path.pop()

        backtrack(end, [end])

        return distances[end], allShortestPaths


class GridMap:
    def __init__(self, width, height):
        self.grid = np.ones((height, width))
        self.width = width
        self.height = height
        self.path = []
        self.res = []
        self.start = (0, 0)
        self.end = (0, 0)

    def getWeight(self, x, y):
        return self.grid[y][x]

    def setRandomMaze(self):
        for y, row in enumerate(self.grid):
            for x, val in enumerate(row):
                self.grid[y][x] = random.randint(1, 10)

    def setObstacles(self, obstacleCoords):
        for x, y in obstacleCoords:
            self.grid[y][x] = np.inf

    def setStartEnd(self, startXY, endXY):
        self.start = startXY
        self.end = endXY

    def surroundWithObstacles(self, x, y):
        if self.isValid(x, y - 1):
            self.grid[y - 1][x] = np.inf
        if self.isValid(x, y + 1):
            self.grid[y + 1][x] = np.inf
        if self.isValid(x + 1, y):
            self.grid[y][x + 1] = np.inf
        if self.isValid(x - 1, y):
            self.grid[y][x - 1] = np.inf

    def sealCol(self, x):
        for i in range(self.width):
            self.grid[i][x] = np.inf

    def sealRow(self, y):
        for i in range(self.height):
            self.grid[y][i] = np.inf

    def isValid(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        if self.grid[y][x] == np.inf:
            return False
        return True

    def displayMap(self):
        pathSet = set(self.path)
        height = len(self.grid)
        width = len(self.grid[0])
        cellWidth = 4
        print("   |", end="")
        for col in range(width):
            print(f"{col:>{cellWidth}}", end="")
        print()
        print("-" * (4 + width * cellWidth))
        for y, row in enumerate(self.grid):  # enumerate default start index is 0
            print(f"{y:>2} |", end="")
            for x, val in enumerate(row):  # double enumerate to locate current xy
                curPos = (x, y)
                if val == np.inf:
                    print(f"{'█':>{cellWidth}}", end="")
                else:
                    if curPos == self.start or curPos == self.end:
                        print(Fore.GREEN + f"{int(val):>{cellWidth}}", end="")
                    elif curPos in pathSet:
                        print(Fore.BLUE + f"{int(val):>{cellWidth}}", end="")
                    else:
                        print(f"{int(val):>{cellWidth}}", end="")
            print()

    def displayMapInPlace(
        self, moveCursorUp=True, visited=None, cursorPos=None
    ):  # True--cursor lift up to top when done, False--remain pos of cursor when done
        if visited is None:
            visited = set()
        pathSet = set(self.path)
        height = len(self.grid)
        width = len(self.grid[0])
        cellWidth = 4
        totalLinesPrinted = height + 2
        print("   |", end="")
        for col in range(width):
            print(f"{col:>{cellWidth}}", end="")
        print("\033[K")

        print("-" * (4 + width * cellWidth) + "\033[k")
        for y, row in enumerate(self.grid):
            print(f"{y:>2} |", end="")
            for x, val in enumerate(row):
                curPos = (x, y)
                if curPos == cursorPos:
                    print(
                        f"\033[47;30m{int(val) if val != np.inf else '█':>{cellWidth}}\033[0m",
                        end="",
                    )
                elif val == np.inf or val == float("inf"):
                    print(f"{'█':>{cellWidth}}", end="")
                else:
                    if curPos == self.start:
                        print(f"\033[42;30m{int(val):>{cellWidth}}\033[0m", end="")
                    elif curPos == self.end:
                        print(f"\033[41;30m{int(val):>{cellWidth}}\033[0m", end="")
                    elif curPos in pathSet:
                        print(f"\033[93m{int(val):>{cellWidth}}\033[0m", end="")
                    elif curPos in visited:
                        print(f"\033[34m{int(val):>{cellWidth}}\033[0m", end="")
                    else:
                        print(f"{int(val):>{cellWidth}}", end="")
            print("\033[k")
        if moveCursorUp:
            sys.stdout.write(f"\033[{totalLinesPrinted}A\r")
            sys.stdout.flush()

    def selectStartEndByCursor(self):
        print("Select Start and End by moving cursor (Enter to confirm)")
        cx, cy = (0, 0)
        selectedFlag = False
        while True:
            self.displayMapInPlace(moveCursorUp=True, cursorPos=(cx, cy))
            ch = getChar()
            if isinstance(ch, str):
                ch = ch.lower()
            if ch == "up" and cy > 0:
                cy -= 1
            elif ch == "down" and cy < self.height - 1:
                cy += 1
            elif ch == "right" and cx < self.width - 1:
                cx += 1
            elif ch == "left" and cx > 0:
                cx -= 1
            elif ch in ("\r", "\n"):
                if selectedFlag:
                    (ex, ey) = (cx, cy)
                    self.end = (ex, ey)
                    break
                selectedFlag = True
                (sx, sy) = (cx, cy)
                self.start = (sx, sy)
                print(
                    "\033[1;36mStart point selected, use arrow keys to select end point (Enter to confirm))\033[0m\033[K"
                )

        self.displayMapInPlace(moveCursorUp=False)

    def bfs(self):
        self.path = []
        self.res = []
        startx, starty = self.start
        endx, endy = self.end
        queue = deque([(startx, starty)])
        visited = set()
        visited.add((startx, starty))
        preNode = {(startx, starty): None}
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        while queue:
            curx, cury = queue.popleft()
            if curx == endx and cury == endy:
                break
            for dx, dy in directions:
                nextx = curx + dx
                nexty = cury + dy
                nextPos = (nextx, nexty)
                if self.isValid(nextx, nexty) and nextPos not in visited:
                    visited.add(nextPos)
                    preNode[nextPos] = (curx, cury)
                    queue.append(nextPos)
        if self.end not in preNode:
            return []
        self.path = []
        cur = self.end
        while cur is not None:
            self.path.append(cur)
            cur = preNode[cur]
        self.path.reverse()

    def bfsAnime(self):
        self.path = []
        self.res = []
        sx, sy = self.start
        ex, ey = self.end
        queue = deque([(sx, sy)])
        visited = set()
        visited.add((sx, sy))
        preNode = {(sx, sy): None}
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        while queue:
            curx, cury = queue.popleft()
            curPos = (curx, cury)
            self.displayMapInPlace(moveCursorUp=True, visited=visited)
            time.sleep(0.01)
            if curPos == self.end:
                break
            for dx, dy in directions:
                nx = dx + curx
                ny = dy + cury
                nextPos = (nx, ny)
                if self.isValid(nx, ny) and nextPos not in visited:
                    visited.add(nextPos)
                    preNode[nextPos] = curPos
                    queue.append(nextPos)
        if self.end not in preNode:
            return []
        self.path = []
        cur = self.end
        while cur is not None:
            self.path.append(cur)
            cur = preNode[cur]
        self.path.reverse()
        self.displayMapInPlace(moveCursorUp=False, visited=visited)

    def astar(self):
        self.path = []
        self.res = []
        startx, starty = self.start
        endx, endy = self.end

        def getMHTdist(x, y):
            return abs(x - endx) + abs(y - endy)

        pq = [(getMHTdist(startx, starty), self.start)]

        actualStepsScore = {self.start: 0}

        preNode = {self.start: None}
        visited = set()
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        while pq:
            curF, curPos = heapq.heappop(pq)
            curx, cury = curPos

            if curPos == self.end:
                break
            if curPos in visited:
                continue
            visited.add(curPos)

            for dx, dy in directions:
                nextStepPair = (dx + curx, dy + cury)
                nextx, nexty = nextStepPair
                nextPos = (nextx, nexty)
                # add step distance here, now default set as 1
                if self.isValid(nextx, nexty) and nextPos not in visited:
                    tentPrice = actualStepsScore[curPos] + self.getWeight(
                        nextx, nexty
                    )  # default price=1
                    if tentPrice < actualStepsScore.get(nextPos, np.inf):
                        preNode[nextPos] = curPos
                        actualStepsScore[nextPos] = tentPrice
                        finalScore = tentPrice + getMHTdist(nextx, nexty)
                        heapq.heappush(pq, (finalScore, nextPos))
        if self.end not in preNode:
            return []
        self.path = []
        cur = self.end
        while cur is not None:
            self.path.append(cur)
            cur = preNode[cur]
        self.path.reverse()

    def astarAnime(self):
        self.path = []
        self.res = []
        startx, starty = self.start
        endx, endy = self.end

        def getMHTdist(x, y):
            return abs(x - endx) + abs(y - endy)

        pq = [(getMHTdist(startx, starty), self.start)]

        actualStepsScore = {self.start: 0}

        preNode = {self.start: None}
        visited = set()
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        while pq:
            curF, curPos = heapq.heappop(pq)
            curx, cury = curPos

            if curPos == self.end:
                break
            if curPos in visited:
                continue
            visited.add(curPos)
            self.displayMapInPlace(moveCursorUp=True, visited=visited)
            time.sleep(0.01)

            for dx, dy in directions:
                nextStepPair = (dx + curx, dy + cury)
                nextx, nexty = nextStepPair
                nextPos = (nextx, nexty)
                # add step distance here, now default set as 1
                if self.isValid(nextx, nexty) and nextPos not in visited:
                    tentPrice = actualStepsScore[curPos] + self.getWeight(
                        nextx, nexty
                    )  # default price=1
                    if tentPrice < actualStepsScore.get(nextPos, np.inf):
                        preNode[nextPos] = curPos
                        actualStepsScore[nextPos] = tentPrice
                        finalScore = tentPrice + getMHTdist(nextx, nexty)
                        heapq.heappush(pq, (finalScore, nextPos))
        if self.end not in preNode:
            return []
        self.path = []
        cur = self.end
        while cur is not None:
            self.path.append(cur)
            cur = preNode[cur]
        self.path.reverse()
        self.displayMapInPlace(moveCursorUp=False, visited=visited)

    def astarWithWeight(self):
        self.path = []
        self.res = []
        sx, sy = self.start
        ex, ey = self.end

        def getMHTdist(x, y):
            return abs(x - ex) + abs(y - ey)

        pq = [(getMHTdist(sx, sy), self.start)]
        actualStepsScore = {self.start: self.getWeight(sx, sy)}
        preNode = {self.start: None}
        visited = set()
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        while pq:
            curF, curPos = heapq.heappop(pq)
            curx, cury = curPos
            if curPos == self.end:
                break
            if curPos in visited:
                continue
            visited.add(curPos)

            for dx, dy in directions:
                nextStepPair = (curx + dx, cury + dy)
                nx, ny = nextStepPair
                nextPos = (nx, ny)

                if self.isValid(nx, ny) and nextPos not in visited:
                    tentPrice = actualStepsScore[curPos] + self.getWeight(nx, ny)
                    if tentPrice < actualStepsScore.get(nextPos, np.inf):
                        preNode[nextPos] = curPos
                        actualStepsScore[nextPos] = tentPrice
                        finalScore = tentPrice + getMHTdist(nx, ny)
                        heapq.heappush(pq, (finalScore, nextPos))
        if self.end not in preNode:
            return []
        self.path = []
        cur = self.end
        while cur is not None:
            self.path.append(cur)
            cur = preNode[cur]
        self.path.reverse()

    def astarWithWeightAnime(self):
        self.path = []
        self.res = []
        sx, sy = self.start
        ex, ey = self.end

        def getMHTdist(x, y):
            return abs(x - ex) + abs(y - ey)

        pq = [(getMHTdist(sx, sy), self.start)]
        actualStepsScore = {self.start: self.getWeight(sx, sy)}
        preNode = {self.start: None}
        visited = set()
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        while pq:
            curF, curPos = heapq.heappop(pq)
            curx, cury = curPos
            if curPos == self.end:
                break
            if curPos in visited:
                continue
            visited.add(curPos)

            self.displayMapInPlace(moveCursorUp=True, visited=visited)
            time.sleep(0.01)

            for dx, dy in directions:
                nextStepPair = (curx + dx, cury + dy)
                nx, ny = nextStepPair
                nextPos = (nx, ny)

                if self.isValid(nx, ny) and nextPos not in visited:
                    tentPrice = actualStepsScore[curPos] + self.getWeight(nx, ny)
                    if tentPrice < actualStepsScore.get(nextPos, np.inf):
                        preNode[nextPos] = curPos
                        actualStepsScore[nextPos] = tentPrice
                        finalScore = tentPrice + getMHTdist(nx, ny)
                        heapq.heappush(pq, (finalScore, nextPos))
        if self.end not in preNode:
            return []
        self.path = []
        cur = self.end
        while cur is not None:
            self.path.append(cur)
            cur = preNode[cur]
        self.path.reverse()
        self.displayMapInPlace(moveCursorUp=False, visited=visited)

    def dijkstra(self):
        self.path = []
        self.res = []
        sx, sy = self.start
        ex, ey = self.end
        distances = {self.start: 0}
        preNodes = {self.start: None}
        visited = set()
        pq = [(0, self.start)]
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        while pq:
            curDist, curPos = heapq.heappop(pq)
            cx, cy = curPos
            if curDist > distances[curPos]:
                continue
            if curPos in visited:
                continue
            if curPos == self.end:
                break

            visited.add(curPos)
            self.displayMapInPlace(moveCursorUp=True, visited=visited)
            time.sleep(0.01)

            for dx, dy in directions:
                nx = cx + dx
                ny = cy + dy
                nextPos = (nx, ny)
                if self.isValid(nx, ny) and nextPos not in visited:
                    newDist = curDist + self.getWeight(nx, ny)
                    if newDist < distances.get(nextPos, np.inf):
                        distances[nextPos] = newDist
                        preNodes[nextPos] = curPos
                        heapq.heappush(pq, (newDist, nextPos))
        self.path = []
        if self.end not in preNodes:
            return []
        cur = self.end
        while cur is not None:
            self.path.append(cur)
            cur = preNodes[cur]
        self.path.reverse()
        self.displayMapInPlace(moveCursorUp=False, visited=visited)


def executionTime(func, *args, **kwargs):
    s = time.perf_counter()
    res = func(*args, **kwargs)
    e = time.perf_counter()
    duration = (e - s) * 1000
    print(f"Execution time: {duration:.2f} ms")
    return res


def setUpWalls(width, height, start, end):
    walls = []
    sx, sy = start
    ex, ey = end
    cntWalls = random.randint(1, int(width * height / 3))
    for _ in range(cntWalls):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        while (x, y) == (sx, sy) or (x, y) == (ex, ey):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
        walls.append((x, y))
    return walls


def resizeTerminal(col, lines):
    if os.name == "nt":
        os.system(f"mode con cols={col} lines={lines}")
    else:
        sys.stdout.write(f"\033[8;{lines};{col}t")
        sys.stdout.flush()


def greetOS():
    if os.name == "nt":
        print(Fore.BLACK + Back.GREEN + "Hello from Windows")
    else:
        if platform.system().startswith("Dar"):
            print(Fore.BLACK + Back.GREEN + Style.BRIGHT + "Hello from MacOS")
        else:
            print(Fore.BLACK + Back.GREEN + Style.BRIGHT + "Hello from Linux")


def itrMenu(title, options):  # options: [(return var/shortcut, display text), ...]
    curIndex = 0
    menuLength = len(options)
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()
    try:
        print(f"\033[1;36m=== {title} ===\033[0m")
        print("[\033[33m↑ / ↓\033[0m] Up&Down  [\033[32mEnter\033[0m] Confirm\n")
        firstDraw = True
        while True:
            if not firstDraw:
                sys.stdout.write(f"\r\033[{menuLength - 1}A")
            firstDraw = False

            for i, (shortcut, text) in enumerate(options):
                if i == curIndex:
                    line = f"\033[42;30m  > [{shortcut}] {text} \033[0m\033[K"
                else:
                    line = f"    [{shortcut}] {text} \033[K"
                if i == menuLength - 1:
                    sys.stdout.write(line)
                else:
                    sys.stdout.write(line + "\n")

            sys.stdout.flush()
            ch = getChar()
            if isinstance(ch, str):
                ch = ch.lower()
            if ch == "up":
                curIndex = (curIndex - 1) % menuLength
            elif ch == "down":
                curIndex = (curIndex + 1) % menuLength
            elif ch in ("\r", "\n"):
                return options[curIndex][0]
            else:
                for idx, (shortcut, _) in enumerate(options):
                    if ch == shortcut:
                        return shortcut
    finally:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()


def main():
    menuOptions = [
        ("s", "SeqList"),
        ("l", "LinkList"),
        ("t", "BiTree"),
        ("g", "Graph"),
        ("d", "StdGraph"),
        ("m", "GridMap"),
    ]
    op = itrMenu("Python DS", menuOptions)
    os.system("cls" if os.name == "nt" else "clear")

    if op.lower() == "s":
        initLength = input("Enter init data, which is the MAXSIZE of SeqList:")
        myList = SeqList(int(initLength))
        for i in range(int(initLength)):
            myList.append(i)
        myList.display()
        rawInput = input("Enter insert index and value:")
        iInsertIndex, nValue = rawInput.split()
        myList.insert(int(iInsertIndex), int(nValue))
        myList.display()
        input("Enter to end")
    elif op.lower() == "l":
        llA = LinkList()
        for i in range(100):
            llA.pushBack(random.randint(0, 1000))
        llA.mergeSortA()
        llA.display()
        llA.mergeSortD()
        llA.display()
        input("Enter to end")
    elif op.lower() == "t":
        myTree = BiTree()
        vals = []
        op = input("p for pre-order construction, l for level-order construction:")
        if op.lower() == "p":
            print(
                "Input vals for bitree in pre-order(None node must be included):",
                end="",
            )
            rawInput = input()
            rawInput = list(rawInput)
            while rawInput:
                vals.append(rawInput.pop(0))
            myTree.createBiTree(vals)
            myTree.preOrderTraverse(myTree.root)
            print()
            myTree.levelTraverse(myTree.root)
            # myTree.locateAndPrintPath(myTree.root, "E")
            executionTime(myTree.locateAndPrintPath, myTree.root, "E")
            print(f"{myTree.countLeafNode(myTree.root)}")
        elif op.lower() == "l":
            print(
                "Input vals for bitree in level-order(None node must be included):",
                end="",
            )
            rawInput = input()
            rawInput = list(rawInput)
            while rawInput:
                vals.append(rawInput.pop(0))
            myTree.createBiTreeLevelOrder(vals)
            myTree.preOrderTraverse(myTree.root)
            print()
            myTree.levelTraverse(myTree.root)
            # myTree.locateAndPrintPath(myTree.root, "E")
            executionTime(myTree.locateAndPrintPath, myTree.root, "E")
            print(f"{myTree.countLeafNode(myTree.root)}")
        input("Enter to end")
    elif op.lower() == "g":
        g = Graph(5)
        edges = [(1, 2), (1, 3), (4, 5), (5, 2), (4, 1), (3, 2), (3, 4)]
        for u, v in edges:
            g.createEdge(u, v)
        paths = g.findPathDFS(4, 2)
        print("Found paths from 4 to 2:")
        for p in paths:
            print(p)

        g = Graph(6)

        edges = [
            (1, 2, 2),
            (1, 3, 4),
            (2, 3, 1),
            (2, 4, 7),
            (3, 5, 3),
            (4, 6, 1),
            (5, 4, 2),
            (5, 6, 5),
        ]
        for u, v, d in edges:
            g.createEdge(u, v, d)

        start_node = 1
        end_node = 6
        shortest_dist, best_path = g.dijkstra(start_node, end_node)

        print(f"从节点 {start_node} 到节点 {end_node} 的最短距离是: {shortest_dist}")
        print(f"最佳路线为: {best_path}")
    elif op.lower() == "d":
        g = StdGraph()
        edges = [
            ("Tokyo", "Nagoya", 350),
            ("Tokyo", "Kyoto", 450),
            ("Nagoya", "Kyoto", 130),
            ("Kyoto", "Osaka", 50),
            ("Nagoya", "Osaka", 180),
            ("Tokyo", "Osaka", 500),
            ("Osaka", "Fukuoka", 500),
        ]
        for start, end, distance in edges:
            g.createEdge(start, end, distance)
        paths = g.findPathDFS("Tokyo", "Osaka")
        print(list(paths))
        for idx, (p, dist) in enumerate(paths, 1):
            print(f"Routine {idx}: {'->'.join(p)}, lenth is {dist}")
        minDist, bestPath = g.dijkstra("Tokyo", "Osaka")
        print(f"Shortest path's len is {minDist}")
        print(f"Best routine: {bestPath}")
        minDist, bestPaths = g.dijkstraAllPaths("Tokyo", "Osaka")
        print(f"Shortest path's len is {minDist}")
        for path in bestPaths:
            print(f"Best routine: {path}")
    elif op.lower() == "m":
        (width, height) = input(
            "Enter GridMap's width and height(example: 20 10): "
        ).split(" ")
        initCol = int(width) * 4 + 10
        initLines = int(height) + 12
        resizeTerminal(initCol, initLines)

        g = GridMap(int(width), int(height))
        gw = GridMap(int(width), int(height))
        gw.setRandomMaze()

        g.selectStartEndByCursor()

        walls = setUpWalls(g.width, g.height, g.start, g.end)
        g.setObstacles(walls)

        print("Now running Dijkstra...")
        g.dijkstra()
        print("Shortest routine: " + Fore.GREEN + f"{g.path}")
        if not g.path:
            print(f"End {g.end} " + Fore.RED + "unreachable")
        else:
            print("Steps: " + Fore.GREEN + f"{len(g.path) - 1}")

        time.sleep(2)

        print("Now running bfs...")
        # g.bfs()
        # g.displayMap()
        g.bfsAnime()
        print("Shortest routine: " + Fore.BLUE + f"{g.path}")
        if not g.path:
            print(f"End {g.end} " + Fore.RED + "unreachable")
        else:
            print("Steps: " + Fore.BLUE + f"{len(g.path) - 1}")

        time.sleep(2)

        print("Now running A*...")
        # g.astar()
        # g.displayMap()
        g.astarAnime()
        print("Shortest routine: " + Fore.GREEN + f"{g.path}")
        if not g.path:
            print(f"End {g.end} " + Fore.RED + "unreachable")
        else:
            print("Steps: " + Fore.GREEN + f"{len(g.path) - 1}")

        time.sleep(2)

        print("Now processing random maze gw:")
        # gw.setStartEnd(
        #     (random.randint(1, 20), random.randint(1, 20)),
        #     (random.randint(1, 20), random.randint(1, 20)),
        # )
        gw.selectStartEndByCursor()
        gw.setObstacles(walls)
        # gw.astarWithWeight()
        # gw.displayMap()
        gw.astarWithWeightAnime()

    else:
        raise SyntaxError("Not a valid op")


if __name__ == "__main__":
    greetOS()
    main()
