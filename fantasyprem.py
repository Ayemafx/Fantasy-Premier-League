import tkinter as tk
from tkinter import messagebox
import sqlite3
import requests
from tkinter import *
import os


class FootballApp:
    def __init__(self):
        # Initialize database
        self.conn = sqlite3.connect("football_app.db")
        self.create_tables()

        # Variables
        self.current_user = None

        # Variables for player grid
        self.player_grid = [[None for _ in range(9)] for _ in range(4)]  # 4x9 grid
        self.selected_position = None

        self.bank = 100  # Default bank value in millions

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                favorite_team TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        cursor.execute('''  
            CREATE TABLE IF NOT EXISTS player_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                position_row INTEGER,
                position_col INTEGER,
                player_name TEXT,
                cost REAL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE (user_id, position_row, position_col)
            )

        ''')  #filter out the data using SELECT * FROM player_info WHERE user_id = 102;

        self.conn.commit()

    def get_teams_from_api(self):
        try:
            response = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
            data = response.json()

            teams = [team['name'] for team in data['teams']]
            return teams
        except requests.exceptions.RequestException as e:
            messagebox.showerror("API Error", f"Error accessing FPL API: {e}")
            return []

    def main_account_screen(self):
        # Rest of your existing code
        self.first_screen = Tk()
        self.first_screen.geometry("300x250")
        self.first_screen.title("Login:")
        Label(text="Login Screen", width="300", height="2", font=("Blackadder ITC", 25)).pack()
        Label(text="").pack()
        Button(text="Login", height="2", bg="medium spring green", width="30", command=self.login).pack()
        Label(text="").pack()
        Button(text="Register", height="2", bg="light cyan", width="30", command=self.register).pack()
        self.first_screen.mainloop()

    def is_new_user(self):
        # Check if there are any records in the teams or player_info tables for the current user
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT COUNT(*)
            FROM teams
            WHERE user_id = (SELECT id FROM users WHERE username = ?)
        ''', (self.current_user[0],))
        teams_count = cursor.fetchone()[0]

        cursor.execute('''
            SELECT COUNT(*)
            FROM player_info
            WHERE user_id = (SELECT id FROM users WHERE username = ?)
        ''', (self.current_user[0],))
        player_info_count = cursor.fetchone()[0]

        # If there are no associated records, consider the user as new
        return teams_count == 0 and player_info_count == 0

    def clear_database(self, user_id):
        cursor = self.conn.cursor()

        # Delete records from the player_info table for the specified user_id
        cursor.execute('DELETE FROM player_info WHERE user_id = ?', (user_id,))

        # Delete records from the teams table for the specified user_id
        cursor.execute('DELETE FROM teams WHERE user_id = ?', (user_id,))

        # Reset the bank value to 100M
        self.bank = 100.0

        # Commit the changes to the database
        self.conn.commit()

        # Optionally, you can print a message to indicate that the database has been cleared
        print(f"Database cleared for user with user_id {user_id}.")

    def register(self):
        self.registering_screen = Toplevel(self.first_screen)
        self.registering_screen.title("Register")
        self.registering_screen.geometry("300x250")

        self.username = StringVar()
        self.password = StringVar()

        Label(self.registering_screen, text="Please enter the credentials below").pack()
        Label(self.registering_screen, text="").pack()

        username_lable = Label(self.registering_screen, text="Username")
        username_lable.pack()
        self.username_entry = Entry(self.registering_screen, textvariable=self.username)
        self.username_entry.pack()

        password_lable = Label(self.registering_screen, text="Password")
        password_lable.pack()
        self.password_entry = Entry(self.registering_screen, textvariable=self.password, show='*')
        self.password_entry.pack()

        Label(self.registering_screen, text="").pack()
        Button(self.registering_screen, text="Register", width=10, bg="light cyan", height=1,
               command=self.register_user).pack()

    def login(self):
        self.login_screen = Toplevel(self.first_screen)
        self.login_screen.title("Login")
        self.login_screen.geometry("300x250")

        Label(self.login_screen, text="Please enter details below to login").pack()
        Label(self.login_screen, text="").pack()

        self.username_verify = StringVar()
        self.password_verify = StringVar()

        Label(self.login_screen, text="Username").pack()
        self.username_login_entry = Entry(self.login_screen, textvariable=self.username_verify)
        self.username_login_entry.pack()

        Label(self.login_screen, text="").pack()
        Label(self.login_screen, text="Password").pack()
        self.password_login_entry = Entry(self.login_screen, textvariable=self.password_verify, show='*')
        self.password_login_entry.pack()

        Label(self.login_screen, text="").pack()
        Button(self.login_screen, text="Login", bg="medium spring green", width=10, height=1, command=self.login_verify).pack()

    def register_user(self):
        username_info = self.username.get()
        password_info = self.password.get()
        list_of_files = os.listdir()

        for i in range(1):
            if not self.username.get() and not self.password.get():
                self.registering_screen.destroy()
                messagebox.showerror("Error", "Blank Entries!")
                self.register()

            elif username_info == password_info:
                self.registering_screen.destroy()
                messagebox.showerror("Error", "Username and Password cant be the same")
                self.register()

            elif username_info in list_of_files:
                self.registering_screen.destroy()
                messagebox.showerror("Error", "Username already taken!")
                self.register()

            elif len(password_info) >= 9:
                self.registering_screen.destroy()
                messagebox.showerror("Error", "Password has to be 8 characters or less!")
                self.register()

            else:
                file = open(username_info, "w")
                file.write(username_info + "\n")
                file.write(password_info)
                file.close()

                self.username_entry.delete(0, END)
                self.password_entry.delete(0, END)

                Label(self.registering_screen, text="Registration Success", fg="green", font=("calibri", 11)).pack()
                break

    def login_verify(self):
        self.name = self.username_verify.get()
        password1 = self.password_verify.get()
        self.username_login_entry.delete(0, END)
        self.password_login_entry.delete(0, END)

        list_of_files = os.listdir()
        if self.name in list_of_files:
            file_path = os.path.join(self.name)
            with open(file_path, "r") as file1:
                lines = file1.read().splitlines()
                if password1 == lines[1]:
                    # Set self.current_user with user information
                    self.current_user = (lines[0],)
                    self.login_success()
                else:
                    self.password_not_recognised()
            file1.close()
        else:
            self.user_not_found()

    def login_success(self):
        print("Login success method")
        self.login_success_screen = Toplevel(self.login_screen)
        self.login_success_screen.title("Success")
        self.login_success_screen.geometry("150x100")

        Label(self.login_success_screen, text="Successfully logged in").pack()
        Button(self.login_success_screen, text="OK", command=self.delete_login_success).pack()
        self.first_screen.destroy()

        # Check if the user has already selected a team
        saved_team = self.get_saved_team(self.current_user[0])

        if saved_team:
            print("Saved team:", saved_team)
            self.team_name_value, self.favorite_team = saved_team  # Set the values here
            print("Team values set")
            self.open_grid_frame()
        else:
            print("No saved team")
            self.team_selection_frame()

    def password_not_recognised(self):
        self.password_not_recogognised_screen = Toplevel(self.login_screen)
        self.password_not_recogognised_screen.title("Success")
        self.password_not_recogognised_screen.geometry("150x100")

        Label(self.password_not_recogognised_screen, text="Invalid Password ").pack()
        Button(self.password_not_recogognised_screen, text="OK", command=self.delete_password_not_recognised).pack()

    def user_not_found(self):
        self.unknown_user_screen = Toplevel(self.login_screen)
        self.unknown_user_screen.title("Success")
        self.unknown_user_screen.geometry("150x100")

        Label(self.unknown_user_screen, text="Error, User Not Found").pack()
        Button(self.unknown_user_screen, text="OK", command=self.delete_user_not_found_screen).pack()

    def team_selection_frame(self):
        self.team_frame = Tk()
        self.team_frame.geometry("300x250")
        self.team_frame.title("Select Teams")
        self.favorite_team = StringVar()
        self.team_name = StringVar()

        Label(self.team_frame, text="Favorite Team:", font=("Blackadder ITC", 15)).pack()

        teams = self.get_teams_from_api()

        self.favorite_team.set("Favourite Team")
        self.favorite_team_dropdown = OptionMenu(self.team_frame, self.favorite_team, *teams)
        self.favorite_team_dropdown.pack()

        Label(self.team_frame, text="Team Name:", font=("Blackadder ITC", 15)).pack()
        self.team_name_entry = Entry(self.team_frame, textvariable=self.team_name)
        self.team_name_entry.pack()

        select_button = Button(self.team_frame, height="2", bg="medium spring green", width="30", text="Select Team",
                               command=self.select_team)
        select_button.pack(pady=10)

        self.team_frame.mainloop()

    def select_team(self):
        print("Select team method")
        # Get the team name and favorite team from the entry fields
        self.team_name_value = self.team_name.get()
        self.favorite_team_value = self.favorite_team.get()

        print("Team name:", self.team_name_value)
        print("Favorite team:", self.favorite_team_value)

        # Check if either field is empty
        if not self.team_name_value or not self.favorite_team_value:
            messagebox.showerror("Error", "Please enter both Team Name and Favorite Team.")
            return  # Stop further execution

        # If both fields are non-empty, proceed with inserting the new team information
        cursor = self.conn.cursor()

        # Check if the user already has a team selected
        existing_team = self.get_saved_team(self.current_user[0])

        if existing_team:
            self.open_grid_frame()
        else:
            # Insert the new team information
            cursor.execute("INSERT INTO teams (user_id, name, favorite_team) VALUES (?, ?, ?)",
                           (self.current_user[0], self.team_name_value, self.favorite_team_value))

        self.conn.commit()
        messagebox.showinfo("Success", "Team selected successfully.")

        self.team_frame.destroy()
        self.open_grid_frame()

    def get_saved_team(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT name, favorite_team FROM teams WHERE user_id = ?', (user_id,))
        return cursor.fetchone()

    def refresh(self):
        # Close the current grid frame
        self.grid_frame.destroy()

        # Calculate the new bank value based on the current saved players
        saved_players = self.get_saved_players(self.current_user[0])
        self.bank = 100.0 - sum(player[3] for player in saved_players)  # Assuming cost is at index 3

        # Open the display saved grid window again
        self.display_saved_grid(saved_players)

    def open_grid_frame(self):
        # print("Debug - Team Name:", self.team_name_value)
        # print("Debug - Favorite Team:", self.favorite_team)

        # Check if the user has already selected players
        saved_players = self.get_saved_players(self.current_user[0])

        if saved_players:
            # If players are already saved, display the saved grid
            self.display_saved_grid(saved_players)
        else:
            # If no players are saved, create a new grid
            self.create_new_grid()

    def display_saved_grid(self, saved_players):
        print("Debug - Saved Players:", saved_players)
        self.grid_frame = Tk()
        self.grid_frame.geometry("800x300")
        self.grid_frame.title(f"Your Team: {self.team_name_value}; Favourite Team: {self.favorite_team}")

        # Display the initial bank amount
        bank_label = Label(self.grid_frame, text=f"Bank: {self.bank}M", font=("Blackadder ITC", 15))
        bank_label.grid(row=0, column=0, columnspan=9, pady=10)

        # Display a clear database button
        clear_btn = Button(self.grid_frame, text="Clear", bg="lightsteelblue1", width=8, height=1,
                           command=lambda: self.clear_database(self.current_user[0]))
        clear_btn.grid(row=0, column=8, pady=10)

        # Display a refresh button
        refresh_btn = Button(self.grid_frame, text="Refresh", bg="lightcoral", width=8, height=1,
                             command=self.refresh)
        refresh_btn.grid(row=0, column=9, pady=10)

        # Define the grid layout
        grid_layout = [
            ["GKP", None, "GKP"],
            ["DEF", None, "DEF", None, "DEF", None, "DEF", None, "DEF"],
            ["MID", None, "MID", None, "MID", None, "MID", None, "MID"],
            ["FWD", None, "FWD", None, "FWD"]
        ]

        # Iterate through saved player info and update the grid
        for player_info in saved_players:
            row, col, player_name, cost = player_info
            init_row = row - 1
            # Ensure there are enough rows in the grid_layout
            while len(grid_layout) <= init_row:
                grid_layout.append([""] * len(grid_layout[0]))  # Fill new rows with empty strings
            # Ensure there are enough columns in the row
            while len(grid_layout[init_row]) <= col * 2:
                grid_layout[init_row].append(None)
            # Update the grid layout with the player's name
            grid_layout[init_row][col] = player_name
            self.update_button(init_row, col, player_name, cost)

        # Use the same code as in open_grid_frame to display the grid
        for i, row in enumerate(grid_layout, start=1):  # Start from row 1 to leave space for bank label
            for j, position in enumerate(row):
                if position is not None:
                    button = Button(self.grid_frame, text=f"{position}", bg="medium spring green", width=15, height=1,
                                    command=lambda i=i, j=j: self.select_position(i, j))  # Adjust row and col index
                    button.grid(row=i, column=j, pady=10, padx=10)

        # Debug statement to print out the updated grid
        print("Debug - Updated Grid Layout:")
        for row in grid_layout:
            print(row)

        self.grid_frame.mainloop()

    def create_new_grid(self):
        self.grid_frame = Tk()
        self.grid_frame.geometry("800x300")
        self.grid_frame.title(f"Your Team: {self.team_name_value}; Favourite Team: {self.favorite_team}")

        # Display the initial bank amount
        bank_label = Label(self.grid_frame, text=f"Bank: {self.bank}M", font=("Blackadder ITC", 15))
        bank_label.grid(row=0, column=0, columnspan=9, pady=10)

        # Display a refresh button
        refresh_btn = Button(self.grid_frame, text="Refresh", bg="lightcoral", width=8, height=1,
                             command=self.refresh)
        refresh_btn.grid(row=0, column=8, pady=10)

        # Define the layout of the grid
        grid_layout = [
            ["GKP", None, "GKP"],
            ["DEF", None, "DEF", None, "DEF", None, "DEF", None, "DEF"],
            ["MID", None, "MID", None, "MID", None, "MID", None, "MID"],
            ["FWD", None, "FWD", None, "FWD"]
        ]

        for i, row in enumerate(grid_layout, start=1):  # Start from row 1 to leave space for bank label
            for j, position in enumerate(row):
                if position:
                    button = Button(self.grid_frame, text=f"{position}", bg="medium spring green", width=15, height=1,
                                    command=lambda i=i, j=j: self.select_position(i, j))  # Adjust row index
                    button.grid(row=i, column=j, pady=10, padx=10)
                    # Initialize the player grid with None values
                    # self.player_grid[i - 1][j] = button  # Store the button reference in the grid

        # Add debug print to check the grid layout
        print("Debug - Grid Layout:")
        for row in self.player_grid:
            print([button if button else None for button in row])

        self.grid_frame.mainloop()

    def select_position(self, row, col):
        print(f"DEBUG: Selected position - row: {row}, col: {col}")

        # Set the selected_position attribute with the current (row, col) tuple
        self.selected_position = (row, col)

        # Get the position string based on the selected position tuple
        position_string = self.get_position_string(row, col)

        self.show_player_selection_dialog(position_string)

    def get_position_string(self, row, col):
        # Define the mapping of rows to player positions
        position_mapping = {
            1: "Goalkeeper",
            2: "Defender",
            3: "Midfielder",
            4: "Forward",
            # Add more positions as needed
        }

        # Get the position string based on the row
        self.position_string = position_mapping.get(row, "Unknown")
        # Print the selected position string for debugging
        print(f"DEBUG: Selected position string: {self.position_string}")

        return self.position_string

    def show_player_selection_dialog(self, position):
        self.dialog = tk.Toplevel()
        self.dialog.title("Select Player")
        self.dialog.geometry("300x250")

        self.player_var = tk.StringVar()

        Label(self.dialog, text="Select a player:", font=("Blackadder ITC", 15)).pack()

        players = self.get_players_from_api(position)

        # Use a StringVar to track the selected player and update the OptionMenu dynamically
        self.player_var.set("Select Your Player")

        # Use a trace on the StringVar to dynamically update the player list
        self.player_var.trace("w", lambda *args: self.update_player_menu_list(position))

        self.player_menu = OptionMenu(self.dialog, self.player_var, *players)
        self.player_menu.pack()

        cost_label = Label(self.dialog, text="Cost: ")
        cost_label.pack()

        # Bind the <FocusOut> and <Configure> events to the update function
        self.player_menu.bind("<FocusOut>",
                              lambda event, cost_label=cost_label: self.update_player_menu_label(cost_label))
        self.player_menu.bind("<Configure>",
                              lambda event, cost_label=cost_label: self.update_player_menu_label(cost_label))

        # Add a button to save the selected player and cost
        save_button = Button(self.dialog, text="Save", bg="medium spring green", width="30", command=lambda: self.save_player_info())
        save_button.pack()

        # Add a button to close the dialog
        close_button = Button(self.dialog, text="Close", bg="cornflowerblue", width="30", command=self.dialog.destroy)
        close_button.pack(pady=5)

        self.dialog.mainloop()

    def update_player_menu_label(self, cost_label, event=None):
        selected_player = self.player_var.get()
        selected_player_cost = self.get_player_cost(selected_player)

        # Debug print statement
        print(f"Selected Player: {selected_player}, Cost: {selected_player_cost}")

        # Update cost label text
        cost_label.config(text=f"Cost: {selected_player_cost}M")

    def update_player_menu_list(self, position):
        # Get the updated list of players after removing the selected player
        players_from_api = self.get_players_from_api(position)
        saved_players = self.get_saved_players(self.current_user[0])

        # Set the updated player list in the OptionMenu
        menu = self.player_menu["menu"]
        menu.delete(0, "end")  # Clear the existing menu options

        for player in players_from_api:
            # Check if the player is not in the saved players database before adding to the menu
            if player not in saved_players:
                menu.add_command(label=player, command=lambda value=player: self.player_var.set(value))

    def save_player_info(self):
        selected_player = self.player_var.get()

        # Check if a player is selected
        if selected_player != "Select Your Player":
            # Get the position for which the player is selected
            position_row, position_col = self.get_selected_position()

            # Retrieve the user ID for the current user
            user_id = self.current_user[0]

            # Get the cost of the selected player (you may need to fetch this from your API)
            selected_player_cost = self.get_player_cost(selected_player)

            # Debug statement to display selected player information
            print(
                f"Selected Player: {selected_player}, Position: ({position_row}, {position_col}), User ID: {user_id}, Cost: {selected_player_cost}")

            # Check if the user already has a player in the selected position
            existing_player = self.get_existing_player(user_id, position_row, position_col)

            if existing_player:
                # Display a message box indicating that the player already exists
                message = f"{existing_player} with cost {selected_player_cost} already exists in the selected position."
                messagebox.showinfo("Player Already Exists", message)
            else:
                # Debug statement for a new player
                print("No existing player found. Inserting a new player.")

                # Insert a new player record
                self.insert_new_player(user_id, position_row, position_col, selected_player, selected_player_cost)
                print("Inserted new player.")

            # Close the dialog after saving
            self.dialog.destroy()

            self.refresh()

    def get_existing_player_by_name(self, user_id, player_name):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT player_name, cost FROM player_info WHERE user_id = ? AND player_name = ?',
            (user_id, player_name))
        return cursor.fetchone()

    def get_players_from_api(self, position):
        try:
            response = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
            data = response.json()
            print(f"DEBUG: Getting players for position: {position}")

            # Map FPL element types to position names
            position_mapping = {
                "Goalkeeper": 1,
                "Defender": 2,
                "Midfielder": 3,
                "Forward": 4,
            }

            self.position_id = position_mapping.get(position)

            if self.position_id is not None:
                players = [
                    {
                        'web_name': player['web_name'],
                        'cost': player['now_cost'] / 10,  # Convert cost to millions
                    }
                    for player in data['elements'] if player['element_type'] == self.position_id
                ]

                # Extract relevant player information, e.g., player names and costs
                self.player_info = players

                print(f"DEBUG: Players for {position}: {self.player_info}")

                return [player['web_name'] for player in players]  # Return only player names
            else:
                messagebox.showerror("Position Error", f"Invalid position: {position}")
                return []

        except requests.exceptions.RequestException as e:
            messagebox.showerror("API Error", f"Error accessing FPL API: {e}")
            return []

    def get_player_cost(self, selected_player):
        for player in self.player_info:
            if player['web_name'] == selected_player:
                return player['cost']
        return 0

    def insert_new_player(self, user_id, position_row, position_col, player_name, cost):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO player_info (user_id, position_row, position_col, player_name, cost)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, position_row, position_col, player_name, cost))
        self.conn.commit()

    def update_existing_player(self, existing_player_id, player_name, cost):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE player_info
            SET player_name = ?, cost = ?
            WHERE id = ?
        ''', (player_name, float(cost), existing_player_id))
        self.conn.commit()

    def get_existing_player(self, user_id, position_row, position_col):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT player_name, cost FROM player_info WHERE user_id = ? AND position_row = ? AND position_col = ?',
            (user_id, position_row, position_col))
        return cursor.fetchone()

    def get_saved_players(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT position_row, position_col, player_name, cost FROM player_info WHERE user_id = ?',
                       (user_id,))
        saved_players = cursor.fetchall()
        print("Debug - Saved Players from Database:", saved_players)
        return saved_players

    def get_selected_position(self):
        if self.selected_position:
            return self.selected_position
        else:
            messagebox.showerror("Error", "No position selected.")
            return None

    def save_player_to_database(self, player, cost, row, col):
        # Get the current user's ID
        user_id = self.get_user_id()

        # Check if there is already a player at the specified position
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT id, player_name, cost FROM player_info WHERE user_id = ? AND position_row = ? AND position_col = ?',
            (user_id, row, col))
        existing_player = cursor.fetchone()

        if existing_player:
            # Player already exists at the specified position
            existing_player_name, existing_player_cost = existing_player[1], existing_player[2]
            messagebox.showwarning("Duplicate Entry",
                                   f"A player already exists at this position: {existing_player_name} (Cost: {existing_player_cost}M). Choose a different position.")
        else:
            # Insert the player information into the database
            cursor.execute('''
                INSERT INTO player_info (user_id, position_row, position_col, player_name, cost)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, row, col, player, cost))
            self.conn.commit()

            # Check the content of the player_info table
            cursor.execute('SELECT * FROM player_info')
            data = cursor.fetchall()
            print("Data in player_info table:", data)

    def update_button(self, row, col, player_name, cost):
        print(f"Debug - Update Button - row: {row}, col: {col}, player: {player_name}, cost: {cost}")
        # Access the button widget at the specified position in the grid
        button = self.player_grid[row - 1][col]  # Adjust row index

        if not button:  # Check if the button has no player stored
            # Store player information in the grid
            self.player_grid[row - 1][col] = {'player': player_name, 'cost': cost}

            # Update bank value
            self.bank -= cost

            # Round the bank value to two decimal places
            self.bank = round(self.bank, 2)

            # Update UI to reflect the change in the grid and the bank value
            bank_label = Label(self.grid_frame, text=f"Bank: {self.bank}M", font=("Blackadder ITC", 15))
            bank_label.grid(row=0, column=0, columnspan=9, pady=10)

            # Save the player information to the database
            self.save_player_to_database(player_name, cost, row, col)
        # elif isinstance(button, Button):  # Check if the button is not the refresh button
        #     # If the button already has a player stored, display a message
        #     messagebox.showinfo("Player Already Selected", "You have already selected a player at this position.")

    def get_user_id(self):
        # Retrieve the user ID using the current user's username
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (self.current_user[0],))
        user_id = cursor.fetchone()
        return user_id[0] if user_id else None

    def delete_team_selection(self):
        self.team_frame.destroy()

    def delete_login_success(self):
        self.login_success_screen.destroy()

    def delete_password_not_recognised(self):
        self.password_not_recogognised_screen.destroy()

    def delete_user_not_found_screen(self):
        self.unknown_user_screen.destroy()


if __name__ == "__main__":
    app = FootballApp()
    app.main_account_screen()
