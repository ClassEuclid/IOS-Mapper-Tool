# iOS Mapper Tool

The iOS Mapper Tool is designed to help forensic professionals visually analyze data from the iOS `com.apple.routined` caches database, specifically focusing on the `ZRTCLLOCATIONMO` table.

This tool can be especially valuable in criminal or civil cases, helping investigators, attorneys, and analysts:

- Visually depict location data on an interactive map
- Present clear evidence to judges, jurors, or clients
- Generate a formatted Excel spreadsheet with readable timestamps and speeds

---

## Features

User-friendly interface  
Converts iOS Apple Absolute Time to readable timestamps  
Converts speeds from meters per second to miles per hour (MPH)  
Sorts data for easy review  
Generates an interactive HTML map  
Saves output files for case documentation  
Available as:
- A Python script
- A compiled Windows executable (.exe)

---

## Example Outputs

### Interactive Map

![HTML Map Screenshot](ExampleImages/HTMLVisual.png)

### Formatted Excel Spreadsheet

![Formatted Spreadsheet Screenshot](ExampleImages/updatedspreadsheet.png)

---

## Use Case

This tool is designed for digital forensic investigators, law enforcement, and legal professionals who need to transform raw iOS location artifacts into clear, understandable visualizations and reports.

It’s especially useful when presenting evidence in court, where clear visuals help explain complex technical data to non-technical audiences.

---

## Forensic Disclaimer

> **IMPORTANT:**  
> Always independently validate and verify your findings.  
> Data artifacts can vary depending on iOS versions, acquisition methods, and software updates.  
> This tool is provided as-is, without warranty, for forensic and educational purposes.

---

## Installation

First, clone or download this repository.

### Install Python Dependencies

If running the Python script:

pip install -r requirements.txt

