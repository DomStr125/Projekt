import random
import time
import tkinter as tk
from tkinter import messagebox
from collections import deque
import pickle

class LabirynthGame:

    DIFFICULTY_SETTINGS = {
        "easy": {
            "width": 30,
            "height": 15,
            "doors": 0,
            "max_keys": 1,
            "hearts": 5,
            "enemies": 5,
            "vision_range": 2
        },
        "medium": {
            "width": 40,
            "height": 20,
            "doors": 3,
            "max_keys": 2,
            "hearts": 5,
            "enemies": 10,
            "vision_range": 2
        },
        "hard": {
            "width": 50,
            "height": 25,
            "doors": 5,
            "max_keys": 3,
            "hearts": 3,
            "enemies": 20,
            "vision_range": 2
        }
    }

    def __init__(self, root, difficulty="easy"): #initializacja gry
        self.root = root
        self.root.title(f"Labirynth Game - {difficulty.capitalize()}")
        self.root.state("zoomed")

        self.width = self.DIFFICULTY_SETTINGS[difficulty]["width"]
        self.height = self.DIFFICULTY_SETTINGS[difficulty]["height"]
        self.cell_size = 32
        self.min_distance = (self.width + self.height) // 2
        self.vision_range = self.DIFFICULTY_SETTINGS[difficulty]["vision_range"]
        self.max_keys = self.DIFFICULTY_SETTINGS[difficulty]["max_keys"]
        self.hearts = self.DIFFICULTY_SETTINGS[difficulty]["hearts"]
        self.enemies_number = self.DIFFICULTY_SETTINGS[difficulty]["enemies"]
        self.difficulty = difficulty

        self.inventory = {
            "keys": [],
            "special_items": [],
            "Gate Key": 0
        }

        self.points = 5000
        self.start_time = time.time()
        self.game_time = 0
        self.is_game_active = True

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        max_cell_width = screen_width // self.width
        max_cell_height = (screen_height - 50) // self.height
        self.cell_size = min(self.cell_size, max_cell_width, max_cell_height)


        self.frame_points = tk.Frame(root, bg='#f0f0f0')
        self.frame_points.pack(side=tk.TOP, fill=tk.X)

        self.label_points = tk.Label(self.frame_points, text="Points: 0", font=('Arial', 10, 'bold'), fg="white", bg="#34495e")   
        self.label_points.pack(side=tk.LEFT, padx=10)

        self.label_time = tk.Label(self.frame_points, text="Time: 0s", font=('Arial', 10, 'bold'), fg="white", bg="#34495e")
        self.label_time.pack(side=tk.LEFT)

        self.label_hearts = tk.Label(self.frame_points, text=f"Hearts: {self.hearts}", font=('Arial', 10, 'bold'), fg="white", bg="#34495e")
        self.label_hearts.pack(side=tk.LEFT, padx=10)

        self.setup_scores()

        self.textures = self.load_textures()

        self.keys = []
        self.key_x, self.key_y = -1, -1
        self.door_x, self.door_y = -1, -1
        self.door_active = True
        self.torch_x, self.torch_y = -1, -1

        self.labirynth = self.generate_labirynth()
        self.player_x, self.player_y = 1, 1
        self.previous_x, self.previous_y = self.player_x, self.player_y
        self.exit_x, self.exit_y = self.random_exit()
        self.labirynth[self.exit_y][self.exit_x] = "E"
        self.place_gate()
        self.place_gate_key()
        self.create_key_door()
        self.labirynth[self.key_y][self.key_x] = "K"
        self.labirynth[self.door_y][self.door_x] = "D"
        self.labirynth[self.torch_x][self.torch_y] = "T"

        self.doors = []
        self.keys_pos = []
        self.keys = []
        self.create_doors_and_keys(self.DIFFICULTY_SETTINGS[difficulty]["doors"])

        self.place_torch()

        self.discovered = [[False for _ in range(self.width)] for _ in range(self.height)]

        self.canvas = tk.Canvas(root, width=self.width * self.cell_size, height=self.height * self.cell_size, bg="white")
        self.canvas.pack(expand=True, fill=tk.BOTH)      
        self.root.bind("<KeyPress>", self.on_key_press)
        self.draw_labirynth()

        self.enemies = []
        self.grass_monsters = set()
        self.player_moves = 0
        self.monster_turns_left = 0
        self.monster_hidden_turns = random.randint(2, 5)
        self.monster_visible_turns = random.randint(2, 5)
        self.monsters_are_visible = False
        self.place_enemies()

    def load_textures(self): # ładowanie tekstur
        textures = {
            "wall": tk.PhotoImage(file="grafika/forest/wall.png"),
            "path": tk.PhotoImage(file="grafika/forest/path.png"),
            "player": tk.PhotoImage(file="grafika/knight.png"),
            "exit": tk.PhotoImage(file="grafika/exit.png"),
            "ruby_key": tk.PhotoImage(file="grafika/ruby_key.png"),
            "ruby_door": tk.PhotoImage(file="grafika/ruby_door.png"),
            "fog": tk.PhotoImage(file="grafika/forest/fog.png"),
            "torch": tk.PhotoImage(file="grafika/forest/torch.png"),
            "gate": tk.PhotoImage(file="grafika/forest/gate.png"),
            "gate_key": tk.PhotoImage(file="grafika/forest/gate_key.png"),
            "amber_key": tk.PhotoImage(file="grafika/amber_key.png"),
            "amber_door": tk.PhotoImage(file="grafika/amber_door.png"),
            "amethyst_key": tk.PhotoImage(file="grafika/amethyst_key.png"),
            "amethyst_door": tk.PhotoImage(file="grafika/amethyst_door.png"),
            "emerald_key": tk.PhotoImage(file="grafika/emerald_key.png"),
            "emerald_door": tk.PhotoImage(file="grafika/emerald_door.png"),
            "sapphire_key": tk.PhotoImage(file="grafika/sapphire_key.png"),
            "sapphire_door": tk.PhotoImage(file="grafika/sapphire_door.png"),
            "grass": tk.PhotoImage(file="grafika/forest/grass.png"),
            "grass_monster": tk.PhotoImage(file="grafika/forest/grass_monster.png"),
        }
        return textures

    def setup_scores(self): # aktualizacja punktów i czasu         
            if self.is_game_active:
                self.game_time = int(time.time() - self.start_time)
                self.points = max(0, 5000 - self.game_time * 10)

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
                if ((x - self.player_x) ** 2 + (y - self.player_y) ** 2) <= self.vision_range ** 2:
                    self.discovered[y][x] = True
                    cell = self.labirynth[y][x]
                    if (x, y) == (self.exit_x, self.exit_y):
                        self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor=tk.NW, image=self.textures["exit"])
                    elif (x, y) == (self.player_x, self.player_y):
                        self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor=tk.NW, image=self.textures["player"])
                    elif isinstance(cell, str) and cell.startswith("K"):
                        # Draw key based on its type
                        key_textures = {
                            "K1": "ruby_key",
                            "K2": "amber_key",
                            "K3": "amethyst_key",
                            "K4": "emerald_key",
                            "K5": "sapphire_key"
                        }
                        texture = self.textures.get(key_textures.get(cell, "ruby_key"))
                        self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor=tk.NW, image=texture)
                    elif isinstance(cell, str) and cell.startswith("D"):
                        # Draw door based on its type
                        door_textures = {
                            "D1": "ruby_door",
                            "D2": "amber_door",
                            "D3": "amethyst_door",
                            "D4": "emerald_door",
                            "D5": "sapphire_door"
                        }
                        texture = self.textures.get(door_textures.get(cell, "ruby_door"))
                        self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor=tk.NW, image=texture)
                    elif (x, y) == (self.torch_x, self.torch_y):
                        self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor=tk.NW, image=self.textures["torch"])
                    elif (x, y) == (self.gate_x, self.gate_y) and self.labirynth[y][x] == "G":
                        self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor=tk.NW, image=self.textures["gate"])
                    elif (x, y) == (self.gate_key_x, self.gate_key_y) and self.labirynth[y][x] == "GK":
                        self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor=tk.NW, image=self.textures["gate_key"])
                    elif cell == "GRASS":
                        self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor=tk.NW, image=self.textures["grass"])
                    elif cell == "GRASS_MONSTER":
                        self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor=tk.NW, image=self.textures["grass_monster"])
                else:
                    self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor=tk.NW, image=self.textures["fog"])

    def on_key_press(self, event): # obsługa klawiszy
        # Show inventory on 'e' key
        if event.keysym.lower() == "e":
            keys_display = ", ".join(self.keys) if self.keys else "None"
            specials_display = ", ".join(self.inventory["special_items"]) if self.inventory["special_items"] else "None"
            gate_key_display = "Yes" if self.inventory.get("Gate Key", 0) else "No"
            message = (
                f"Inventory:\n"
                f"Keys: {keys_display}\n"
                f"Special items: {specials_display}\n"
                f"Gate Key: {gate_key_display}"
            )
            messagebox.showinfo("Inventory", message)
            return

        if event.keysym == "space":
            self.show_minimap()
            return

        if event.keysym.lower() == "f5":
            self.save_game()
            return

        if event.keysym.lower() == "f9":
            self.load_game()
            return

        if event.keysym.lower() == "p":
            self.save_game()
            return
        if event.keysym.lower() == "l":
            self.load_game()
            return

        new_x, new_y = self.player_x, self.player_y
        previous_x, previous_y = self.player_x, self.player_y

        if event.keysym in ("w", "Up", "W"):
            new_y -= 1
        elif event.keysym in ("s", "Down", "S"):
            new_y += 1
        elif event.keysym in ("a", "Left", "A"):
            new_x -= 1
        elif event.keysym in ("d", "Right", "D"):
            new_x += 1

        if 0 <= new_x < self.width and 0 <= new_y < self.height: #blokada ścian
            cell = self.labirynth[new_y][new_x]
            # Check for door
            if isinstance(cell, str) and cell.startswith("D"):
                key_type = "K" + cell[1:]  # e.g. D2 -> K2
                if key_type in self.keys:
                    # Open the door
                    self.labirynth[new_y][new_x] = 0
                    self.keys.remove(key_type)
                    self.points += 200
                    self.label_points.config(text=f"Punkty: {self.points}")
                    print(f"You opened door {cell}!")
                    self.player_x, self.player_y = new_x, new_y
                else:
                    print(f"You need key {key_type} to open this door!")
                    # Don't move
            elif cell != 1:
                self.player_x, self.player_y = new_x, new_y

        self.player_moves += 1
        if self.player_moves % 3 == 0:
            self.monster_turns_left = 2
            self.grass_monsters = set(self.enemies)
            for (x, y) in self.enemies:
                self.labirynth[y][x] = "GRASS_MONSTER"
        elif self.monster_turns_left > 0:
            self.monster_turns_left -= 1
            if self.monster_turns_left == 0:
                for (x, y) in self.enemies:
                    self.labirynth[y][x] = "GRASS"
                self.grass_monsters.clear()

        # Monster visibility logic
        if not hasattr(self, "monsters_are_visible"):
            self.monsters_are_visible = False
            self.monster_hidden_turns = random.randint(3, 5)
            self.monster_visible_turns = random.randint(1, 2)

        if self.monsters_are_visible:
            self.monster_visible_turns -= 1
            if self.monster_visible_turns <= 0:
                # Hide monsters
                for (x, y) in self.enemies:
                    self.labirynth[y][x] = "GRASS"
                self.grass_monsters.clear()
                self.monsters_are_visible = False
                self.monster_hidden_turns = random.randint(3, 5)
        else:
            self.monster_hidden_turns -= 1
            if self.monster_hidden_turns <= 0:
                # Show monsters
                self.grass_monsters = set(self.enemies)
                for (x, y) in self.enemies:
                    self.labirynth[y][x] = "GRASS_MONSTER"
                self.monsters_are_visible = True
                self.monster_visible_turns = random.randint(1, 2)

        self.draw_labirynth()

        # Check for key collection
        cell = self.labirynth[self.player_y][self.player_x]
        if isinstance(cell, str) and cell.startswith("K"):
            if cell not in self.keys:
                if len(self.keys) >= self.max_keys and self.max_keys > 0:
                    removed_key = self.keys.pop(0)
                    # Place the removed key at the current position
                    self.labirynth[self.player_y][self.player_x] = removed_key
                    print(f"Inventory full! Dropped oldest key: {removed_key} and picked up {cell}")
                elif self.max_keys == 0:
                    print("You cannot carry any keys on this difficulty!")
                    return
                else:
                    self.labirynth[self.player_y][self.player_x] = 0
                    print(f"You found key {cell}!")
                self.keys.append(cell)
                # Only clear the cell if we didn't just drop a key there
                if self.labirynth[self.player_y][self.player_x] == cell:
                    self.labirynth[self.player_y][self.player_x] = 0

        # Torch collection
        if (self.player_x, self.player_y) == (self.torch_x, self.torch_y):
            self.labirynth[self.torch_y][self.torch_x] = 0
            self.torch_x, self.torch_y = -1, -1
            self.vision_range += 2
            self.points += 100
            self.label_points.config(text=f"Punkty: {self.points}")
            print("You found a torch! Vision increased.")
            self.inventory["special_items"].append("torch")
            self.draw_labirynth()

        # Exit
        if (self.player_x, self.player_y) == (self.exit_x, self.exit_y):
            self.is_game_active = False
            final_time = int(time.time() - self.start_time)
            self.points += self.hearts * 250
            messagebox.showinfo("Congratulations!", f"You've reached the exit in {final_time}s \n Your score: {self.points}")
            self.root.quit()

        # Gate logic (unchanged)
        if (self.player_x, self.player_y) == (self.gate_x, self.gate_y):
            if self.inventory["Gate Key"] == 1:
                self.labirynth[self.gate_y][self.gate_x] = 0
                self.gate_x, self.gate_y = -1, -1
                self.points += 500
                self.label_points.config(text=f"Punkty: {self.points}")
                print("You opened the gate!")
                self.draw_labirynth()
            else:
                print("You need a Gate Key to open this gate!")
                self.player_x, self.player_y = previous_x, previous_y

        if (self.player_x, self.player_y) == (self.gate_key_x, self.gate_key_y):
            self.labirynth[self.gate_key_y][self.gate_key_x] = 0
            self.gate_key_x, self.gate_key_y = -1, -1
            self.inventory["Gate Key"] += 1
            self.points += 300
            self.label_points.config(text=f"Punkty: {self.points}")
            print("You found a Gate Key!")
            self.draw_labirynth()

        if (self.player_x, self.player_y) in self.grass_monsters:
            self.hearts -= 1
            self.label_hearts.config(text=f"Hearts: {self.hearts}")
            print("You were hit by a monster! Lost 1 heart.")
            if self.hearts <= 0:
                self.is_game_active = False
                messagebox.showinfo("Game Over", "You lost all your hearts!")
                self.root.quit()
                   
    def create_key_door(self): # tworzenie klucza i drzwi
        reachable_paths = self.find_reachable_paths(self.player_x, self.player_y)

        # położenie klucza
        self.key_x, self.key_y = random.choice([
            (x, y) for x, y in reachable_paths
            if (x, y) != (self.player_x, self.player_y) and (x, y) != (self.exit_x, self.exit_y)
        ])
        self.labirynth[self.key_y][self.key_x] = "K"

        # ścieżka od gracza do klucza i od klucza do wyjścia
        path_to_key = self.find_path(self.player_x, self.player_y, self.key_x, self.key_y)
        path_key_to_exit = self.find_path(self.key_x, self.key_y, self.exit_x, self.exit_y)

        # Umieść drzwi tylko na ścieżce od klucza do wyjścia, nie blokując ścieżki od gracza do klucza
        if len(path_key_to_exit) > 2:
            # Unikaj umieszczania drzwi na kluczu lub wyjściu
            possible_door_positions = [
                pos for pos in path_key_to_exit[1:-1]
                if pos not in path_to_key
            ]
            if possible_door_positions:
                self.door_x, self.door_y = random.choice(possible_door_positions)
            else:
                # fallback: stwórz drzwi w losowej dostępnej lokalizacji
                self.door_x, self.door_y = random.choice([
                    (x, y) for (x, y) in reachable_paths
                    if (x, y) != (self.player_x, self.player_y)
                    and (x, y) != (self.exit_x, self.exit_y)
                    and (x, y) != (self.key_x, self.key_y)
                    and (x, y) not in path_to_key
                ])
            self.labirynth[self.door_y][self.door_x] = "D"
        else:
            # fallback: stwórz drzwi w losowej dostępnej lokalizacji
            self.door_x, self.door_y = random.choice([
                (x, y) for (x, y) in reachable_paths
                if (x, y) != (self.player_x, self.player_y)
                and (x, y) != (self.exit_x, self.exit_y)
                and (x, y) != (self.key_x, self.key_y)
                and (x, y) not in path_to_key
            ])
            self.labirynth[self.door_y][self.door_x] = "D"

    def create_doors_and_keys(self, num_doors): # tworzenie wielu drzwi i kluczy
        for i in range(num_doors):
            reachable_paths = self.find_reachable_paths(self.player_x, self.player_y)
            # Place key
            key_pos = random.choice([
                (x, y) for x, y in reachable_paths
                if (x, y) != (self.player_x, self.player_y) and (x, y) != (self.exit_x, self.exit_y)
                and (x, y) not in self.keys_pos and (x, y) not in self.doors
            ])
            self.keys_pos.append(key_pos)
            self.labirynth[key_pos[1]][key_pos[0]] = f"K{i+1}"

            # Find path from player to key and key to exit
            path_to_key = self.find_path(self.player_x, self.player_y, key_pos[0], key_pos[1])
            path_key_to_exit = self.find_path(key_pos[0], key_pos[1], self.exit_x, self.exit_y)

            # Place door only on path from key to exit, not blocking player to key
            possible_door_positions = [
                pos for pos in path_key_to_exit[1:-1]
                if pos not in path_to_key and pos not in self.doors and pos not in self.keys_pos
            ]
            if possible_door_positions:
                door_pos = random.choice(possible_door_positions)
            else:
                door_pos = random.choice([
                    (x, y) for (x, y) in reachable_paths
                    if (x, y) != (self.player_x, self.player_y)
                    and (x, y) != (self.exit_x, self.exit_y)
                    and (x, y) not in self.keys_pos
                    and (x, y) not in self.doors
                    and (x, y) not in path_to_key
                ])
            self.doors.append(door_pos)
            self.labirynth[door_pos[1]][door_pos[0]] = f"D{i+1}"
    
    def place_torch(self): # umieszczanie położenia pochodni
        possible = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if self.labirynth[y][x] == 0 and
               (x, y) != (self.player_x, self.player_y) and
               (x, y) != (self.exit_x, self.exit_y) and
               (x, y) != (self.key_x, self.key_y) and
               (x, y) != (self.door_x, self.door_y)
        ]
        if possible:
            self.torch_x, self.torch_y = random.choice(possible)
            self.labirynth[self.torch_y][self.torch_x] = "T"
        else:
            self.torch_x, self.torch_y = -1, -1

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

    def place_gate(self): # umieszczanie bramy
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(directions)
        for dx, dy in directions:
            gx, gy = self.exit_x + dx, self.exit_y + dy
            if 0 <= gx < self.width and 0 <= gy < self.height and self.labirynth[gy][gx] == 0:
                self.labirynth[gy][gx] = "G"
                self.gate_x, self.gate_y = gx, gy
                return
        self.gate_x, self.gate_y = -1, -1

    def place_gate_key(self): # umieszczanie klucza do bramy
        visited = [[False]*self.width for _ in range(self.height)]
        queue = deque([(self.gate_x, self.gate_y, 0)])
        visited[self.gate_y][self.gate_x] = True
        far_cells = []
        while queue:
            x, y, dist = queue.popleft()
            if dist >= 30 and self.labirynth[y][x] == 0:
                far_cells.append((x, y))
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < self.width and 0 <= ny < self.height and not visited[ny][nx] and self.labirynth[ny][nx] == 0:
                    visited[ny][nx] = True
                    queue.append((nx, ny, dist+1))
        if far_cells:
            self.gate_key_x, self.gate_key_y = random.choice(far_cells)
            self.labirynth[self.gate_key_y][self.gate_key_x] = "GK"
        else:
            self.gate_key_x, self.gate_key_y = -1, -1

    def show_minimap(self): # wyświetlanie minimapy
        minimap = tk.Toplevel(self.root)
        minimap.title("Minimap")
        cell_size = 8  # Small cells for minimap
        canvas = tk.Canvas(minimap, width=self.width*cell_size, height=self.height*cell_size, bg="white")
        canvas.pack()

        for y in range(self.height):
            for x in range(self.width):
                if not self.discovered[y][x]:
                    color = "blue"  # Unknown
                elif (x, y) == (self.exit_x, self.exit_y):
                    color = "green"  # Exit
                elif isinstance(self.labirynth[y][x], str) and self.labirynth[y][x].startswith("K"):
                    color = "yellow"  # Key
                elif self.labirynth[y][x] == 1:
                    color = "black"  # Wall
                else:
                    color = "white"  # Path
                canvas.create_rectangle(
                    x*cell_size, y*cell_size, (x+1)*cell_size, (y+1)*cell_size,
                    fill=color, outline=""
                )
        # Mark player position
        canvas.create_rectangle(
            self.player_x*cell_size, self.player_y*cell_size,
            (self.player_x+1)*cell_size, (self.player_y+1)*cell_size,
            fill="red", outline=""
        )

    def place_enemies(self):
        possible = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if self.labirynth[y][x] == 0
            and (x, y) != (self.player_x, self.player_y)
            and (x, y) != (self.exit_x, self.exit_y)
            and (x, y) != (self.torch_x, self.torch_y)
            and (x, y) != (self.gate_x, self.gate_y)
            and (x, y) != (self.gate_key_x, self.gate_key_y)
            and not any((abs(x-ex) <= 1 and abs(y-ey) <= 1) for (ex, ey) in self.enemies)
        ]
        random.shuffle(possible)
        for _ in range(self.enemies_number):
            for idx, (x, y) in enumerate(possible):
                if all(abs(x-ex) > 1 or abs(y-ey) > 1 for (ex, ey) in self.enemies):
                    self.enemies.append((x, y))
                    self.labirynth[y][x] = "GRASS"
                    possible.pop(idx)
                    break

    def save_game(self, filename="savegame.pkl"):
        state = {
            "labirynth": self.labirynth,
            "player_x": self.player_x,
            "player_y": self.player_y,
            "previous_x": self.previous_x,
            "previous_y": self.previous_y,
            "exit_x": self.exit_x,
            "exit_y": self.exit_y,
            "doors": self.doors,
            "keys_pos": self.keys_pos,
            "keys": self.keys,
            "points": self.points,
            "hearts": self.hearts,
            "inventory": self.inventory,
            "torch_x": self.torch_x,
            "torch_y": self.torch_y,
            "gate_x": getattr(self, "gate_x", -1),
            "gate_y": getattr(self, "gate_y", -1),
            "gate_key_x": getattr(self, "gate_key_x", -1),
            "gate_key_y": getattr(self, "gate_key_y", -1),
            "discovered": self.discovered,
            "enemies": self.enemies,
            "grass_monsters": list(self.grass_monsters),
            "player_moves": self.player_moves,
            "monster_turns_left": self.monster_turns_left,
            "monster_hidden_turns": self.monster_hidden_turns,
            "monster_visible_turns": self.monster_visible_turns,
            "monsters_are_visible": self.monsters_are_visible,
            "game_time": self.game_time,
            "start_time": self.start_time,
            "difficulty": self.difficulty,
        }
        with open(filename, "wb") as f:
            pickle.dump(state, f)
        messagebox.showinfo("Game Saved", "Your game has been saved!")

    def load_game(self, filename="savegame.pkl"):
        with open(filename, "rb") as f:
            state = pickle.load(f)
        self.labirynth = state["labirynth"]
        self.player_x = state["player_x"]
        self.player_y = state["player_y"]
        self.previous_x = state["previous_x"]
        self.previous_y = state["previous_y"]
        self.exit_x = state["exit_x"]
        self.exit_y = state["exit_y"]
        self.doors = state["doors"]
        self.keys_pos = state["keys_pos"]
        self.keys = state["keys"]
        self.points = state["points"]
        self.hearts = state["hearts"]
        self.inventory = state["inventory"]
        self.torch_x = state["torch_x"]
        self.torch_y = state["torch_y"]
        self.gate_x = state.get("gate_x", -1)
        self.gate_y = state.get("gate_y", -1)
        self.gate_key_x = state.get("gate_key_x", -1)
        self.gate_key_y = state.get("gate_key_y", -1)
        self.discovered = state["discovered"]
        self.enemies = state["enemies"]
        self.grass_monsters = set(state["grass_monsters"])
        self.player_moves = state["player_moves"]
        self.monster_turns_left = state["monster_turns_left"]
        self.monster_hidden_turns = state["monster_hidden_turns"]
        self.monster_visible_turns = state["monster_visible_turns"]
        self.monsters_are_visible = state["monsters_are_visible"]
        self.game_time = state["game_time"]
        self.start_time = state["start_time"]
        self.difficulty = state["difficulty"]
        self.draw_labirynth()
        messagebox.showinfo("Game Loaded", "Your game has been loaded!")

    @staticmethod
    def start_game_with_difficulty(root, difficulty): # uruchomienie gry z wybranym poziomem trudności
        root.deiconify()
        LabirynthGame(root, difficulty)
    
    @staticmethod
    def choose_difficulty(root, callback): # wybór poziomu trudności
        dialog = tk.Toplevel(root)
        dialog.title("Choose Difficulty")

        tk.Label(dialog, text="Choose difficulty level:", font=('Arial', 12)).pack(pady=10)

        def start_and_close(difficulty):
            dialog.destroy()
            callback(root, difficulty)

        def load_and_start():
            root.deiconify()
            game = LabirynthGame(root, "easy")  # Difficulty will be overwritten by save
            game.load_game()

        tk.Button(dialog, text="Easy", command=lambda: start_and_close("easy")).pack(fill=tk.X, padx=20, pady=5)
        tk.Button(dialog, text="Medium", command=lambda: start_and_close("medium")).pack(fill=tk.X, padx=20, pady=5)
        tk.Button(dialog, text="Hard", command=lambda: start_and_close("hard")).pack(fill=tk.X, padx=20, pady=5)
        tk.Button(dialog, text="Load Game", command=load_and_start).pack(fill=tk.X, padx=20, pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    LabirynthGame.choose_difficulty(root, LabirynthGame.start_game_with_difficulty)
    root.mainloop()