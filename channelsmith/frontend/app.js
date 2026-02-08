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
    zoneElement.style.borderColor = '#14b8a6';
    zoneElement.style.backgroundColor = 'rgba(13, 115, 119, 0.1)';

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
    }

    // Update pack button ready state if at least one channel is selected
    updatePackButtonState();
}

function displayImagePreview(file, canvas) {
    const ctx = canvas.getContext('2d');
    const img = new Image();

    img.onload = () => {
        // Clear canvas with checkerboard
        ctx.fillStyle = '#1a1a1a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw checkerboard pattern
        for (let i = 0; i < canvas.width; i += 20) {
            for (let j = 0; j < canvas.height; j += 20) {
                if ((i / 20 + j / 20) % 2 === 0) {
                    ctx.fillStyle = '#2d2d2d';
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

        // Clear preview canvas
        const previewId = `preview-${channel.split('_')[0]}`;
        const previewCanvas = document.getElementById(previewId);
        if (previewCanvas) {
            const ctx = previewCanvas.getContext('2d');
            ctx.fillStyle = '#1a1a1a';
            ctx.fillRect(0, 0, previewCanvas.width, previewCanvas.height);
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

    for (const [channelPos, base64Data] of Object.entries(channels)) {
        const info = channelLabels[channelPos] || { label: channelPos, color: 'bg-gray-600' };

        const card = document.createElement('div');
        card.className = 'preview-card';
        card.innerHTML = `
            <div class="flex justify-between items-start mb-3">
                <div class="preview-label">${info.label}</div>
                <button class="btn-secondary text-xs py-1 px-2" onclick="downloadChannel('${channelPos}', '${base64Data}')">
                    📥 Download
                </button>
            </div>
            <img src="${base64Data}" class="w-full rounded-lg" style="image-rendering: pixelated;">
        `;

        resultsContainer.appendChild(card);
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

    function updateFeedback(file) {
        state.unpackImage = file;
        zone.style.borderColor = '#14b8a6';
        zone.style.backgroundColor = 'rgba(13, 115, 119, 0.1)';
        filenameSpan.textContent = file.name;
        feedback.classList.remove('hidden');

        // Make unpack button green and add vibration animation
        unpackButton.classList.add('ready', 'vibrate');

        // Remove vibration animation after it completes
        setTimeout(() => {
            unpackButton.classList.remove('vibrate');
        }, 600);
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
}

function initApp() {
    // Setup tab switching
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.addEventListener('click', () => {
            if (btn.dataset.tab) {
                switchTab(btn.dataset.tab);
            }
        });
    });

    // Setup Info button
    const infoButton = document.getElementById('info-button');
    if (infoButton) {
        infoButton.addEventListener('click', () => {
            window.open('https://github.com/cgCrate/ChannelSmith', '_blank');
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

    // Set default template to 'Free'
    const packTemplateSelect = document.getElementById('pack-template');
    if (packTemplateSelect) {
        packTemplateSelect.value = 'Free';
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
document.addEventListener('DOMContentLoaded', initApp);
