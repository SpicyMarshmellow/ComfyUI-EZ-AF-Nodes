import re

class EZ_Extract_Prompt:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "searchword": ("STRING", {"multiline": False, "default": ""}),
                "extract_all": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "extract_prompt"
    CATEGORY = "EZ NODES"
    DESCRIPTION = """
Extracts full lines of text from input text based on the header provided in input

If "extract_all" is set ot true, node will return the original text with all headers removed

Use with EZ_CSV_Loader to extract text content based on header name
"""

    def extract_prompt(self, string, searchword, extract_all):
        if extract_all:
            result = []
            for line in string.splitlines():
                stripped = line.strip()
                if not stripped:
                    continue  # Skip empty lines
                if stripped.endswith(":") and len(stripped.split()) == 1:
                    continue  # Skip headers
                result.append(line)
            return ("\n".join(result),)

        searchword = searchword.lower()
        collect = False
        lines_out = []

        for line in string.splitlines():
            if not collect:
                # Detect header line
                header = line.strip()
                if header.lower().rstrip(':') == searchword:
                    collect = True
                continue

            # Stop on first empty line
            if line.strip() == "":
                break
            lines_out.append(line)

        return ("\n".join(lines_out),)
        
class EZ_Find_Replace:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
            },
            "optional": {
                "find": ("STRING", {"multiline": False, "default": ""}),
                "replace": ("STRING", {"multiline": False, "default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "find_replace"
    CATEGORY = "EZ NODES"
    DESCRIPTION = """
Finds and replaces all instances of text string
"""

    def find_replace(self, string, find, replace):
        string = string.replace(find, replace)
        return (string,)

class EZ_Text_to_Size:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_input": ("STRING", {"default": "1024x1024"}),
            },
        }

    RETURN_TYPES = ("INT", "INT",)
    RETURN_NAMES = ("WIDTH", "HEIGHT",)
    FUNCTION = "extract_size"
    CATEGORY = "EZ NODES"
    DESCRIPTION = """
Extract the last 2 numbers found within a text string to be used as width and height
"""

    def extract_size(self, text_input):
        try:
            # Handle None or empty input
            if text_input is None or text_input == "":
                print("EZ_Text_to_Size: No input provided, using default 1024x1024")
                return (1024, 1024,)
            
            # Convert to string to ensure we're working with a string
            text_input = str(text_input)
            
            # Extract all numbers from the text using regex
            numbers = re.findall(r'\d+', text_input)
            
            # Check if we have at least 2 numbers
            if len(numbers) < 2:
                print(f"EZ_Text_to_Size: Need at least 2 numbers, found {len(numbers)} in '{text_input}'. Using default 1024x1024")
                return (1024, 1024,)
            
            # Return last two numbers as width and height
            width = int(numbers[-2])
            height = int(numbers[-1])
            
            print(f"EZ_Text_to_Size: Extracted {width}x{height} from '{text_input}'")
            return (width, height,)
            
        except Exception as e:
            print(f"EZ_Text_to_Size: Error processing input '{text_input}': {str(e)}. Using default 1024x1024")
            return (1024, 1024,)