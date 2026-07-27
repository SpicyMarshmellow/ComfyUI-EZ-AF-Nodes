import { app } from "../../../scripts/app.js";

// Code largely inspired by FILL NODES, credit to the author: https://github.com/filliptm/ComfyUI_Fill-Nodes

app.registerExtension({
    name: "Comfy.EZ_Prompt_Loader",
    async nodeCreated(node) {
        if (node.comfyClass === "EZ_Prompt_Loader") {
            addFileBrowserUI(node);
        }
    }
});

async function addFileBrowserUI(node) {
    // Tweakable variables
    const CLICK_Y_OFFSET = 0;
    const CLICK_X_OFFSET = -2;

    const rootDirectoryWidget = node.widgets.find(w => w.name === "prompt_directory");
    const selectedFilesWidget = node.widgets.find(w => w.name === "selected_files");
    const selectionModeWidget = node.widgets.find(w => w.name === "selection_mode");
    const filterTextWidget = node.widgets.find(w => w.name === "filter_text");

    if (!rootDirectoryWidget || !selectedFilesWidget || !selectionModeWidget || !filterTextWidget) {
        console.error("Required widgets not found:", { rootDirectoryWidget, selectedFilesWidget, selectionModeWidget, filterTextWidget });
        return;
    }

    rootDirectoryWidget.hidden = false;
    selectedFilesWidget.hidden = true;
    selectionModeWidget.hidden = false;
    filterTextWidget.hidden = false;

    const MIN_WIDTH = 390;
    const MIN_HEIGHT = 410;
    const TOP_PADDING = 212;
    const BOTTOM_PADDING = 5;
    const BOTTOM_SKIP = 10;
    const TOP_BAR_HEIGHT = 0;
    const ITEM_SIZE = 180;
    const MIN_ITEM_SIZE = 180; // Your desired base size
    const ITEM_PADDING = 10;
    const SCROLLBAR_WIDTH = 8;
    const TEXT_PADDING = 10;
    const PREVIEW_PADDING = 20; // Padding for preview text
    const PREVIEW_SKIP = 152; // Skip for preview text
    const BORDER_RADIUS = 0;
    const SELECTION_BORDER_RADIUS = 0;
    const SELECTION_BORDER_PADDING = 2;
    const ELLIPSIS = "...";

    const COLORS = {
        background: "#1e1e1e",
        topBar: "#252526",
        item: "#2d2d30",
        itemHover: "#3e3e42",
        itemSelected: "#0e639c",
        text: "#ffffff",
        scrollbar: "#3e3e42",
        scrollbarHover: "#505050",
        divider: "#4f0074",
        dividerHover: "#16727c"
    };

    let currentDirectory = null;
    let filterText = filterTextWidget.value;
    let selectedFiles = new Set();
    let files = [];
    let thumbnails = {};
    let scrollOffset = 0;
    let targetScrollOffset = 0;
    let isAnimating = false;
    let isDragging = false;
    let scrollStartY = 0;
    let scrollStartOffset = 0;

    
    // Helper to calculate the stretched size
    function getAdaptiveSize() {
        const availableWidth = node.size[0] - SCROLLBAR_WIDTH - ITEM_PADDING;
        // Calculate how many columns fit at the minimum size
        const cols = Math.max(1, Math.floor(availableWidth / (MIN_ITEM_SIZE + ITEM_PADDING)));
        // Distribute remaining space so they fit perfectly
        const stretchedSize = (availableWidth / cols) - ITEM_PADDING;
        return { size: stretchedSize, cols: cols };
    }

    async function updateFiles() {
        try {
            const response = await fetch('/ez_file_browser/get_directory_structure', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: currentDirectory, filter: filterText })
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error("Server error:", errorData.error);
                return;
            }

            const data = await response.json();
            if (!data.files) {
                console.error("Invalid response format:", data);
                return;
            }

            files = data.files;
            await loadThumbnails();
            node.setDirtyCanvas(true);
        } catch (error) {
            console.error("Error updating files:", error);
        }
    }

    async function loadThumbnails() {
        thumbnails = {};
        for (const file of files) {
            try {
                const imageFile = file.replace('.txt', '.png');
                const pathParts = file.split(/[/\\]/);
                const fileName = pathParts[pathParts.length - 1];
                const dirPath = pathParts.length > 1 ? pathParts.slice(0, -1).join('/') : '';
                const fileDir = dirPath ? `${currentDirectory}/${dirPath}` : currentDirectory;
                const thumbnailDir = fileDir.replace(/prompts/g, 'thumbnails');

                const response = await fetch('/ez_file_browser/get_thumbnail', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ path: thumbnailDir, file: fileName.replace('.txt', '.png') })
                });
                if (response.ok) {
                    const blob = await response.blob();
                    thumbnails[file] = await createImageBitmap(blob);
                }
            } catch (error) {
                console.error(`Error loading thumbnail for ${file}:`, error);
            }
        }
    }

    async function fetchFileInfo(relativePath) {
        try {
            const response = await fetch('/ez_file_browser/get_file_info', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ relative_path: relativePath })
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error("Server error:", errorData.error);
                return null;
            }

            const result = await response.json();
            return result.full_path || null;
        } catch (error) {
            console.error("Error fetching file info:", error);
            return null;
        }
    }

    function updateSelectedFiles(file) {
        if (selectionModeWidget.value === "multiple" || selectionModeWidget.value === "random") {
            if (selectedFiles.has(file)) {
                selectedFiles.delete(file);
            } else {
                selectedFiles.add(file);
            }
        } else {
            selectedFiles.clear();
            selectedFiles.add(file);
        }

        const selectedFilesString = Array.from(selectedFiles).join(", ");
        selectedFilesWidget.value = selectedFilesString;
        node.setDirtyCanvas(true);
    }

    function drawPreviewText(ctx, text) {
        ctx.fillStyle = COLORS.text;
        ctx.font = "12px Arial";

        const maxWidth = node.size[0] - TEXT_PADDING * 2;

        let displayText = text;
        if (selectionModeWidget.value === "multiple") {
            const count = selectedFiles.size;
            displayText = `${count} prompt${count !== 1 ? 's' : ''} selected`;
        } else if (selectionModeWidget.value === "random") {
            const count = selectedFiles.size > 0 ? selectedFiles.size : files.length;
            displayText = `selecting from ${count} prompt${count !== 1 ? 's' : ''}`;
        } else {
            if (selectedFiles.size > 0) {
                const selectedFile = Array.from(selectedFiles)[0];
                const pathParts = selectedFile.split(/[/\\]/);
                const fileName = pathParts[pathParts.length - 1].split(".")[0];
                displayText = fileName;
            } else {
                displayText = "";
            }
        }

        const textMetrics = ctx.measureText(displayText);

        if (textMetrics.width > maxWidth) {
            let truncatedText = displayText;
            while (ctx.measureText(truncatedText + ELLIPSIS).width > maxWidth && truncatedText.length > 0) {
                truncatedText = truncatedText.slice(0, -1);
            }
            displayText = truncatedText + ELLIPSIS;
        }

        ctx.fillText(displayText, PREVIEW_PADDING, PREVIEW_SKIP);
    }

    const refreshButton = node.addWidget("button", "Refresh / Clear", null, () => {
        selectedFiles.clear();
        selectedFilesWidget.value = "";
        (async () => {
            currentDirectory = await fetchFileInfo(rootDirectoryWidget.value);
            if (currentDirectory) {
                updateFiles();
            }
        })();
    }, { serialize: false });

    rootDirectoryWidget.callback = () => {
        selectedFiles.clear();
        selectedFilesWidget.value = "";
        (async () => {
            currentDirectory = await fetchFileInfo(rootDirectoryWidget.value);
            if (currentDirectory) {
                updateFiles();
            }
        })();
    };

    filterTextWidget.callback = () => {
        filterText = filterTextWidget.value;
        updateFiles();
    };

    const invertButton = node.addWidget("button", "Invert Selection", null, () => {
        if (selectionModeWidget.value !== "multiple" && selectionModeWidget.value !== "random") return;
        const newSelected = new Set();
        for (const file of files) {
            if (!selectedFiles.has(file)) newSelected.add(file);
        }
        selectedFiles = newSelected;
        const selectedFilesString = Array.from(selectedFiles).join(", ");
        selectedFilesWidget.value = selectedFilesString;
        node.setDirtyCanvas(true);
    }, { serialize: false });

    setTimeout(() => {
        invertButton.disabled = selectionModeWidget.value !== "multiple" && selectionModeWidget.value !== "random";
    }, 0);

    const origSelectionModeCallback = selectionModeWidget.callback;
    selectionModeWidget.callback = () => {
        selectedFiles.clear();
        selectedFilesWidget.value = "";
        invertButton.disabled = selectionModeWidget.value !== "multiple" && selectionModeWidget.value !== "random";
        node.setDirtyCanvas(true);
        if (origSelectionModeCallback) origSelectionModeCallback();
    };

    node.onDrawBackground = function(ctx) {
        if (!this.flags.collapsed) {
            const pos = TOP_PADDING - TOP_BAR_HEIGHT;
            ctx.fillStyle = COLORS.background;
            ctx.fillRect(0, pos, this.size[0], this.size[1] - pos - BOTTOM_SKIP);

            ctx.fillStyle = COLORS.topBar;
            ctx.fillRect(0, pos, this.size[0], TOP_BAR_HEIGHT);

            drawPreviewText(ctx, selectedFiles.size > 0 ? Array.from(selectedFiles)[0].split(".")[0] : "");

            ctx.save();
            ctx.beginPath();
            ctx.rect(0, TOP_PADDING, this.size[0] - SCROLLBAR_WIDTH, this.size[1] - TOP_PADDING - BOTTOM_PADDING - BOTTOM_SKIP);
            ctx.clip();
            drawFiles(ctx, 0, TOP_PADDING - scrollOffset, this.size[0] - SCROLLBAR_WIDTH - 10, this.size[1] - TOP_PADDING - BOTTOM_PADDING - BOTTOM_SKIP);
            ctx.restore();

            drawScrollbar(ctx, this.size[0] - SCROLLBAR_WIDTH, TOP_PADDING, SCROLLBAR_WIDTH, this.size[1] - TOP_PADDING - BOTTOM_PADDING - BOTTOM_SKIP, scrollOffset, getTotalFilesHeight());
        }
    };

    function drawRoundedRect(ctx, x, y, width, height, radius, color) {
        ctx.beginPath();
        ctx.moveTo(x + radius, y);
        ctx.lineTo(x + width - radius, y);
        ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
        ctx.lineTo(x + width, y + height - radius);
        ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
        ctx.lineTo(x + radius, y + height);
        ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
        ctx.lineTo(x, y + radius);
        ctx.quadraticCurveTo(x, y, x + radius, y);
        ctx.closePath();
        ctx.fillStyle = color;
        ctx.fill();
    }

    function drawScrollbar(ctx, x, y, width, height, offset, totalHeight) {
        drawRoundedRect(ctx, x, y, width, height, width / 2, COLORS.scrollbar);

        const visibleHeight = height;
        const scrollHeight = Math.max(height * (visibleHeight / totalHeight), 20);
        const maxOffset = Math.max(0, totalHeight - visibleHeight);
        const scrollY = y + (offset / maxOffset) * (height - scrollHeight);

        drawRoundedRect(ctx, x, scrollY, width, scrollHeight, width / 2, COLORS.scrollbarHover);
    }

    // FIX: now uses the same adaptive sizing as drawFiles/onMouseDown,
    // instead of the old fixed ITEM_SIZE, so scrollbar height and scroll
    // bounds can never drift out of sync with the actual rendered grid.
    function getTotalFilesHeight() {
        const { size, cols } = getAdaptiveSize();
        return Math.ceil(files.length / cols) * (size + ITEM_PADDING);
    }

    function drawFiles(ctx, x, y, width, height) {
        const { size, cols } = getAdaptiveSize();
        const startRow = Math.floor(scrollOffset / (size + ITEM_PADDING));
        const endRow = Math.min(Math.ceil(files.length / cols), startRow + Math.ceil(height / (size + ITEM_PADDING)) + 2);

        for (let row = startRow; row < endRow; row++) {
            for (let col = 0; col < cols; col++) {
                const fileIndex = row * cols + col;
                if (fileIndex >= files.length) break;

                const file = files[fileIndex];
                const xPos = x + ITEM_PADDING + col * (size + ITEM_PADDING);
                const yPos = y + ITEM_PADDING + row * (size + ITEM_PADDING);

                const bgColor = selectedFiles.has(file) ? COLORS.itemSelected : COLORS.item;
                drawRoundedRect(ctx, xPos, yPos, size, size, BORDER_RADIUS, bgColor);

                if (thumbnails[file]) {
                    ctx.save();
                    ctx.beginPath();
                    ctx.roundRect(xPos, yPos, size, size, BORDER_RADIUS);
                    ctx.clip();
                    ctx.drawImage(thumbnails[file], xPos, yPos, size, size);
                    ctx.restore();
                }

                const gradientHeight = size / 2;
                const gradient = ctx.createLinearGradient(xPos, yPos + size - gradientHeight, xPos, yPos + size);
                gradient.addColorStop(0, 'rgba(0, 0, 0, 0)');
                gradient.addColorStop(1, 'rgb(0, 0, 0)');
                ctx.fillStyle = gradient;
                ctx.fillRect(xPos, yPos + size - gradientHeight, size, gradientHeight);

                ctx.fillStyle = COLORS.text;
                ctx.font = "12px Arial";
                const pathParts = file.split(/[/\\]/);
                const fileName = pathParts[pathParts.length - 1].split(".")[0];
                const maxTextWidth = size - TEXT_PADDING * 2;

                let displayText = fileName;
                if (ctx.measureText(displayText).width > maxTextWidth) {
                    while (ctx.measureText(displayText + ELLIPSIS).width > maxTextWidth && displayText.length > 0) {
                        displayText = displayText.slice(0, -1);
                    }
                    displayText += ELLIPSIS;
                }
                ctx.fillText(displayText, xPos + TEXT_PADDING, yPos + size - TEXT_PADDING);

                if (selectedFiles.has(file)) {
                    ctx.strokeStyle = COLORS.itemSelected;
                    ctx.lineWidth = 3;
                    ctx.strokeRect(xPos - 1, yPos - 1, size + 2, size + 2);
                }
            }
        }
    }

    node.onMouseDown = function(event) {
        const pos = TOP_PADDING - TOP_BAR_HEIGHT;
        const localY = event.canvasY - this.pos[1] - pos + CLICK_Y_OFFSET;
        const localX = event.canvasX - this.pos[0] + CLICK_X_OFFSET;

        if (localY < 0 || localY > this.size[1] || localX < 0 || localX > this.size[0]) {
            return false;
        }

        if (localY > TOP_BAR_HEIGHT && localY < this.size[1] - pos - 10) {
            if (localX >= 0 && localX < this.size[0] - SCROLLBAR_WIDTH) {
                const { size, cols } = getAdaptiveSize();
                const row = Math.floor((localY - TOP_BAR_HEIGHT + scrollOffset) / (size + ITEM_PADDING));
                const col = Math.floor(localX / (size + ITEM_PADDING));
                const fileIndex = row * cols + col;

                if (fileIndex >= 0 && fileIndex < files.length) {
                    updateSelectedFiles(files[fileIndex]);
                }
                return true;
            } else if (localX >= this.size[0] - SCROLLBAR_WIDTH) {
                isDragging = true;
                scrollStartY = event.canvasY;
                scrollStartOffset = scrollOffset;
                return true;
            }
        }

        return false;
    };

    node.onMouseMove = function(event) {
        const pos = TOP_PADDING - TOP_BAR_HEIGHT;
        const localY = event.canvasY - this.pos[1] - pos + CLICK_Y_OFFSET;
        const localX = event.canvasX - this.pos[0] + CLICK_X_OFFSET;

        if (isDragging) {
            const totalHeight = getTotalFilesHeight();
            const visibleHeight = this.size[1] - TOP_PADDING - BOTTOM_PADDING - BOTTOM_SKIP;
            const maxOffset = Math.max(0, totalHeight - visibleHeight);
            const scrollMove = (event.canvasY - scrollStartY) * (totalHeight / visibleHeight);
            scrollOffset = Math.max(0, Math.min(maxOffset, scrollStartOffset + scrollMove));
            this.setDirtyCanvas(true);
            return true;
        }

        return false;
    };

    node.onMouseUp = function(event) {
        isDragging = false;
        document.body.style.cursor = 'default';
        return false;
    };

    function updateNodeSize() {
        const width = Math.max(MIN_WIDTH, node.size[0]);
        const height = Math.max(MIN_HEIGHT, node.size[1]);
        node.size[0] = width;
        node.size[1] = height;
    }

    node.onResize = function() {
        updateNodeSize();
        this.setDirtyCanvas(true);
    };

    setTimeout(() => {
        selectedFiles = new Set(
            selectedFilesWidget.value.split(',').map(t => t.trim()).filter(t => t !== '')
        );
        invertButton.disabled = selectionModeWidget.value !== "multiple" && selectionModeWidget.value !== "random";
        node.setDirtyCanvas(true);
    }, 0);

    setTimeout(async () => {
        currentDirectory = await fetchFileInfo(rootDirectoryWidget.value);
        if (currentDirectory) {
            updateFiles();
        }
        updateNodeSize();
    }, 0);

    const canvasEl = app.canvas.canvas;

    const stopViewportZoom = (event) => {
        const rect = canvasEl.getBoundingClientRect();
        const mouseX = event.clientX - rect.left;
        const mouseY = event.clientY - rect.top;
        const worldPos = app.canvas.convertCanvasToOffset([mouseX, mouseY]);

        const localX = worldPos[0] - node.pos[0];
        const localY = worldPos[1] - node.pos[1];

        const isOverBrowser = (
            localX >= 0 &&
            localX <= node.size[0] &&
            localY >= TOP_PADDING &&
            localY <= node.size[1] - BOTTOM_SKIP
        );

        if (isOverBrowser && !node.flags.collapsed) {
            event.preventDefault();
            event.stopPropagation();

            const totalHeight = getTotalFilesHeight();
            const visibleHeight = node.size[1] - TOP_PADDING - BOTTOM_PADDING - BOTTOM_SKIP;
            const maxOffset = Math.max(0, totalHeight - visibleHeight);

            targetScrollOffset = Math.max(0, Math.min(maxOffset, targetScrollOffset + event.deltaY * 0.5));

            if (!isAnimating) {
                isAnimating = true;
                requestAnimationFrame(smoothScrollLoop);
            }
        }
    };

    function smoothScrollLoop() {
        const easingFactor = 0.15;
        const diff = targetScrollOffset - scrollOffset;

        if (Math.abs(diff) > 0.1) {
            scrollOffset += diff * easingFactor;
            node.setDirtyCanvas(true);
            requestAnimationFrame(smoothScrollLoop);
        } else {
            scrollOffset = targetScrollOffset;
            isAnimating = false;
            node.setDirtyCanvas(true);
        }
    }

    canvasEl.addEventListener('wheel', stopViewportZoom, { passive: false, capture: true });

    const onRemoved = node.onRemoved;
    node.onRemoved = function() {
        canvasEl.removeEventListener('wheel', stopViewportZoom, { capture: true });
        if (onRemoved) onRemoved.apply(this, arguments);
    };
}
