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
                "random_selection": ("BOOLEAN", {"default": False}),
            },
            "hidden": {
                **{f"input_{i}": ("*", {"forceInput": "True"}) for i in range(1, 51)}
            },
        }

    RETURN_TYPES = (any,)
    FUNCTION = "switch"
    CATEGORY = "EZ NODES"
    DESCRIPTION = """
Switch between multiple inputs based on selected index.

Enable random_selection to choose a random input each time.
Returns the selected input unchanged.
"""

    def switch(self, number_of_inputs, random_selection, selected_index, **kwargs):
        # If random_selection is enabled, we need to read all inputs for random selection
        if random_selection:
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
        
        # For non-random selection, only read the specific input needed
        target_input_key = f"input_{selected_index}"
        if target_input_key in kwargs:
            return (kwargs[target_input_key],)
        else:
            return (None,)
    
    @classmethod
    def IS_CHANGED(cls, random_selection, **kwargs):
        # Always re-execute if random selection is enabled
        if random_selection:
            return random.random()
        return False