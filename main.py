"""
Script: IOS Mapper Tool
Description: Digital Forensics tool for analyzing iOS com.apple.routined caches.sqlite databases,
using a modern GUI built with CustomTkinter. Allows for a quicker display for presentation or court purposes, or faster filter. 

Author: Class Euclid
Date: 07/12/25
Version: 2.2.0

Dependencies:
- Pandas
- Folium
- CustomTkinter

Version History:
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

# Function to convert Apple timestamp to human-readable datetime
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

        # Input file Currently supports the com.apple.routined caches db from the zrtclocationmo table
        self.input_label = ctk.CTkLabel(self, text="Select Input Excel File:")
        self.input_label.pack(pady=(20, 5))

        self.input_entry = ctk.CTkEntry(self, width=400)
        self.input_entry.pack(pady=5)

        self.input_button = ctk.CTkButton(self, text="Browse", command=self.browse_input_file)
        self.input_button.pack(pady=5)

        # Output file
        self.output_label = ctk.CTkLabel(self, text="Select Output Excel File:")
        self.output_label.pack(pady=(20, 5))

        self.output_entry = ctk.CTkEntry(self, width=400)
        self.output_entry.pack(pady=5)

        self.output_button = ctk.CTkButton(self, text="Browse", command=self.browse_output_file)
        self.output_button.pack(pady=5)

        # Timestamp format to remove clutter for user
        self.format_label = ctk.CTkLabel(self, text="Enter Timestamp Format:")
        self.format_label.pack(pady=(20, 5))

        self.format_entry = ctk.CTkEntry(self, width=400)
        self.format_entry.insert(0, "%m/%d/%Y %H:%M:%S")  # default format
        self.format_entry.pack(pady=5)

        # Run button
        self.run_button = ctk.CTkButton(self, text="Run Analysis", command=self.run_analysis)
        self.run_button.pack(pady=(30, 10))

    def browse_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Input Excel File",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if file_path:
            self.input_entry.delete(0, ctk.END)
            self.input_entry.insert(0, file_path)

    def browse_output_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Save Formatted Excel As",
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if file_path:
            self.output_entry.delete(0, ctk.END)
            self.output_entry.insert(0, file_path)

    def run_analysis(self):
        input_file = self.input_entry.get()
        output_file = self.output_entry.get()
        time_format = self.format_entry.get()

        if not input_file or not output_file or not time_format:
            messagebox.showerror("Error", "Please complete all required fields.")
            return

        try:
            # Load data
            df = pd.read_excel(input_file)

            # Convert timestamps
            df['Converted_ZTIMESTAMP'] = df['ZTIMESTAMP'].apply(
                lambda x: apple_time_to_datetime(x).strftime(time_format)
            )

            # Convert speed
            df['SPEED'] = df['ZSPEED'].apply(convert_zspeed)

            # Sort data
            df_sorted = df.sort_values(by='Converted_ZTIMESTAMP')

            # Save Excel
            df_sorted.to_excel(output_file, index=False)
            messagebox.showinfo("Success", f"Data saved to {output_file}")

            # Derive map file path from output Excel location
            output_dir = os.path.dirname(output_file)
            map_file = os.path.join(output_dir, "location_data_map.html")

            # Generate Folium map
            map_center = [
                df_sorted['ZATITUDE'].mean(),
                df_sorted['ZLONGITUDE'].mean()
            ]

            folium_map = folium.Map(location=map_center, zoom_start=12)

            for _, row in df_sorted.iterrows():
                popup_text = (
                    f"<strong>Z_PK:</strong> {row['Z_PK']}<br>"
                    f"<strong>SPEED:</strong> {row['SPEED']}<br>"
                    f"<strong>Timestamp:</strong> {row['Converted_ZTIMESTAMP']}"
                )

                folium.CircleMarker(
                    location=(row['ZATITUDE'], row['ZLONGITUDE']),
                    radius=2,
                    color='red',
                    fill=True,
                    fill_color='red',
                    fill_opacity=0.6,
                    popup=folium.Popup(popup_text, max_width=300)
                ).add_to(folium_map)

            folium_map.save(map_file)
            messagebox.showinfo("Success", f"Map saved to {map_file}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")


if __name__ == "__main__":
    ctk.set_appearance_mode("System")   # Options: "System", "Dark", "Light"
    ctk.set_default_color_theme("blue")
    app = ForensicsApp()
    app.mainloop()