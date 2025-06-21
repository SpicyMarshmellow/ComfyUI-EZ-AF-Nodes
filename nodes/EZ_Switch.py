import random

class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

any = AnyType("*")

class EZ_Switch: # logic for dynamic inputs stolen from Bjornulf nodes. Inspired by Impact-Pack
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "number_of_inputs": ("INT", {"default": 2, "min": 2, "max": 50, "step": 1}),
                "selected_index": ("INT", {"default": 1, "min": 1, "max": 50, "step": 1}),
                "selection_mode": (["by index", "by random", "automatic"], {"default": "by index"}),
            },
            "hidden": {
                **{f"input_{i}": ("*", {"forceInput": "True"}) for i in range(1, 51)}
            },
        }

    RETURN_TYPES = (any,)
    FUNCTION = "switch"
    CATEGORY = "EZ NODES"
    DESCRIPTION = """
Switch between multiple inputs based on selection mode.

- "by index": Select input by specified index
- "by random": Choose a random input each time
- "automatic": Output the first input that is not None
Returns the selected input unchanged.
"""

    def switch(self, number_of_inputs, selection_mode, selected_index=None, **kwargs):
        if selection_mode == "by index":
            # For non-random selection, only read the specific input needed (original logic)
            if selected_index is None:
                return (None,)
            target_input_key = f"input_{selected_index}"
            if target_input_key in kwargs:
                return (kwargs[target_input_key],)
            else:
                return (None,)
        
        elif selection_mode == "by random":
            # If random_selection is enabled, we need to read all inputs for random selection
            inputs = [] 
            for k in sorted(kwargs.keys()):
                v = kwargs[k]
                if v is not None:  # Accept any non-None input, not just strings
                    inputs.append(v)
            
            if len(inputs) > 0:
                selected_index = random.randint(1, len(inputs))
                return (inputs[selected_index - 1],)
            else:
                return (None,)
        
        elif selection_mode == "automatic":
            # Return the first non-None input
            for k in sorted(kwargs.keys()):
                v = kwargs[k]
                if v is not None:  # Accept any non-None input, not just strings
                    return (v,)
            return (None,)
        
        else:
            return (None,)
    
    @classmethod
    def IS_CHANGED(cls, selection_mode, **kwargs):
        # Always re-execute if random selection is enabled
        if selection_mode == "by random":
            return None
        return False