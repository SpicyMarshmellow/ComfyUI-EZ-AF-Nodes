import re

def clean_text(text):
    text = re.sub(r'\n','####', text) # Replace line breaks to keep it for future (line breaks should not be deleted by default
    text = re.sub(r'\s+,', ',', text) # Remove spaces before commas
    text = re.sub(r',+', ',', text) # Remove duplicate commas
    text = re.sub(r',(\S)', r', \1', text) # Add a space after a comma if it's followed by a word without space
    text = re.sub(r'[ \t]+', ' ', text) # Replace multiple spaces with a single space, while keeping newlines
    text = re.sub(r'\.,|,\.', '.', text) # Replace incorrect combinations like '.,' and ',.' with '.'
    text = re.sub(r"####",'\n', text) # Return line breaks
    text = re.sub(r'(\n\s*){3,}', '\n\n', text) # Consolidate three or more consecutive newlines into two
    text = text.strip().replace(" .", ".") # Remove spaces before periods
    text = re.sub(r',(\S)', r' ', text) # Add a space after a comma if it's followed by a word without space
    cleaned_lines = [line.lstrip("., ") for line in text.splitlines()] # Delete excess commas
    text = "\n".join(cleaned_lines)
    return text

class EZ_Text_Concat: # inspired by WAS-Suite by Jordan Thompson (WASasquatch) and Bjornulf nodes
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "number_of_inputs": ("INT", {"default": 2, "min": 2, "max": 50, "step": 1}),
                "delimiter": ("STRING", {"default": "\\n"}),
                "beautify": (["never", "before", "after"], {"default": "never"}),
                "line_breaks": (["keep", "delete"], {"default": "keep"}),
            },
            "hidden": {
                **{f"text_{i}": ("STRING", {"forceInput": "True"}) for i in range(1, 51)}
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "text_concatenate"
    CATEGORY = "EZ NODES"
    DESCRIPTION = """
Concatenate any number of string inputs into a single string with options to beatify text before or after concatenation

use single or multiple "\\n" inputs as delimiter to add line breaks
"""

    def text_concatenate(self, delimiter, beautify, line_breaks, number_of_inputs, **kwargs):
        text_inputs = [] 
        delimiter=delimiter.replace("\\n","\n")
        for k in sorted(kwargs.keys()):
            v = kwargs[k]
            if isinstance(v, str):
                if beautify == "before":
                        v=clean_text(v)
                if v != "":
                    text_inputs.append(v)
        merged_text = delimiter.join(text_inputs)
        print(merged_text)
        if beautify == "after":
            merged_text = clean_text(merged_text)
        if line_breaks == "delete":
            merged_text = re.sub(r'\n',' ', merged_text)
            merged_text = re.sub(r'\s+', ' ', merged_text)
        return (merged_text,)