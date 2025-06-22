class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

any = AnyType("*")

class EZ_Input:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "String": ("STRING", {"multiline": True}),
            }
        }

    RETURN_TYPES = (any, )
    RETURN_NAMES = ("STRING", )
    
    OUTPUT_TOOLTIPS = ("Multiline string that may be input in 'combo' input slot.",)

    FUNCTION = "doit"

    CATEGORY = "EZ NODES"
    DESCRIPTION = """
This node outputs multiline string but assigns "ANY" type to it.
Created for my personal convenience and for testing purposes.
If you don't need "ANY" type output, consider using Comfy Core — "String (Multiline)" instead.
"""

    def doit(self, String):
        
        Combo = String
        return (Combo, )