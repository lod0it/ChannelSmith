/**
 * ChannelSmith Web UI Application
 *
 * Main JavaScript application for the ChannelSmith texture packing/unpacking tool.
 * Handles UI interactions, state management, and API communication.
 */

// ============================================================================
// STATE MANAGEMENT
// ============================================================================

const state = {
    currentTab: 'pack',
    packTemplate: 'Free',
    unpackTemplate: 'Free',
    packChannels: {
        red_channel: null,
        green_channel: null,
        blue_channel: null,
        alpha_channel: null,
    },
    unpackImage: null,
    packedResult: null,
    unpackedChannels: {},
    docsLoaded: false,
    templateDetails: {},
};

// Channel type to human-readable label mapping
const CHANNEL_TYPE_LABELS = {
    'ambient_occlusion': 'Ambient Occlusion',
    'roughness': 'Roughness',
    'metallic': 'Metallic',
    'displacement': 'Displacement',
    'opacity': 'Opacity',
};

// Template channel mappings (hardcoded to avoid API calls)
const TEMPLATE_CHANNELS = {
    'Free': {
        'R': { type: 'ambient_occlusion', label: 'Red Channel' },
        'G': { type: 'roughness', label: 'Green Channel' },
        'B': { type: 'metallic', label: 'Blue Channel' },
        'A': { type: 'opacity', label: 'Alpha Channel (Optional)' },
    },
    'ORM': {
        'R': { type: 'ambient_occlusion', label: 'Ambient Occlusion' },
        'G': { type: 'roughness', label: 'Roughness' },
        'B': { type: 'metallic', label: 'Metallic' },
        'A': { type: 'opacity', label: 'Alpha Channel (Optional)' },
    },
    'ORD': {
        'R': { type: 'ambient_occlusion', label: 'Ambient Occlusion' },
        'G': { type: 'roughness', label: 'Roughness' },
        'B': { type: 'displacement', label: 'Displacement' },
        'A': { type: 'opacity', label: 'Alpha Channel (Optional)' },
    },
};

// ============================================================================
// API CLIENT
// ============================================================================

const API = {
    baseURL: '/api',

    /**
     * Pack texture channels into a single image.
     */
    async pack(template, channels) {
        const formData = new FormData();
        formData.append('template', template);

        for (const [key, file] of Object.entries(channels)) {
            if (file) {
                formData.append(key, file);
            }
        }

        const response = await fetch(`${this.baseURL}/pack`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Pack failed');
        }

        return await response.blob();
    },

    /**
     * Unpack a texture image into individual channels.
     */
    async unpack(imageFile, template) {
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('template', template);

        const response = await fetch(`${this.baseURL}/unpack`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Unpack failed');
        }

        return await response.json();
    },

    /**
     * Get list of available templates.
     */
    async getTemplates() {
        const response = await fetch(`${this.baseURL}/templates`);
        if (!response.ok) throw new Error('Failed to fetch templates');
        return await response.json();
    },

    /**
     * Get detailed information about a specific template.
     */
    async getTemplateDetails(templateName) {
        const response = await fetch(`${this.baseURL}/templates/${templateName}`);
        if (!response.ok) throw new Error(`Failed to fetch template details for ${templateName}`);
        return await response.json();
    },

    /**
     * Health check.
     */
    async health() {
        const response = await fetch(`${this.baseURL}/health`);
        return response.ok;
    },
};

// ============================================================================
// UI UTILITIES
// ============================================================================

function showProgress(message) {
    const container = document.getElementById('progress-container');
    document.getElementById('progress-message').textContent = message;
    container.classList.remove('hidden');
}

function hideProgress() {
    document.getElementById('progress-container').classList.add('hidden');
}

function showError(message) {
    const container = document.getElementById('error-container');
    document.getElementById('error-message').textContent = message;
    container.classList.remove('hidden');
    setTimeout(() => container.classList.add('hidden'), 5000);
}

function showSuccess(message) {
    const container = document.getElementById('success-container');
    document.getElementById('success-message').textContent = message;
    container.classList.remove('hidden');
    setTimeout(() => container.classList.add('hidden'), 3000);
}

// ============================================================================
// ZOOM PREVIEW
// ============================================================================

function openZoom(imageElement, label) {
    const modal = document.getElementById('zoom-modal');
    const zoomImage = document.getElementById('zoom-image');
    const zoomLabel = document.getElementById('zoom-label');

    if (imageElement.tagName === 'CANVAS') {
        // Convert canvas to image
        zoomImage.src = imageElement.toDataURL('image/png');
    } else if (imageElement.tagName === 'IMG') {
        zoomImage.src = imageElement.src;
    }

    zoomLabel.textContent = label || 'Preview';
    modal.classList.add('active');
}

function closeZoom(event) {
    // Allow closing by clicking outside or on close button
    const modal = document.getElementById('zoom-modal');
    modal.classList.remove('active');
}

// ============================================================================
// DOCUMENTATION LOADING
// ============================================================================

/**
 * Simple markdown to HTML converter for documentation display.
 * Handles headings, emphasis, links, lists, code blocks, and tables.
 */
function markdownToHtml(markdown) {
    let html = markdown;

    // Escape HTML
    html = html
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');

    // Code blocks (triple backticks)
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
        return `<pre class="bg-[#0a0a0a] border border-[#2a2a2a] rounded p-4 overflow-x-auto my-4"><code class="text-gray-300 text-sm">${code.trim()}</code></pre>`;
    });

    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code class="bg-[#0a0a0a] px-2 py-1 rounded text-[#ff8c42] text-sm">$1</code>');

    // Headers
    html = html.replace(/^### (.*?)$/gm, '<h3 class="text-xl font-bold mt-6 mb-3 text-[#ff6b35]">$1</h3>');
    html = html.replace(/^## (.*?)$/gm, '<h2 class="text-2xl font-bold mt-8 mb-4 text-[#ff6b35]">$1</h2>');
    html = html.replace(/^# (.*?)$/gm, '<h1 class="text-3xl font-bold mt-10 mb-5 text-[#ff6b35]">$1</h1>');

    // Horizontal rules
    html = html.replace(/^---$/gm, '<hr class="my-6 border-[#2a2a2a]">');

    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold">$1</strong>');

    // Italic
    html = html.replace(/\*(.*?)\*/g, '<em class="italic">$1</em>');

    // Links
    html = html.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" class="text-[#ff8c42] hover:text-[#ffa65a] underline" target="_blank">$1</a>');

    // Lists - unordered
    html = html.replace(/^\s*[-*+] (.*?)$/gm, '<li class="ml-6">$1</li>');
    html = html.replace(/(<li class="ml-6">.*?<\/li>)/s, (match) => {
        return '<ul class="list-disc my-3">' + match + '</ul>';
    });

    // Lists - ordered
    html = html.replace(/^\s*(\d+)\. (.*?)$/gm, '<li class="ml-6">$2</li>');
    html = html.replace(/(<li class="ml-6">[0-9].*?<\/li>)/s, (match) => {
        return '<ol class="list-decimal my-3">' + match + '</ol>';
    });

    // Tables
    html = html.replace(
        /\| (.*?) \|\n\| *[-:| ]+? *\|\n((?:\| .*? \|\n?)*)/g,
        (match, headers, rows) => {
            const headerCells = headers.split('|').map(h => h.trim()).filter(h => h);
            const rowsArray = rows.split('\n').filter(r => r.trim());

            let table = '<table class="w-full my-4 border-collapse"><thead>';
            table += '<tr class="border-b border-[#2a2a2a]">';
            headerCells.forEach(h => {
                table += `<th class="text-left px-4 py-2 font-bold text-[#ff8c42]">${h}</th>`;
            });
            table += '</tr></thead><tbody>';

            rowsArray.forEach(row => {
                const cells = row.split('|').map(c => c.trim()).filter(c => c);
                if (cells.length === headerCells.length) {
                    table += '<tr class="border-b border-[#2a2a2a]">';
                    cells.forEach(cell => {
                        table += `<td class="px-4 py-2 text-gray-300">${cell}</td>`;
                    });
                    table += '</tr>';
                }
            });

            table += '</tbody></table>';
            return table;
        }
    );

    // Paragraphs
    html = html.replace(/\n\n+/g, '</p><p class="my-4 leading-relaxed text-gray-300">');
    html = '<p class="my-4 leading-relaxed text-gray-300">' + html + '</p>';

    // Line breaks
    html = html.replace(/\n(?!<)/g, '<br>');

    // Clean up double tags
    html = html.replace(/<\/p><p class="my-4 leading-relaxed text-gray-300"><\/p>/g, '</p><p class="my-4 leading-relaxed text-gray-300">');
    html = html.replace(/<p class="my-4 leading-relaxed text-gray-300"><\/p>/g, '');

    return html;
}

/**
 * Load and display the documentation from cs_wiki.md
 */
async function loadDocumentation() {
    const contentContainer = document.getElementById('info-content');

    try {
        // Fetch documentation from the Flask route
        console.log('Loading documentation...');
        const response = await fetch('/cs_wiki.md', {
            method: 'GET',
            headers: {
                'Accept': 'text/markdown, text/plain, */*',
            },
            cache: 'no-cache',
        });

        console.log(`Fetch response status: ${response.status}`);

        if (!response.ok) {
            console.log(`Failed to load documentation. Status: ${response.status} ${response.statusText}`);
            console.log('Response headers:', response.headers);
            const text = await response.text();
            console.log('Response body:', text);
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const markdown = await response.text();
        const htmlContent = markdownToHtml(markdown);

        contentContainer.innerHTML = htmlContent;

        // Scroll to top
        contentContainer.scrollTop = 0;
    } catch (error) {
        console.error('Failed to load documentation:', error);
        contentContainer.innerHTML = `
            <div class="text-center py-12 text-red-400">
                <p>⚠️ Error loading documentation</p>
                <p class="text-sm text-gray-500 mt-2">${error.message}</p>
            </div>
        `;
    }
}

function switchTab(tabName) {
    state.currentTab = tabName;

    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });

    // Update panels
    document.querySelectorAll('.panel-section').forEach(panel => {
        panel.classList.toggle('active', panel.id === `${tabName}-panel`);
    });
}

/**
 * Reset channel labels to generic names (for Free template).
 */
function resetChannelLabelsToGeneric() {
    console.log('[resetChannelLabelsToGeneric] Resetting channel labels to generic names');

    const labelEl = document.getElementById('label-red');
    const labelEl2 = document.getElementById('label-green');
    const labelEl3 = document.getElementById('label-blue');
    const labelEl4 = document.getElementById('label-alpha');

    if (labelEl) { labelEl.innerText = 'Red Channel'; console.log('Updated label-red'); }
    if (labelEl2) { labelEl2.innerText = 'Green Channel'; console.log('Updated label-green'); }
    if (labelEl3) { labelEl3.innerText = 'Blue Channel'; console.log('Updated label-blue'); }
    if (labelEl4) { labelEl4.innerText = 'Alpha Channel (Optional)'; console.log('Updated label-alpha'); }

    const previewEl1 = document.getElementById('preview-label-red');
    const previewEl2 = document.getElementById('preview-label-green');
    const previewEl3 = document.getElementById('preview-label-blue');
    const previewEl4 = document.getElementById('preview-label-alpha');

    if (previewEl1) { previewEl1.innerText = 'Red'; console.log('Updated preview-label-red'); }
    if (previewEl2) { previewEl2.innerText = 'Green'; console.log('Updated preview-label-green'); }
    if (previewEl3) { previewEl3.innerText = 'Blue'; console.log('Updated preview-label-blue'); }
    if (previewEl4) { previewEl4.innerText = 'Alpha'; console.log('Updated preview-label-alpha'); }
}

/**
 * Update pack channel labels based on the selected template.
 * Uses hardcoded template mappings (no API calls needed).
 */
function updatePackChannelLabels(templateName) {
    console.log(`[updatePackChannelLabels] Called with template: ${templateName}`);

    // Get template configuration (hardcoded)
    const templateConfig = TEMPLATE_CHANNELS[templateName];
    if (!templateConfig) {
        console.error(`[updatePackChannelLabels] Unknown template: ${templateName}`);
        return;
    }

    console.log(`[updatePackChannelLabels] Using template config for ${templateName}`);

    // Update each channel position
    const positions = [
        { pos: 'R', labelId: 'label-red', previewId: 'preview-label-red' },
        { pos: 'G', labelId: 'label-green', previewId: 'preview-label-green' },
        { pos: 'B', labelId: 'label-blue', previewId: 'preview-label-blue' },
        { pos: 'A', labelId: 'label-alpha', previewId: 'preview-label-alpha' },
    ];

    for (const posItem of positions) {
        const channelInfo = templateConfig[posItem.pos];
        if (!channelInfo) {
            console.log(`[updatePackChannelLabels] No channel info for position ${posItem.pos}`);
            continue;
        }

        const label = channelInfo.label;
        console.log(`[updatePackChannelLabels] Position ${posItem.pos}: label="${label}"`);

        // Update main label
        const labelElement = document.getElementById(posItem.labelId);
        if (labelElement) {
            labelElement.innerText = label;
            console.log(`[updatePackChannelLabels] ✓ Updated ${posItem.labelId} to "${label}"`);
        } else {
            console.warn(`[updatePackChannelLabels] ✗ Element ${posItem.labelId} NOT FOUND`);
        }

        // Update preview label (shortened version)
        const previewLabel = label.length > 10 ? label.split(' ')[0] : label;
        const previewLabelElement = document.getElementById(posItem.previewId);
        if (previewLabelElement) {
            previewLabelElement.innerText = previewLabel;
            console.log(`[updatePackChannelLabels] ✓ Updated ${posItem.previewId} to "${previewLabel}"`);
        } else {
            console.warn(`[updatePackChannelLabels] ✗ Element ${posItem.previewId} NOT FOUND`);
        }
    }
}

// ============================================================================
// FILE HANDLING
// ============================================================================

function isImageFile(file) {
    // Check MIME type for standard image formats
    if (file.type.startsWith('image/')) {
        return true;
    }
    // Also accept TGA files by extension (MIME type often not recognized by browsers)
    if (file.name.toLowerCase().endsWith('.tga')) {
        return true;
    }
    return false;
}

function setupUploadZone(zoneElement) {
    const fileInput = zoneElement.querySelector('input[type="file"]');
    const channel = zoneElement.dataset.channel;

    // Click to upload
    zoneElement.addEventListener('click', () => fileInput.click());

    // File selection
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelected(channel, e.target.files[0], zoneElement);
        }
    });

    // Drag and drop
    zoneElement.addEventListener('dragover', (e) => {
        e.preventDefault();
        zoneElement.classList.add('dragover');
    });

    zoneElement.addEventListener('dragleave', () => {
        zoneElement.classList.remove('dragover');
    });

    zoneElement.addEventListener('drop', (e) => {
        e.preventDefault();
        zoneElement.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (isImageFile(file)) {
                handleFileSelected(channel, file, zoneElement);
            } else {
                showError('Please drop an image file');
            }
        }
    });
}

function handleFileSelected(channel, file, zoneElement) {
    // Store file
    state.packChannels[channel] = file;

    // Update UI
    zoneElement.style.borderColor = '#ff8c42';
    zoneElement.style.backgroundColor = 'rgba(255, 107, 53, 0.1)';

    // Show clear button
    const clearBtn = zoneElement.parentElement.querySelector('.clear-btn');
    if (clearBtn) {
        clearBtn.classList.remove('hidden');
    }

    // Show preview
    const previewId = `preview-${channel.split('_')[0]}`;
    const previewCanvas = document.getElementById(previewId);
    if (previewCanvas) {
        displayImagePreview(file, previewCanvas);

        // Make preview clickable when image is uploaded
        const card = previewCanvas.closest('.preview-card');
        if (card && !card.classList.contains('clickable')) {
            card.classList.add('clickable');
            previewCanvas.addEventListener('click', () => {
                openZoom(previewCanvas, channel.split('_')[0].charAt(0).toUpperCase() + channel.split('_')[0].slice(1));
            });
        }
    }

    // Update pack button ready state if at least one channel is selected
    updatePackButtonState();
}

function displayImagePreview(file, canvas) {
    const ctx = canvas.getContext('2d');
    const img = new Image();

    img.onload = () => {
        // Clear canvas with checkerboard
        ctx.fillStyle = '#0a0a0a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw checkerboard pattern
        for (let i = 0; i < canvas.width; i += 20) {
            for (let j = 0; j < canvas.height; j += 20) {
                if ((i / 20 + j / 20) % 2 === 0) {
                    ctx.fillStyle = '#0f0f0f';
                    ctx.fillRect(i, j, 20, 20);
                }
            }
        }

        // Scale and center image
        const scale = Math.min(
            canvas.width / img.width,
            canvas.height / img.height,
            1
        );
        const x = (canvas.width - img.width * scale) / 2;
        const y = (canvas.height - img.height * scale) / 2;

        ctx.drawImage(img, x, y, img.width * scale, img.height * scale);
    };

    img.src = URL.createObjectURL(file);
}

function clearChannelUpload(channel) {
    // Clear state
    state.packChannels[channel] = null;

    // Find zone and reset UI
    const zone = document.querySelector(`[data-channel="${channel}"]`);
    if (zone) {
        zone.style.borderColor = '';
        zone.style.backgroundColor = '';

        // Reset file input
        const fileInput = zone.querySelector('input[type="file"]');
        if (fileInput) {
            fileInput.value = '';
        }

        // Hide clear button
        const clearBtn = zone.parentElement.querySelector('.clear-btn');
        if (clearBtn) {
            clearBtn.classList.add('hidden');
        }

        // Clear preview canvas and remove clickable class
        const previewId = `preview-${channel.split('_')[0]}`;
        const previewCanvas = document.getElementById(previewId);
        if (previewCanvas) {
            const ctx = previewCanvas.getContext('2d');
            ctx.fillStyle = '#0a0a0a';
            ctx.fillRect(0, 0, previewCanvas.width, previewCanvas.height);

            // Remove clickable class when image is cleared
            const card = previewCanvas.closest('.preview-card');
            if (card) {
                card.classList.remove('clickable');
            }
        }
    }

    // Update pack button ready state
    updatePackButtonState();
}

function updatePackButtonState() {
    const packButton = document.getElementById('pack-button');
    const hasChannels = Object.values(state.packChannels).some(ch => ch !== null);

    if (hasChannels) {
        if (!packButton.classList.contains('ready')) {
            packButton.classList.add('ready', 'vibrate');
            setTimeout(() => {
                packButton.classList.remove('vibrate');
            }, 600);
        }
    } else {
        packButton.classList.remove('ready');
    }
}

// ============================================================================
// PACK TEXTURE FUNCTIONALITY
// ============================================================================

async function handlePack() {
    try {
        // Get selected template
        const template = document.getElementById('pack-template').value;
        state.packTemplate = template;

        // Check if at least one channel is provided
        const hasChannels = Object.values(state.packChannels).some(ch => ch !== null);
        if (!hasChannels) {
            showError('Please upload at least one channel');
            return;
        }

        showProgress('Packing texture...');

        // Call API
        const blob = await API.pack(template, state.packChannels);
        state.packedResult = blob;

        // Display result
        displayPackedResult(blob);
        showSuccess('Texture packed successfully!');

        hideProgress();
    } catch (error) {
        showError(`Pack failed: ${error.message}`);
        hideProgress();
    }
}

function displayPackedResult(blob) {
    const resultSection = document.getElementById('pack-result');
    const resultImage = document.getElementById('result-image');

    // Create data URL
    const url = URL.createObjectURL(blob);
    resultImage.src = url;

    // Show result section
    resultSection.classList.remove('hidden');

    // Make result image clickable and add zoom handler
    const card = resultImage.closest('.preview-card');
    if (card && !card.classList.contains('clickable')) {
        card.classList.add('clickable');
        if (!resultImage.hasClickHandler) {
            resultImage.addEventListener('click', () => {
                openZoom(resultImage, 'Packed Result');
            });
            resultImage.hasClickHandler = true;
        }
    }

    // Setup download button
    document.getElementById('download-packed').onclick = () => {
        const link = document.createElement('a');
        link.href = url;
        link.download = `channelsmith_packed_${state.packTemplate.toLowerCase()}.png`;
        link.click();
    };
}

// ============================================================================
// UNPACK TEXTURE FUNCTIONALITY
// ============================================================================

async function handleUnpack() {
    try {
        if (!state.unpackImage) {
            showError('Please upload an image to unpack');
            return;
        }

        // Auto-detect template from image or use default
        const template = state.unpackTemplate || 'ORM';

        showProgress('Unpacking texture...');

        // Call API
        const result = await API.unpack(state.unpackImage, template);
        state.unpackedChannels = result.channels;

        // Display results
        displayUnpackedChannels(result.channels);
        showSuccess('Texture unpacked successfully!');

        // Reset button state for next upload
        const unpackButton = document.getElementById('unpack-button');
        unpackButton.classList.remove('ready');
        state.unpackImage = null;

        hideProgress();
    } catch (error) {
        showError(`Unpack failed: ${error.message}`);
        hideProgress();
    }
}

function displayUnpackedChannels(channels) {
    const resultsContainer = document.getElementById('unpack-results');
    resultsContainer.innerHTML = '';

    // Channel position labels
    const channelLabels = {
        R: { label: 'Red Channel', color: 'bg-red-600' },
        G: { label: 'Green Channel', color: 'bg-green-600' },
        B: { label: 'Blue Channel', color: 'bg-blue-600' },
        A: { label: 'Alpha Channel', color: 'bg-gray-600' },
    };

    // Display channels in order: R, G, B, A
    const channelOrder = ['R', 'G', 'B', 'A'];
    for (const channelPos of channelOrder) {
        if (!(channelPos in channels)) continue;

        const base64Data = channels[channelPos];
        const info = channelLabels[channelPos];

        const card = document.createElement('div');
        card.className = 'preview-card clickable';
        card.innerHTML = `
            <div class="flex justify-between items-start mb-3">
                <div class="preview-label">${info.label}</div>
                <button class="btn-secondary text-xs py-1 px-2" onclick="downloadChannel('${channelPos}', '${base64Data}')">
                    📥 Download
                </button>
            </div>
            <img src="${base64Data}" class="w-full rounded-lg unpack-preview-image" style="image-rendering: pixelated;" data-channel="${channelPos}" data-label="${info.label}">
        `;

        resultsContainer.appendChild(card);

        // Add click handler for zoom
        const img = card.querySelector('img');
        img.addEventListener('click', () => {
            openZoom(img, info.label);
        });
    }
}

function downloadChannel(channelType, base64Data) {
    const link = document.createElement('a');
    link.href = base64Data;
    link.download = `channelsmith_${channelType}_${state.unpackTemplate.toLowerCase()}.png`;
    link.click();
}

// ============================================================================
// INITIALIZATION
// ============================================================================

function setupUnpackUploadZone() {
    const zone = document.getElementById('unpack-upload');
    const fileInput = zone.querySelector('input[type="file"]');
    const feedback = document.getElementById('unpack-upload-feedback');
    const filenameSpan = document.getElementById('unpack-filename');
    const unpackButton = document.getElementById('unpack-button');
    const clearBtn = document.getElementById('unpack-clear-btn');

    function updateFeedback(file) {
        state.unpackImage = file;
        zone.style.borderColor = '#ff8c42';
        zone.style.backgroundColor = 'rgba(255, 107, 53, 0.1)';
        filenameSpan.textContent = file.name;
        feedback.classList.remove('hidden');
        clearBtn.classList.remove('hidden');

        // Make unpack button green and add vibration animation
        unpackButton.classList.add('ready', 'vibrate');

        // Remove vibration animation after it completes
        setTimeout(() => {
            unpackButton.classList.remove('vibrate');
        }, 600);
    }

    function clearUnpackUpload() {
        state.unpackImage = null;
        fileInput.value = '';
        zone.style.borderColor = '';
        zone.style.backgroundColor = '';
        feedback.classList.add('hidden');
        clearBtn.classList.add('hidden');
        unpackButton.classList.remove('ready');
    }

    // Click to upload
    zone.addEventListener('click', () => fileInput.click());

    // File selection
    fileInput.addEventListener('change', (e) => {
        if (e.target.length > 0 || (e.target.files && e.target.files.length > 0)) {
            const file = e.target.files[0];
            updateFeedback(file);
        }
    });

    // Drag and drop
    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('dragover');
    });

    zone.addEventListener('dragleave', () => {
        zone.classList.remove('dragover');
    });

    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (isImageFile(file)) {
                updateFeedback(file);
            } else {
                showError('Please drop an image file');
            }
        }
    });

    // Clear button handler
    clearBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        clearUnpackUpload();
    });
}

function initApp() {
    // Setup mode toggle (Pack/Unpack switch)
    const modeToggle = document.getElementById('mode-toggle');
    if (modeToggle) {
        modeToggle.addEventListener('change', () => {
            switchTab(modeToggle.checked ? 'unpack' : 'pack');
        });
    }

    // Setup Info button
    const infoButton = document.getElementById('info-button');
    if (infoButton) {
        infoButton.addEventListener('click', () => {
            switchTab('info');
            if (!state.docsLoaded) {
                loadDocumentation();
                state.docsLoaded = true;
            }
        });
    }

    // Setup Info Close button
    const infoCloseBtn = document.getElementById('info-close-btn');
    if (infoCloseBtn) {
        infoCloseBtn.addEventListener('click', () => {
            switchTab('pack');
            modeToggle.checked = false;
        });
    }

    // Setup pack upload zones
    document.querySelectorAll('#pack-channels .upload-zone').forEach(zone => {
        setupUploadZone(zone);
    });

    // Setup clear buttons
    document.querySelectorAll('.clear-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const channel = btn.dataset.channel;
            clearChannelUpload(channel);
        });
    });

    // Setup pack button
    document.getElementById('pack-button').addEventListener('click', handlePack);

    // Setup unpack upload zone
    setupUnpackUploadZone();

    // Setup unpack button
    document.getElementById('unpack-button').addEventListener('click', handleUnpack);

    // Initialize tab visibility
    switchTab('pack');

    // Set default template to 'Free' and add change listener
    const packTemplateSelect = document.getElementById('pack-template');
    console.log('packTemplateSelect element:', packTemplateSelect);
    if (packTemplateSelect) {
        console.log('Setting up pack template selector');
        packTemplateSelect.value = 'Free';
        console.log('Initial template value:', packTemplateSelect.value);

        // Update labels when template changes
        packTemplateSelect.addEventListener('change', (e) => {
            console.log('Pack template changed to:', e.target.value);
            updatePackChannelLabels(e.target.value);
        });
        console.log('Event listener attached to pack template selector');

        // Initial label update for default template
        console.log('Calling updatePackChannelLabels with "Free"');
        updatePackChannelLabels('Free');
    } else {
        console.error('Pack template selector element not found!');
    }

    // Load available templates
    API.getTemplates().then(data => {
        // Update template selectors if needed
        console.log('Available templates:', data.templates);
    }).catch(error => {
        console.error('Failed to load templates:', error);
    });

    // Health check
    API.health().then(ok => {
        if (!ok) {
            showError('Backend connection failed');
        }
    }).catch(error => {
        console.error('Health check failed:', error);
    });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('[DOMContentLoaded] Event fired - initializing app');
    initApp();

    // Expose update function to window for manual testing
    window.testUpdateLabels = function(templateName) {
        console.log(`[testUpdateLabels] Manually testing with: ${templateName}`);
        updatePackChannelLabels(templateName);
    };
    console.log('[DOMContentLoaded] Exposed testUpdateLabels to window.testUpdateLabels()');
});
