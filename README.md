<div align="center">

# EZ-AF Nodes for ComfyUI

[Installation](#installation) | [Nodes](#nodes) | [Example](#example)

</div>

---

A nope pack for advanced prompt-building. Conveniently control parts of text prompts with custom UI.
Pack includes loaders from txt and csv files, dynamic text concatenation tool and easy-to-use input node

# Get Started

## Installation

#### Option 1. ComfyUI-Manager

1. Install [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager) into `custom_nodes` if you haven't already:

   ```shell
   git clone https://github.com/ltdrdata/ComfyUI-Manager comfyui-manager
   ```

2. Launch/Restart ComfyUI

3. Open the Manager, search `ez-af` in the Custom Nodes Manager and then install it.

#### Option 2. Manual Installation

1. Clone this repo into `custom_nodes`:
   
    ```shell
    cd ComfyUI/custom_nodes
    git clone https://github.com/ez-af/ComfyUI-EZ-AF-Nodes.git
    ```
2. Launch/Restart ComfyUI

# Nodes

## File Loader Nodes
File loader nodes allows visually pleasing and intuitive selection of prompts, tags or other texts with custom UI.
Loader nodes can output single or multiple texts based on selection, as well as randomize selection or batch/list all texts.
Loader nodes keep selections on workflow load or page refresh.

## File Structure
Files are loaded from directories and subdirectories within `comfyui-ez-af-nodes` project, populate these directories with your custom presets as you like

```
comfyui-ez-af-nodes/
├── PROMPTS/          # For prompt text files and thumbnails
├── CSV/              # For CSV data files  
└── TAGS/             # For tag files
```

## **EZ Prompt Loader**
Loads full content of text files based on selection. Supports image thumbnails.
Thumnails are shown if there is an image (.png/.jpg) file with the name matching the .txt file name in the same folder

## **EZ CSV Loader**
Loads and processes content of CSV files based on rows.

## **EZ Tag Loader**
Loads whole lines of text based on selection.

# Utility Nodes

## **EZ Text Concatenate**
Dynamic input node. Combines any number of text inputs with customizable delimiters and text beautification options.

## **EZ Switch**
Dynamic input node. Allows selection of a single input either randomly or by index.

WARNING: This node uses "ANY" type for both inputs and output, allowing it to pass anything, including models, images, latents, etc.
This node doesn't do any processing with inputs it gets, so if you try to pass its output to a node that does not expect certain type, you will get an error.

## **EZ Extract Prompt**
Utility node, expected to be used with either CSV or PROMPT File loaders.
Extracts content from text based on headers. Can extract all non-header content or specific section.

## **EZ Text to Size**
Extracts width and height values from text strings (always uses the last 2 found numbers as size).

## **Other Text Utilities**
You may find more nodes that do basic things like find & replace or input string, i keep them for myself for testing purposes, i recommend using built-in comfy core nodes instead

# Example Workflow

*To be added*

# License

MIT License - see [LICENSE](LICENSE) file for details.

<div align="center">

**EZ-AF**

</div>
