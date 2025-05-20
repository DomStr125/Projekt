import math
import random
import time
import tkinter as tk
from tkinter import messagebox
from collections import deque


class LabirynthGame:
    def __init__(self, root, width=100, height=100): #initializacja gry
        self.root = root
        self.root.title("Labirynth Game")

        self.width = width
        self.height = height
        self.cell_size = 32
        self.min_distance = (width + height) // 2

        self.points = 0
        self.start_time = time.time()
        self.game_time = 0
        self.is_game_active = True

        self.frame_points = tk.Frame(root, bg='#f0f0f0')
        self.frame_points.pack(side=tk.TOP, fill=tk.X)

        self.label_points = tk.Label(self.frame_points, text="Points: 0", font=('Arial', 10, 'bold'), fg="white", bg="#34495e")   
        self.label_points.pack(side=tk.LEFT, padx=10)

        self.label_time = tk.Label(self.frame_points, text="Time: 0s", font=('Arial', 10, 'bold'), fg="white", bg="#34495e")
        self.label_time.pack(side=tk.LEFT)

        self.setup_scores()

        self.textures = self.load_textures()
        self.colors = {
            "wall": "black",
            "path": "white",
            "player": "blue",
            "exit": "green",
            "key": "gold",
            "door": "red"
        }

        self.keys = []
        self.key_x, self.key_y = -1, -1
        self.door_x, self.door_y = -1, -1
        self.door_active = True

        self.labirynth = self.generate_labirynth()
        self.player_x, self.player_y = 1, 1
        self.previous_x, self.previous_y = self.player_x, self.player_y
        self.exit_x, self.exit_y = self.random_exit()
        self.labirynth[self.exit_y][self.exit_x] = "E"
        self.create_key_door()
        self.labirynth[self.key_y][self.key_x] = "K"

        self.canvas = tk.Canvas(root, width=self.width * self.cell_size, height=self.height * self.cell_size, bg="white")
        self.canvas.pack()      
        self.root.bind("<KeyPress>", self.on_key_press)
        self.draw_labirynth()

    def load_textures(self): # ładowanie tekstur
        textures = {
            "wall": tk.PhotoImage(file="grafika/wall.png"),
            "path": tk.PhotoImage(file="grafika/path.png"),
            "player": tk.PhotoImage(file="grafika/knight.png"),
            "exit": tk.PhotoImage(file="grafika/exit.png"),
            "key": tk.PhotoImage(file="grafika/silver_key.png"),
            "door": tk.PhotoImage(file="grafika/silver_door.png")
        }
        return textures

    def setup_scores(self): # aktualizacja punktów i czasu         
            if self.is_game_active:
                self.game_time = int(time.time() - self.start_time)
                self.points = max(0, 10000 - self.game_time * 10)

                self.label_points.config(text=f"Punkty: {self.points}")
                self.label_time.config(text=f"Czas: {self.game_time}s")

                self.root.after(1000, self.setup_scores)
    
    def generate_labirynth(self): # generowanie labiryntu możliwego do przejścia
        labirynth = [[1 for i in range(self.width)] for j in range(self.height)]

        x, y = random.randint(1, self.width), random.randint(1, self.height)
        stock = [(1, 1)]
        labirynth[1][1] = 0
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        while stock:
            x, y = stock[-1]
            neighbors = []
            for dx, dy in directions:
                nx, ny = x + dx * 2, y + dy * 2
                if 0 < nx < self.width - 1 and 0 < ny < self.height - 1 and labirynth[ny][nx] == 1:
                    neighbors.append((dx, dy))
                
            if neighbors:
                dx, dy = random.choice(neighbors)
                labirynth[y + dy][x + dx] = 0
                labirynth[y + dy * 2][x + dx * 2] = 0
                stock.append((x + dx * 2, y + dy * 2))  
            else:
                stock.pop()

        for i in range(self.width):
            labirynth[0][i] = 1
            labirynth[self.height - 1][i] = 1
        for j in range(self.height):
            labirynth[j][0] = 1
            labirynth[j][self.width - 1] = 1

        return labirynth
    
    def find_furthest_point(self, start_x, start_y): # znajdowanie najdalszego punktu w labiryncie
        visited = [[False for i in range(self.width)] for j in range(self.height)]
        queue = deque()
        queue.append((start_x, start_y, 0))
        visited[start_y][start_x] = True
        max_distance = (start_x, start_y, 0)

        while queue:
            x, y, dist = queue.popleft()
            if dist > max_distance[2]:
                max_distance = (x, y, dist)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and not visited[ny][nx] and self.labirynth[ny][nx] != 1:
                    visited[ny][nx] = True
                    queue.append((nx, ny, dist + 1))
        
        return max_distance[0], max_distance[1]

    def random_exit(self): # losowanie pozycji wyjścia
        exit_x, exit_y = self.find_furthest_point(self.player_x, self.player_y)
        while exit_x == self.player_x and exit_y == self.player_y:
            exit_x, exit_y = random.choice([(x,y) for y in range(self.height) for x in range(self.width) if self.labirynth[y][x] == 0])
        return exit_x, exit_y

    def draw_labirynth(self): # wyświetlanie labiryntu z położeniem gracza i wyjściem
        self.canvas.delete("all")

        for y in range(self.height):
            for x in range(self.width):
                if self.labirynth[y][x] == 1:
                    self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor=tk.NW, image=self.textures["wall"])
                else:
                    self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor=tk.NW, image=self.textures["path"])
        
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) == (self.exit_x, self.exit_y):
                    self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor=tk.NW, image=self.textures["exit"])
                elif (x, y) == (self.player_x, self.player_y):
                    self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor=tk.NW, image=self.textures["player"])
                elif (x, y) == (self.key_x, self.key_y) and self.labirynth[y][x] == "K":
                    self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor=tk.NW, image=self.textures["key"])
                elif (x, y) == (self.door_x, self.door_y) and self.door_active:
                    self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor=tk.NW, image=self.textures["door"])

    def on_key_press(self, event): # obsługa klawiszy
        new_x, new_y = self.player_x, self.player_y
        previous_x, previous_y = self.player_x, self.player_y

        if event.keysym == "w":
            new_y -= 1
        elif event.keysym == "s":
            new_y += 1
        elif event.keysym == "a":
            new_x -= 1
        elif event.keysym == "d":
            new_x += 1

        if 0 <= new_x < self.width and 0 <= new_y < self.height: #blokada ścian
            if self.labirynth[new_y][new_x] != 1:
                self.player_x, self.player_y = new_x, new_y
                self.draw_labirynth()


        if (self.player_x, self.player_y) == (self.key_x, self.key_y): #zbieranie klucza
            self.keys.append("K")
            self.labirynth[self.key_y][self.key_x] = 0
            self.key_x, self.key_y = -1, -1 
            print("You found a key!")
        
        if (self.player_x, self.player_y) == (self.door_x, self.door_y) and self.door_active: #otwieranie drzwi
            if "K" in self.keys:
                self.door_active = False
                self.labirynth[self.door_y][self.door_x] = 0
                self.keys.remove("K")
                self.points += 150
                print("You opened the door!")
            else:
                print("You need a key to open this door!")
                self.player_x, self.player_y = previous_x, previous_y

        if (self.player_x, self.player_y) == (self.exit_x, self.exit_y): # wyjście z labiryntu
            self.is_game_active = False
            final_time = int(time.time() - self.start_time)
            messagebox.showinfo("Congratulations!", f"You've reached the exit in {final_time}s \n Your score: {self.points}")
            self.root.quit()
                   
    def create_key_door(self): # tworzenie klucza i drzwi
        reachable_paths = self.find_reachable_paths(self.player_x, self.player_y)

        self.key_x, self.key_y = random.choice([(x, y) for x, y in reachable_paths if (x, y) != (self.player_x, self.player_y) and (x, y) != (self.exit_x, self.exit_y)])
        self.labirynth[self.key_y][self.key_x] = "K"

        exit_path = self.find_path(self.key_x, self.key_y, self.exit_x, self.exit_y)
        if len(exit_path) > 20:
            self.door_x, self.door_y = exit_path[20]
            self.labirynth[self.door_y][self.door_x] = "D"
        else:
            self.door_x, self.door_y = random.choice([(x, y) for (x, y) in reachable_paths if (x, y) != (self.player_x, self.player_y) and (x, y) != (self.exit_x, self.exit_y)])
            self.labirynth[self.door_y][self.door_x] = "D"
    
    def find_reachable_paths(self, start_x, start_y): # znajdowanie dostępnych ścieżek
        visited = set()
        queue = deque([(start_x, start_y)])
        reachable = []

        while queue:
            x, y = queue.popleft()
            if (x, y) in visited:
                continue

            visited.add((x, y))
            if self.labirynth[y][x] != 1:
                reachable.append((x, y))
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        queue.append((nx, ny))
        return reachable

    def find_path(self, start_x, start_y, target_x, target_y): # znajdowanie ścieżki w labiryncie
        queue = deque([(start_x, start_y, [])])
        visited = set()

        while queue:
            x, y, path = queue.popleft()
            if (x, y) == (target_x, target_y):
                return path + [(x, y)]
            
            if (x, y) in visited:
                continue

            visited.add((x, y))
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and self.labirynth[ny][nx] != 1:
                    queue.append((nx, ny, path + [(x, y)]))
        
        return []

if __name__ == "__main__":
    root = tk.Tk()
    game = LabirynthGame(root, width=45, height=20)
    root.mainloop()