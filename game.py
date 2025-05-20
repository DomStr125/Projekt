import random
import time
import tkinter as tk
from tkinter import messagebox
from collections import deque

class LabirynthGame:

    DIFFICULTY_SETTINGS = {
        "easy": {
            "width": 30,
            "height": 15,
            "doors": 1,
            "max_keys": 1,
            "hearts": 5,
            "enemies": 0,
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
            "width": 60,
            "height": 30,
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
        self.enemies = self.DIFFICULTY_SETTINGS[difficulty]["enemies"]

        self.inventory = {
            "keys": [],
            "special_items": []
        }

        self.points = 0
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
        self.create_key_door()
        self.labirynth[self.key_y][self.key_x] = "K"
        self.labirynth[self.door_y][self.door_x] = "D"
        self.labirynth[self.torch_x][self.torch_y] = "T"

        self.place_torch()

        self.canvas = tk.Canvas(root, width=self.width * self.cell_size, height=self.height * self.cell_size, bg="white")
        self.canvas.pack(expand=True, fill=tk.BOTH)      
        self.root.bind("<KeyPress>", self.on_key_press)
        self.draw_labirynth()

    def load_textures(self): # ładowanie tekstur
        textures = {
            "wall": tk.PhotoImage(file="grafika/wall.png"),
            "path": tk.PhotoImage(file="grafika/path.png"),
            "player": tk.PhotoImage(file="grafika/knight.png"),
            "exit": tk.PhotoImage(file="grafika/exit.png"),
            "key": tk.PhotoImage(file="grafika/silver_key.png"),
            "door": tk.PhotoImage(file="grafika/silver_door.png"),
            "fog": tk.PhotoImage(file="grafika/fog.png"),
            "torch": tk.PhotoImage(file="grafika/torch.png")
            # "background": tk.PhotoImage(file="grafika/background.png")  # <-- REMOVE THIS LINE
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
                if ((x - self.player_x) ** 2 + (y - self.player_y) ** 2) <= self.vision_range ** 2:
                    if (x, y) == (self.exit_x, self.exit_y):
                        self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor=tk.NW, image=self.textures["exit"])
                    elif (x, y) == (self.player_x, self.player_y):
                        self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor=tk.NW, image=self.textures["player"])
                    elif (x, y) == (self.key_x, self.key_y) and self.labirynth[y][x] == "K":
                        self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor=tk.NW, image=self.textures["key"])
                    elif (x, y) == (self.door_x, self.door_y) and self.door_active:
                        self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor=tk.NW, image=self.textures["door"])
                    elif (x, y) == (self.torch_x, self.torch_y):
                        self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor=tk.NW, image=self.textures["torch"])
                else:
                    self.canvas.create_image(x * self.cell_size, y * self.cell_size, anchor=tk.NW, image=self.textures["fog"])

    def on_key_press(self, event): # obsługa klawiszy
        new_x, new_y = self.player_x, self.player_y
        previous_x, previous_y = self.player_x, self.player_y

        if event.keysym in ("w", "Up"):
            new_y -= 1
        elif event.keysym in ("s", "Down"):
            new_y += 1
        elif event.keysym in ("a", "Left"):
            new_x -= 1
        elif event.keysym in ("d", "Right"):
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
                self.points += 200
                self.label_points.config(text=f"Punkty: {self.points}")
                print("You opened the door!")
            else:
                print("You need a key to open this door!")
                self.player_x, self.player_y = previous_x, previous_y
        
        if (self.player_x, self.player_y) == (self.torch_x, self.torch_y):
            self.labirynth[self.torch_y][self.torch_x] = 0
            self.torch_x, self.torch_y = -1, -1
            self.vision_range += 2
            self.points += 100
            self.label_points.config(text=f"Punkty: {self.points}")
            print("You found a torch! Vision increased.")
            self.inventory["special_items"].append("torch")
            self.draw_labirynth()

        if (self.player_x, self.player_y) == (self.exit_x, self.exit_y): # wyjście z labiryntu
            self.is_game_active = False
            final_time = int(time.time() - self.start_time)
            messagebox.showinfo("Congratulations!", f"You've reached the exit in {final_time}s \n Your score: {self.points}")
            self.root.quit()
                   
    def create_key_door(self): # tworzenie klucza i drzwi
        reachable_paths = self.find_reachable_paths(self.player_x, self.player_y)

        # tworzenie klucza
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

        tk.Button(dialog, text="Easy", command=lambda: start_and_close("easy")).pack(fill=tk.X, padx=20, pady=5)
        tk.Button(dialog, text="Medium", command=lambda: start_and_close("medium")).pack(fill=tk.X, padx=20, pady=5)
        tk.Button(dialog, text="Hard", command=lambda: start_and_close("hard")).pack(fill=tk.X, padx=20, pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    LabirynthGame.choose_difficulty(root, LabirynthGame.start_game_with_difficulty)
    root.mainloop()