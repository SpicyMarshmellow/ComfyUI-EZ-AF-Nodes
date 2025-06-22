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
                "number_of_inputs": ("INT", {"default": 2, "min": 2, "max": 50, "step": 1, "tooltip": "Dynamically select number of inputs. Only the last of current inputs may be affected when this value is changed"}),
                "selected_index": ("INT", {"default": 1, "min": 1, "max": 50, "step": 1, "tooltip": "Index of input to be passed to output (if in 'by index' mode)"}),
                "selection_mode": (["by index", "by random", "automatic"], {"default": "by index", "tooltip": "modes:\n"
                                                                                            "- by index: Select input by specifying index\n"
                                                                                            "- by random: Choose a random input each time\n"
                                                                                            "- automatic: Output the first input that is not None"}),
            },
            "optional": {
                "opt_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, "forceInput": True, "tooltip": "Control SEED, used only in 'by random' selection mode.\nIf not connected, always re-executes node on prompt"}),
            },
            "hidden": {
                **{f"input_{i}": ("*", {"forceInput": "True"}) for i in range(1, 51)}
            },
        }

    RETURN_TYPES = (any,)

    OUTPUT_TOOLTIPS = ("Unprocessed value of any type.",)

    FUNCTION = "switch"

    CATEGORY = "EZ NODES"
    DESCRIPTION = "Switch between any number of inputs automatically, based on index or randomly."


    def switch(self, number_of_inputs, selection_mode, selected_index=None, opt_seed=0, **kwargs):
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
            # Use seed for deterministic random selection only if opt_seed is provided and not 0
            if opt_seed is not None and opt_seed != 0:
                random.seed(opt_seed)
            
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
    def IS_CHANGED(cls, selection_mode, opt_seed=0, **kwargs):
        # Always re-execute if random selection is enabled
        if selection_mode == "by random":
            # For random mode, include seed in the hash only if opt_seed is provided and not 0
            if opt_seed is not None and opt_seed != 0:
                return str(opt_seed) + str(selection_mode)
            else:
                return float('nan')  # Fall back to normal random behavior
        return False