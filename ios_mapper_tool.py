"""
Script: IOS Mapper Tool
Description: Tool for analyzing iOS com.apple.routined caches.sqlite databases,
using a modern GUI built with CustomTkinter. Allows for fast display, filtering, and mapping of location data.

Author: Class Euclid
Date: 07/16/25
Version: 2.3.0

Dependencies:
- Pandas
- Folium
- CustomTkinter

Version History:
- 2.3.0 - 07/16/25: Added filtering by date typed by user, fixed issues with GUI
- 2.2.0 - 07/12/25: Map HTML automatically saved alongside Excel output.

References:
- Pandas: https://pandas.pydata.org/
- Folium: https://python-visualization.github.io/folium/latest/
- CustomTkinter: https://github.com/TomSchimansky/CustomTkinter
"""

import pandas as pd
from datetime import datetime, timedelta
import folium
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os

# Function to convert Apple timestamp to human readable datetime
def apple_time_to_datetime(apple_time):
    apple_base_date = datetime(2001, 1, 1)
    return apple_base_date + timedelta(seconds=apple_time)

# Function to convert ZSPEED from meters per second to MPH
def convert_zspeed(zspeed):
    try:
        zspeed = float(zspeed)
        return f"{zspeed * 2.237:.2f} MPH" if zspeed > 0 else "0 MPH"
    except (ValueError, TypeError):
        return "0 MPH"

# Main app class
class ForensicsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("iOS Mapper Tool")
        self.geometry("600x350")

        # Input file
        self.input_label = ctk.CTkLabel(self, text="Select Input Excel or CSV File:")
        self.input_label.pack(pady=(20, 5))

        self.input_entry = ctk.CTkEntry(self, width=400)
        self.input_entry.pack(pady=5)

        self.input_button = ctk.CTkButton(self, text="Browse", command=self.browse_input_file)
        self.input_button.pack(pady=5)

        # Output file
        self.output_label = ctk.CTkLabel(self, text="Select Output File name and location:")
        self.output_label.pack(pady=(20, 5))

        self.output_entry = ctk.CTkEntry(self, width=400)
        self.output_entry.pack(pady=5)

        self.output_button = ctk.CTkButton(self, text="Browse", command=self.browse_output_file)
        self.output_button.pack(pady=5)

        # Timestamp filter
        self.format_label = ctk.CTkLabel(
            self,
            text="Enter Date to Filter (MM/DD/YYYY) or leave blank for all data:"
        )
        self.format_label.pack(pady=(20, 5))

        self.format_entry = ctk.CTkEntry(self, width=400)
        self.format_entry.insert(0, "")  # default blank
        self.format_entry.pack(pady=5)

        # Run button
        self.run_button = ctk.CTkButton(self, text="Run Analysis", command=self.run_analysis)
        self.run_button.pack(pady=(30, 10))

    def browse_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Input File",
            filetypes=[
                ("Excel Files", "*.xlsx"),
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.input_entry.delete(0, ctk.END)
            self.input_entry.insert(0, file_path)

    def browse_output_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Save Formatted File As",
            defaultextension=".xlsx",
            filetypes=[
                ("Excel Files", "*.xlsx"),
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            output_dir = os.path.dirname(file_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            self.output_entry.delete(0, ctk.END)
            self.output_entry.insert(0, file_path)

    def run_analysis(self):
        input_file = self.input_entry.get()
        output_file = self.output_entry.get()
        filter_string = self.format_entry.get().strip()

        if not input_file or not output_file:
            messagebox.showerror("Error", "Please complete all required fields.")
            return

        try:
            # Load data
            try:
                if input_file.lower().endswith('.csv'):
                    df = pd.read_csv(input_file)
                else:
                    df = pd.read_excel(input_file, engine="openpyxl")
            except Exception:
                # fallback for Excel file that's secretly CSV
                df = pd.read_csv(input_file)

            # Convert timestamps to full datetime string
            df['Full_ZTIMESTAMP'] = df['ZTIMESTAMP'].apply(
                lambda x: apple_time_to_datetime(x).strftime("%Y-%m-%d %H:%M:%S")
            )
            # Extract date only (yyyy-mm-dd)
            df['DATE_ONLY'] = df['Full_ZTIMESTAMP'].str.slice(0, 10)

            # Check whether to filter
            filter_date = None
            if filter_string:
                try:
                    # Convert user date from MM/DD/YYYY → YYYY-MM-DD
                    parsed_date = datetime.strptime(filter_string, "%m/%d/%Y")
                    filter_date = parsed_date.strftime("%Y-%m-%d")
                except ValueError:
                    messagebox.showerror(
                        "Error",
                        f"Invalid date format. Please enter as MM/DD/YYYY."
                    )
                    return

            # Filter data if a date was provided
            if filter_date:
                df_filtered = df[df['DATE_ONLY'] == filter_date].copy()
            else:
                df_filtered = df.copy()

            if df_filtered.empty:
                messagebox.showinfo("No Data", "No data found for the specified date.")
                return

            # Convert speed
            df_filtered['SPEED'] = df_filtered['ZSPEED'].apply(convert_zspeed)

            # Sort
            df_sorted = df_filtered.sort_values(by='Full_ZTIMESTAMP')

            # Save file
            if output_file.lower().endswith('.csv'):
                df_sorted.to_csv(output_file, index=False)
            else:
                df_sorted.to_excel(output_file, index=False, engine="openpyxl")

            messagebox.showinfo("Success", f"Data saved to {output_file}")

            # Generate Folium map only if there are coordinates
            if 'ZLATITUDE' in df_sorted.columns and 'ZLONGITUDE' in df_sorted.columns:
                map_center = [
                    df_sorted['ZLATITUDE'].mean(),
                    df_sorted['ZLONGITUDE'].mean()
                ]

                folium_map = folium.Map(location=map_center, zoom_start=12)

                for _, row in df_sorted.iterrows():
                    popup_text = (
                        f"<strong>Z_PK:</strong> {row['Z_PK']}<br>"
                        f"<strong>SPEED:</strong> {row['SPEED']}<br>"
                        f"<strong>Timestamp:</strong> {row['Full_ZTIMESTAMP']}"
                    )

                    folium.CircleMarker(
                        location=(row['ZLATITUDE'], row['ZLONGITUDE']),
                        radius=2,
                        color='red',
                        fill=True,
                        fill_color='red',
                        fill_opacity=0.6,
                        popup=folium.Popup(popup_text, max_width=300)
                    ).add_to(folium_map)

                output_dir = os.path.dirname(output_file)
                map_file = os.path.join(output_dir, "location_data_map.html")

                folium_map.save(map_file)
                messagebox.showinfo("Success", f"Map saved to {map_file}")
            else:
                messagebox.showinfo(
                    "Note",
                    "Columns ZLATITUDE and ZLONGITUDE not found. Map not generated."
                )

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")

if __name__ == "__main__":
    ctk.set_appearance_mode("System")   
    ctk.set_default_color_theme("blue")
    app = ForensicsApp()
    app.mainloop()
