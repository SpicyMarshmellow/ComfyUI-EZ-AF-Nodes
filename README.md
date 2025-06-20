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

##

#### Option 2. Manual Installation

1. Clone this repo into `custom_nodes`:
   
    ```shell
    git clone https://github.com/ez-af/ComfyUI-EZ-AF-Nodes.git
    ```
2. Launch/Restart ComfyUI

# Nodes

## File Loader Nodes
Custom UI File Loader nodes allows visually pleasing and intuitive selection of prompts, tags or rows of CSV file.
Loader nodes can output single or multiple texts based on mode, as well as randomize selection or batch/list all texts.
Loader nodes keep selections on workflow load or page refresh.

### Selection modes:
- single: Select one item at a time. Output 1 item at a time.
- multiple: Select multiple items. Output will be concatenated with a comma.
- random: Randomly select one item from selection on each prompt queue. If less than 2 items are selected, will draw randomly from all items.

### File Structure
Files are loaded from directories and subdirectories within `comfyui-ez-af-nodes` project, populate these directories with your custom presets as you like

```
comfyui-ez-af-nodes/
├── PROMPTS/          # For prompt text files and thumbnails
├── CSV/              # For CSV data files  
└── TAGS/             # For tag files
```

## **EZ Prompt Loader**

![image](https://github.com/user-attachments/assets/fafec7d1-ae31-40ac-b7ba-bb3f546ec810)

Loads full content of text files based on selection. Supports image thumbnails.
> [!NOTE]
> Thumnails are only shown if there is an image (.png/.jpg) file with the name matching the .txt file in the same folder

## **EZ CSV Loader**

![image](https://github.com/user-attachments/assets/f89ba509-9908-4894-856d-7fdfa80f4f46)

Loads and processes content of CSV files based on rows.
> [!NOTE]
> - Can process any number of columns, headers of currently processed file are listed in the top left corner
> - Should be used with [EZ Extract Prompt](#EZ-Extract-Prompt) node
> - Outputs a single string containing contents of all columns like this:
>  ```
>  [Header 1 = Name]:
>  3D RENDER
>
>  [Header 2 = Prompt]:
>  professional 3d render, intricate details...
>
>  ...
>  ```

## **EZ Tag Loader**

![image](https://github.com/user-attachments/assets/2699d058-1565-40fd-83c1-dc1004cd1374)

Loads whole lines of text based on selection.
> [!NOTE]
> - You can add extra text after each tag, works with all selection modes and batch.
> - Empty lines of text are ignored, to include empty tag as an option, put "\[empty\]" as a line in .txt file with tags

# Utility Nodes

## **EZ Text Concatenate**

![image](https://github.com/user-attachments/assets/98ebab2b-cac0-4e8e-a0a6-9c498e342118)

Dynamic input node. Combines any number of text inputs with customizable delimiters and text beautification options.

## **EZ Switch**

![image](https://github.com/user-attachments/assets/dd15ae5a-320d-4cf0-8fb6-c7ca50cd84b4)

Dynamic input node. Allows selection of a single input either randomly or by index.

> [!WARNING]
> This node uses "ANY" type for both inputs and output, allowing it to pass anything, including models, images, latents, etc.
> This node doesn't do any processing with inputs it gets, so if you try to pass its output to a node that does not expect certain type, you will get an error.

## **EZ Extract Prompt**

![image](https://github.com/user-attachments/assets/1c168fac-8b75-4bbb-b1e0-f5d2eae785b8)

Utility node, expected to be used with either CSV or PROMPT File loaders.
Extracts content from text based on headers. Can extract all non-header content or specific section.

## **EZ Text to Size**

![image](https://github.com/user-attachments/assets/9d239325-fe55-4f54-8b7e-f74d6b8039e5)

Extracts width and height values from text strings (always uses the last 2 found numbers as size).

## **Other Text Utilities**
You may find more nodes that do basic things like find & replace or input string, i keep them for myself for testing purposes, i recommend using built-in comfy core nodes instead

# Example Workflow

*To be added*

# License

[MIT License](LICENSE)

<div align="center">

**EZ-AF**

</div>
