from server import PromptServer  # type: ignore // ComfyUI Core
import os
import random
from aiohttp import web
import json
import csv

root_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.abspath(os.path.join(root_dir, "../csv"))

class EZ_CSV_Loader:
    @classmethod
    def INPUT_TYPES(cls):
        global csv_path
        try:
            csv_files = []
            for root, dirs, files in os.walk(csv_path):
                for f in files:
                    if f.lower().endswith('.csv'):
                        full_path = os.path.join(root, f)
                        rel_path = os.path.relpath(full_path, csv_path)
                        csv_files.append(rel_path)
        except Exception as e:
            csv_files = []

        return {
            "required": {
                "csv_file": (csv_files,),
                "selection_mode": (["single", "multiple", "random"], {"default": "single"}),
            },
            "optional": {
                "filter_text": ("STRING", {"default": ""}),
                "selected_row": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("STRING", "OPT_FILEPATH", "BATCH_SELECTED")
    OUTPUT_IS_LIST = (False, False, True)

    FUNCTION = "browse_csv"

    CATEGORY = "EZ NODES"
    DESCRIPTION = """
Loads rows from a CSV file based on UI selection
Each row in the CSV is selectable; the first row is used as headers
Selection types:
- single: Select one row at a time
- multiple: Select multiple rows (comma-separated indices)
- random: Randomly select one row on each prompt queue
"""

    def browse_csv(self, csv_file, selection_mode="single", selected_row="", filter_text=""):
        global csv_path
        csv_file = os.path.join(csv_path, csv_file)
        csv_file = os.path.abspath(csv_file)

        if not os.path.isfile(csv_file):
            return ("No CSV file found", csv_file, [])

        # Read CSV
        with open(csv_file, "r", encoding="utf-8") as f:
            first_line = f.readline()
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(first_line, delimiters=",;")
            except Exception:
                dialect = csv.excel
            reader = list(csv.reader(f, dialect))
            if not reader or len(reader) < 2:
                return ("No data rows found in file", csv_file, [])
            headers = reader[0]
            rows = reader[1:]
            
            # Filter out empty rows (rows where all cells are empty or whitespace)
            rows = [row for row in rows if any(cell.strip() for cell in row)]

        # Filter rows if filter_text is provided (search in any cell)
        if filter_text:
            rows = [row for row in rows if any(filter_text.lower() in str(cell).lower() for cell in row)]

        if not rows:
            return ("No matching rows found", csv_file, [])

        # Handle selection
        selected_indices = []
        if selection_mode == "random":
            selected_indices = [random.randint(0, len(rows)-1)]
        elif selection_mode == "multiple":
            if selected_row:
                try:
                    selected_indices = [int(idx) for idx in selected_row.split(",") if idx.strip().isdigit() and int(idx) < len(rows)]
                except Exception:
                    selected_indices = []
        else:  # single
            if not selected_row or not selected_row.isdigit() or int(selected_row) >= len(rows):
                selected_indices = [0]
            else:
                selected_indices = [int(selected_row)]

        # Format output for main output
        outputs = []
        for idx in selected_indices:
            row = rows[idx]
            out = ""
            for h, v in zip(headers, row):
                out += f"{h}:\n{v}\n\n"
            outputs.append(out.strip())
        output_str = "\n---\n".join(outputs)

        # Format output for ALL_SELECTED_ROWS (list)
        if len(selected_indices) <= 1:
            all_indices = list(range(len(rows)))
        else:
            all_indices = selected_indices
        all_outputs = []
        for idx in all_indices:
            row = rows[idx]
            out = ""
            for h, v in zip(headers, row):
                out += f"{h}:\n{v}\n\n"
            all_outputs.append(out.strip())

        return (output_str, csv_file, all_outputs)

    @classmethod
    def IS_CHANGED(cls, csv_file, selection_mode, selected_row="", filter_text=""):
        if selection_mode == "random":
            return float('nan')
        return selected_row + str(csv_file) + str(selection_mode)

    @classmethod
    def VALIDATE_INPUTS(cls, csv_file, selected_row="", selection_mode="single"):
        global csv_path
        csv_file = os.path.join(csv_path, csv_file)
        csv_file = os.path.abspath(csv_file)
        if not os.path.isfile(csv_file):
            return "CSV file does not exist"
        return True

def get_directory_structure(path):
    structure = {"name": os.path.basename(path), "children": [], "path": path, "expanded": False}
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_dir():
                    structure["children"].append(get_directory_structure(entry.path))
    except PermissionError:
        pass
    return structure

def get_rows_from_csv(file_path, filter_text=""):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            first_line = f.readline()
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(first_line, delimiters=",;")
            except Exception:
                dialect = csv.excel
            reader = list(csv.reader(f, dialect))
            if not reader or len(reader) < 2:
                return {"headers": [], "rows": []}
            headers = reader[0]
            rows = reader[1:]
            
            # Filter out empty rows (rows where all cells are empty or whitespace)
            rows = [row for row in rows if any(cell.strip() for cell in row)]
            
            if filter_text:
                rows = [row for row in rows if any(filter_text.lower() in str(cell).lower() for cell in row)]
            return {"headers": headers, "rows": rows}
    except Exception as e:
        print(f"Error reading CSV file {file_path}: {e}")
        return {"headers": [], "rows": []}

@PromptServer.instance.routes.post("/ez_csv_browser/get_directory_structure")
async def api_get_directory_structure(request):
    try:
        data = await request.json()
        path = data.get("path", "./")
        filter_text = data.get("filter", "")

        if not os.path.isabs(path):
            path = os.path.abspath(path)

        if not os.path.exists(path):
            return web.json_response({"error": "Path does not exist"}, status=400)

        # If path is a file, get its directory
        if os.path.isfile(path):
            directory = os.path.dirname(path)
            structure = get_directory_structure(directory)
            csv_data = get_rows_from_csv(path, filter_text)
        else:
            structure = get_directory_structure(path)
            csv_data = {"headers": [], "rows": []}

        response_data = {
            "structure": structure,
            "headers": csv_data["headers"],
            "rows": csv_data["rows"]
        }
        return web.json_response(response_data)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

@PromptServer.instance.routes.post("/ez_csv_browser/get_file_info")
async def get_file_info(request):
    try:
        data = await request.json()
        rel_path = data.get("relative_path", "")
        full_path = os.path.normpath(os.path.join(csv_path, rel_path))
        if not full_path.startswith(csv_path):
            return web.json_response({"error": "Invalid path"}, status=400)
        if not os.path.exists(full_path):
            return web.json_response({"error": "File not found"}, status=404)
        return web.json_response({
            "full_path": full_path,
        })
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)