<div align="center">

# EZ-AF Nodes for ComfyUI

[Installation](#installation) | [Nodes](#nodes) | [Example](#example)

</div>

---

A nope pack for advanced prompt-building. Conveniently control parts of text prompts with custom UI.
Pack includes loaders from txt and csv files, dynamic text concatenation tool and easy-to-use input node

# Get Started

## Installation

#### Option 1 — ComfyUI-Manager

1. Install [ComfyUI-Manager](https://github.com/ltdrdata/ComfyUI-Manager) into `custom_nodes` if you haven't already:

   ```shell
   git clone https://github.com/ltdrdata/ComfyUI-Manager comfyui-manager
   ```

2. Launch/Restart ComfyUI

3. Open the Manager, search `ez-af` in the Custom Nodes Manager and then install it.

#### Option 2 — Manual Installation

1. Clone this repo into `custom_nodes`:
   
    ```shell
    cd ComfyUI/custom_nodes
    git clone https://github.com/ez-af/ComfyUI-EZ-AF-Nodes.git
    ```
2. Launch/Restart ComfyUI

# Nodes

## File Loader Nodes
File loader nodes allows visual and intuitive selection of prompts, tags or other texts via custom UI.
All loader nodes can output single or multiple texts based on selection, as well as randomize selection or batch all texts.
All loader nodes can read files form subdirectories.

## File Structure
Files are loaded from directories within `comfyui-ez-af-nodes` project, populate these directories with your custom presets as you like

```
comfyui-ez-af-nodes/
├── PROMPTS/          # For prompt text files
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

# Text Processing Nodes

## **EZ Extract Prompt**
Utility node, expected to be used with File loaders.
Extracts content from text based on headers. Can extract all non-header content or specific section.

## **EZ Find & Replace**
Performs find and replace operations on text strings with case-sensitive replacement.

## **EZ Text Concatenate**
Combines any number of text inputs with customizable delimiters and text beautification options.

## **EZ Input**
Simple text input node for manual text entry with universal output type.

## **EZ Text to Size**
Extracts width and height values from text strings containing size information.

# Example Workflow

*To be added*

# License

MIT License - see [LICENSE](LICENSE) file for details.

<div align="center">

**EZ-AF**

</div>
