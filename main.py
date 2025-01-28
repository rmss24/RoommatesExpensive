import customtkinter as ctk
from tkinter import messagebox
from CTkListbox import CTkListbox
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import json
import os
from CTkTable import CTkTable
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import locale
import matplotlib.dates
import matplotlib
import numpy as np
from sklearn.linear_model import LinearRegression
matplotlib.use('TkAgg') 
from matplotlib.dates import MonthLocator, DateFormatter

class Roommate:
    def __init__(self, name):
        self.name = name
        self.payments = 0

    def add_payment(self, amount):
        self.payments += amount


def calculate_differences(roommates, total_expenses):
    individual_share = total_expenses / len(roommates)
    balance = {r.name: r.payments - individual_share for r in roommates}
    return balance


class ExpenseManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Roommate Expense Management")
        self.root.geometry("1000x800")
        
        # File path to save data
        self.data_file = "expense_history.json"
        self.expense_history = self.load_history()
        
        # Create the main panel
        self.notebook = ctk.CTkTabview(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Tabs for expense management
        self.tab_management = self.notebook.add("Expense Management")
        self.tab_history = self.notebook.add("History and Charts")
        self.tab_predictions = self.notebook.add("Predictions")  # New tab for predictions
        
        # Setup the main frame in the management tab
        self.main_frame = ctk.CTkFrame(
            self.tab_management,
            corner_radius=10,
            fg_color=("gray90", "gray13")
        )
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.roommates = []

        # Responsive layout for widgets
        self.name_label = ctk.CTkLabel(self.main_frame, text="Roommate Name:")
        self.name_label.grid(row=0, column=0, pady=10, padx=10, sticky="w")
        
        self.name_var = ctk.StringVar()
        self.name_entry = ctk.CTkEntry(self.main_frame, textvariable=self.name_var, width=200)
        self.name_entry.grid(row=0, column=1, pady=10, padx=10, sticky="ew")

        self.add_button = ctk.CTkButton(self.main_frame, text="Add Roommate",
                                        command=self.add_roommate)
        self.add_button.grid(row=0, column=2, pady=10, padx=10, sticky="ew")

        self.amount_label = ctk.CTkLabel(self.main_frame, text="Amount:")
        self.amount_label.grid(row=1, column=0, pady=10, padx=10, sticky="w")

        self.amount_var = ctk.StringVar()
        self.amount_entry = ctk.CTkEntry(
            self.main_frame, 
            textvariable=self.amount_var, 
            width=200,
            state="normal" 
        )
        self.amount_entry.grid(row=1, column=1, pady=5, padx=10, sticky="ew")

        self.payment_button = ctk.CTkButton(self.main_frame, text="Record Payment",
                                            command=self.record_payment)
        self.payment_button.grid(row=1, column=2, pady=5, padx=10, sticky="ew")

        self.roommate_list = CTkListbox(
            self.main_frame,
            width=400,
            height=200,
            text_color="white",
            fg_color="black",
            command=self.on_select_roommate 
        )
        self.roommate_list.grid(row=2, column=0, columnspan=3, pady=20, sticky="nsew")

        self.remove_button = ctk.CTkButton(self.main_frame, text="Remove Roommate",
                                           command=self.remove_roommate)
        self.remove_button.grid(row=3, column=0, columnspan=3, pady=10, sticky="ew")

        self.calculate_button = ctk.CTkButton(self.main_frame, text="Calculate Balance",
                                              command=self.show_balance)
        self.calculate_button.grid(row=4, column=0, columnspan=3, pady=10, sticky="ew")

        self.show_history_button = ctk.CTkButton(
            self.main_frame, 
            text="Show History and Charts",
            command=self.show_charts
        )
        self.show_history_button.grid(row=5, column=0, columnspan=3, pady=10, sticky="ew")

        # Configure grid for responsiveness
        self.main_frame.grid_rowconfigure(2, weight=1)  # Allows the list to expand
        self.main_frame.grid_columnconfigure(1, weight=1)  # Allows the entry to expand

        # Setup the main frame in the predictions tab
        self.predictions_frame = ctk.CTkFrame(self.tab_predictions)
        self.predictions_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.prediction_button = ctk.CTkButton(
            self.predictions_frame, 
            text="Predict Future Expenses",
            command=self.predict_expenses
        )
        self.prediction_button.pack(pady=20)

        self.prediction_label = ctk.CTkLabel(self.predictions_frame, text="")
        self.prediction_label.pack(pady=10)

    def on_select_roommate(self, name):
        """Callback when a roommate is selected from the list"""
        self.name_var.set(name.split(":")[0]) 

    def update_list(self):
        """Updates the display of the roommate list."""
        self.roommate_list.delete(0, "end")
        for roommate in self.roommates:
            self.roommate_list.insert("end", f"{roommate.name}: €{roommate.payments:.2f}")

    def add_roommate(self):
        name = self.name_var.get().strip()
        if name:
            new_roommate = Roommate(name)
            self.roommates.append(new_roommate)
            self.update_list()
            self.name_var.set("")
        else:
            messagebox.showwarning("Error", "Please enter a valid name")

    def record_payment(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Error", "Please enter the roommate's name")
            return

        try:
            amount = float(self.amount_var.get())
            for roommate in self.roommates:
                if roommate.name == name:
                    roommate.add_payment(amount)
                    # Save the payment to history
                    self.add_to_history(name, amount)
                    self.update_list()
                    self.amount_var.set("")
                    self.amount_entry.focus()
                    return
            messagebox.showwarning("Error", "Roommate not found")
        except ValueError:
            messagebox.showwarning("Error", "Please enter a valid amount")

    def remove_roommate(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Error", "Please enter the name of the roommate to remove")
            return

        for i, roommate in enumerate(self.roommates):
            if roommate.name == name:
                del self.roommates[i]
                self.update_list()
                self.name_var.set("")
                return

        messagebox.showwarning("Error", "Roommate not found")

    def show_balance(self):
        if len(self.roommates) < 2:
            messagebox.showwarning("Error", "At least two roommates are required")
            return

        total_expenses = sum(r.payments for r in self.roommates)
        balance = calculate_differences(self.roommates, total_expenses)

        creditors = [(name, balance) for name, balance in balance.items() if balance > 0]
        debtors = [(name, balance) for name, balance in balance.items() if balance < 0]

        result = "Detailed Balance:\n\n"

        for debtor, debt in debtors:
            remaining_debt = abs(debt)
            for creditor, credit in creditors:
                if credit > 0 and remaining_debt > 0:
                    payment = min(credit, remaining_debt)
                    result += f"{debtor} owes €{payment:.2f} to {creditor}\n"
                    remaining_debt -= payment

        result += "\nGeneral Summary:\n"
        for name, balance in balance.items():
            if balance > 0:
                result += f"{name} should receive €{balance:.2f}\n"
            elif balance < 0:
                result += f"{name} should pay €{abs(balance):.2f}\n"
            else:
                result += f"{name} is even\n"

        messagebox.showinfo("Result", result)

    def load_history(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    print(f"Loaded data: {data}")  # Debug
                    return data
            print("History file not found")  # Debug
            return []
        except Exception as e:
            print(f"Error loading history: {e}")  # Debug
            return []

    def add_to_history(self, name, amount):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_payment = {
            "date": date,
            "name": name,
            "amount": amount
        }
        self.expense_history.append(new_payment)
        with open(self.data_file, 'w') as f:
            json.dump(self.expense_history, f)

    def show_charts(self):
        # Clear the history tab
        for widget in self.tab_history.winfo_children():
            widget.destroy()

        if not self.expense_history:
            messagebox.showinfo("Info", "No historical data available")
            return

        try:
            # Convert data to DataFrame
            df = pd.DataFrame(self.expense_history)
            
            # Sort data by date in descending order and take the last 5 for the table
            df_table = df.sort_values(by='date', ascending=False).head(5)  # Modify here

            # Check loaded data
            print("Loaded data:", df)  # Debug
            
            # Convert the date column
            df['date'] = pd.to_datetime(df['date'], errors='coerce')  # Use errors='coerce' to handle potential errors
            
            # Check for invalid dates
            if df['date'].isnull().any():
                print("Warning: there are invalid dates in the DataFrame.")
                print("Invalid dates:", df[df['date'].isnull()])  # Show invalid dates
                return
            
            # Create a frame to contain everything
            main_frame = ctk.CTkFrame(self.tab_history)
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Frame for the table
            table_frame = ctk.CTkFrame(main_frame)
            table_frame.pack(fill="x", padx=20, pady=(0, 10))  # Reduced bottom padding
            
            # Create table with the last 5 items
            headers = ["Date", "Name", "Amount"]
            rows = [[p["date"], p["name"], f"€{p['amount']:.2f}"] for p in df_table.to_dict(orient='records')]  # Modify here
            
            table = CTkTable(
                table_frame,
                values=[headers] + rows,
                header_color=ocra,
                hover_color=ocra_hover
            )
            table.pack(fill="x", padx=20, pady=10)
            
            # Charts with all historical data
            # Frame for the charts
            frame_charts = ctk.CTkFrame(main_frame)
            frame_charts.pack(fill="both", expand=True, padx=20, pady=(30, 0))  # Increased top padding
            
            # Create the figure with the charts
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))  # Increased for better visibility
            fig.patch.set_facecolor('#2b2b2b')
            
            # Expense chart per person
            expenses_per_person = df.groupby('name')['amount'].sum()  # Use complete df
            ax1.bar(expenses_per_person.index, expenses_per_person.values, color=ocra)
            ax1.set_title('Total Expenses per Person', color='white')
            ax1.set_facecolor('#2b2b2b')
            ax1.tick_params(colors='white')
            
            # Time trend chart
            for name in df['name'].unique():  # Use complete df
                person_data = df[df['name'] == name]
                person_data = person_data.sort_values('date')
                ax2.plot(person_data['date'], person_data['amount'].cumsum(), 
                         label=name, linewidth=2, marker='o')  # Added marker for points
            ax2.set_title('Expense Trend Over Time', color='white', pad=20)
            ax2.set_facecolor('#2b2b2b')
            ax2.tick_params(colors='white', rotation=45)
            ax2.set_xlabel('Date', color='white')  # X-axis label
            ax2.set_ylabel('Cumulative Amount (€)', color='white')  # Y-axis label
            
            # Add grid
            ax2.grid(True, color='gray', alpha=0.3)
            ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # Format the x-axis to show months in Italian
            try:
                locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
            except locale.Error:
                italian_months = {
                    1: 'January', 2: 'February', 3: 'March', 4: 'April',
                    5: 'May', 6: 'June', 7: 'July', 8: 'August',
                    9: 'September', 10: 'October', 11: 'November', 12: 'December'
                }
                def format_date(x, p):
                    date = matplotlib.dates.num2date(x)
                    return f"{italian_months[date.month]} {date.year}"
                ax2.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(format_date))
            else:
                ax2.xaxis.set_major_locator(MonthLocator())
                ax2.xaxis.set_major_formatter(DateFormatter('%B %Y'))
            
            plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
            plt.tight_layout()

            # Create the canvas in a separate frame
            canvas_frame = ctk.CTkFrame(frame_charts)
            canvas_frame.pack(fill="both", expand=True)
            
            canvas = FigureCanvasTkAgg(fig, canvas_frame)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill="both", expand=True)
            
            # Force the canvas to update
            canvas.draw()
            
            # Explicitly handle events
            self.root.update_idletasks()

        except Exception as e:
            messagebox.showerror("Error", f"Error displaying charts: {str(e)}")
            print(f"Detailed error: {str(e)}")  # For debug

    def predict_expenses(self):
        # Prepare data for regression
        df = pd.DataFrame(self.expense_history)
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M')  # Extract month (YYYY-MM)
        
        # Group by month and name, sum amounts
        monthly_expenses = df.groupby(['month', 'name'])['amount'].sum().reset_index()

        # Linear regression model for each roommate
        predictions = {}
        fig, ax = plt.subplots(figsize=(8, 5))
        
        for name in monthly_expenses['name'].unique():
            roommate_data = monthly_expenses[monthly_expenses['name'] == name].copy()
            roommate_data['month_ordinal'] = roommate_data['month'].dt.to_timestamp().map(datetime.toordinal)

            # Check if there is enough data
            if len(roommate_data) < 2:
                continue  # At least one pair of points is needed for regression

            # Linear regression model
            X = roommate_data['month_ordinal'].values.reshape(-1, 1)
            y = roommate_data['amount'].values

            model = LinearRegression()
            model.fit(X, y)

            # Predict expenses for the next 6 months
            future_months = [roommate_data['month'].max().to_timestamp() + pd.DateOffset(months=i) for i in range(1, 7)]
            future_ordinal = np.array([date.toordinal() for date in future_months]).reshape(-1, 1)
            future_expenses = model.predict(future_ordinal)

            # Save predictions
            predictions[name] = future_expenses.sum()

            # Plot historical data
            ax.scatter(roommate_data['month'].dt.to_timestamp(), y, label=f'Data {name}', alpha=0.7)
            
            # Plot regression line on past data
            line_x = np.linspace(X.min(), future_ordinal.max(), 100)
            line_y = model.predict(line_x.reshape(-1, 1))
            ax.plot([datetime.fromordinal(int(x)) for x in line_x], line_y, linestyle="--", label=f'Prediction {name}')

        ax.set_title("Expense Prediction")
        ax.set_xlabel("Months")
        ax.set_ylabel("Expenses (€)")
        ax.legend()
        ax.grid(True)

        # Show the chart
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Insert the chart into the UI
        canvas = FigureCanvasTkAgg(fig, self.predictions_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

        # Show the result in text
        result = "\n".join([f"{name}: €{expense:.2f}" for name, expense in predictions.items()])
        self.prediction_label.configure(text=f"Predicted expenses for the next 6 months:\n{result}")

    def display_predictions(self, monthly_expenses, future_months, predictions):
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Set the background color of the figure
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#2b2b2b')
        
        # Check for historical data
        for name in monthly_expenses['name'].unique():
            roommate_data = monthly_expenses[monthly_expenses['name'] == name]
            ax.plot(roommate_data['month'].dt.to_timestamp(), roommate_data['amount'], 
                    label=f'Historical Expenses {name}', linewidth=2, color='cyan', marker='o')

        # Show predictions for each roommate
        for name in predictions.keys():
            last_month = monthly_expenses[monthly_expenses['name'] == name]['month'].max()
            future_dates = [last_month.to_timestamp() + pd.DateOffset(months=i) for i in range(1, 7)]
            future_expenses = [predictions[name]] * len(future_dates)  # Ensure future_expenses is a list

            # Plot the prediction line
            ax.plot(future_dates, future_expenses, label=f'Predictions {name}', linestyle='--', linewidth=2, color='magenta', marker='x')

            # Add annotations for the predictions
            for i, expense in enumerate(future_expenses):
                ax.annotate(f'€{expense:.2f}', (future_dates[i], expense), textcoords="offset points", xytext=(0,10), ha='center', color='white')

        # Configure title, subtitle, labels, and legend
        ax.set_title('Future Expense Predictions', color='white', fontsize=16)
        ax.set_xlabel('Month', color='white', fontsize=14)
        ax.set_ylabel('Expenses (€)', color='white', fontsize=14)
        ax.legend(loc='best', fontsize=10, facecolor='white')
        
        # Add grid
        ax.grid(True, color='gray', linestyle='--', alpha=0.5)

        # Color the axes and ticks
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        plt.xticks(rotation=45)

        # Configure layout and display the chart
        plt.tight_layout()

        # Create the canvas in a separate frame
        canvas_frame = ctk.CTkFrame(self.predictions_frame)
        canvas_frame.pack(fill="both", expand=True)
        
        canvas = FigureCanvasTkAgg(fig, canvas_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True)
        
        # Force the canvas to update
        canvas.draw()

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    
    ocra = "#DAA520"  
    ocra_hover = "#B8860B"  
    
    ctk.set_default_color_theme("blue")  
    style = {
        "CTkButton": {
            "fg_color": ocra,
            "hover_color": ocra_hover,
            "border_color": ocra
        }
    }
    
    for widget, config in style.items():
        ctk.ThemeManager.theme[widget].update(config)

    try:
        root = ctk.CTk()
        app = ExpenseManagementApp(root)
        root.mainloop()
    except Exception as e:
        print(f"An error occurred: {e}")
