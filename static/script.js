// static/script.js - Complete JavaScript for Fake News Detection System

// Global Variables
let currentUser = null;
let charts = {};

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Fake News Detector Initialized');
    
    // Initialize all components
    initializeTooltips();
    initializeFormValidation();
    initializeModalHandlers();
    initializeAutoSave();
    initializeRealTimeValidation();
    
    // Load user preferences
    loadUserPreferences();
    
    // Setup CSRF protection
    setupCSRFProtection();
});

// ==================== TOOLTIP FUNCTIONS ====================
function initializeTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.textContent = e.target.getAttribute('data-tooltip');
    tooltip.style.position = 'absolute';
    tooltip.style.background = '#333';
    tooltip.style.color = 'white';
    tooltip.style.padding = '5px 10px';
    tooltip.style.borderRadius = '5px';
    tooltip.style.fontSize = '12px';
    tooltip.style.zIndex = '1000';
    tooltip.style.top = (e.pageY - 30) + 'px';
    tooltip.style.left = e.pageX + 'px';
    document.body.appendChild(tooltip);
    e.target._tooltip = tooltip;
}

function hideTooltip(e) {
    if (e.target._tooltip) {
        e.target._tooltip.remove();
    }
}

// ==================== FORM VALIDATION ====================
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', validateForm);
    });
}

function validateForm(e) {
    const form = e.target;
    const inputs = form.querySelectorAll('input[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            showError(input, 'This field is required');
            isValid = false;
        } else {
            clearError(input);
        }
        
        // Email validation
        if (input.type === 'email' && input.value) {
            if (!isValidEmail(input.value)) {
                showError(input, 'Please enter a valid email address');
                isValid = false;
            }
        }
        
        // Password validation
        if (input.type === 'password' && input.value) {
            if (input.value.length < 6) {
                showError(input, 'Password must be at least 6 characters');
                isValid = false;
            }
        }
    });
    
    // Password match validation
    const password = form.querySelector('#password');
    const confirmPassword = form.querySelector('#confirm_password');
    if (password && confirmPassword && password.value !== confirmPassword.value) {
        showError(confirmPassword, 'Passwords do not match');
        isValid = false;
    }
    
    if (!isValid) {
        e.preventDefault();
    }
}

function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showError(input, message) {
    const formGroup = input.closest('.form-group');
    if (formGroup) {
        const error = formGroup.querySelector('.error-message') || document.createElement('div');
        error.className = 'error-message';
        error.style.color = '#dc3545';
        error.style.fontSize = '12px';
        error.style.marginTop = '5px';
        error.textContent = message;
        if (!formGroup.querySelector('.error-message')) {
            formGroup.appendChild(error);
        }
        input.style.borderColor = '#dc3545';
    }
}

function clearError(input) {
    const formGroup = input.closest('.form-group');
    if (formGroup) {
        const error = formGroup.querySelector('.error-message');
        if (error) {
            error.remove();
        }
        input.style.borderColor = '#e0e0e0';
    }
}

// ==================== MODAL HANDLERS ====================
function initializeModalHandlers() {
    const modals = document.querySelectorAll('.modal');
    const closeButtons = document.querySelectorAll('.close');
    
    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            const modal = button.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
            }
        });
    });
    
    window.addEventListener('click', (e) => {
        modals.forEach(modal => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
}

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// ==================== AUTO-SAVE FUNCTIONALITY ====================
function initializeAutoSave() {
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        const key = `autosave_${textarea.id || 'news_text'}`;
        
        // Load saved data
        const saved = localStorage.getItem(key);
        if (saved && !textarea.value) {
            textarea.value = saved;
        }
        
        // Save on input
        textarea.addEventListener('input', debounce(() => {
            localStorage.setItem(key, textarea.value);
            showNotification('Draft saved', 'success');
        }, 1000));
    });
}

// ==================== REAL-TIME VALIDATION ====================
function initializeRealTimeValidation() {
    const inputs = document.querySelectorAll('input, textarea');
    inputs.forEach(input => {
        input.addEventListener('input', () => {
            if (input.value.trim()) {
                clearError(input);
            }
        });
    });
}

// ==================== NEWS DETECTION FUNCTIONS ====================
async function detectNews() {
    const newsText = document.getElementById('news_text')?.value;
    if (!newsText) {
        showNotification('Please enter some news text', 'warning');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/api/detect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: newsText })
        });
        
        const result = await response.json();
        displayDetectionResult(result);
        saveToHistory(result);
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error analyzing news', 'danger');
    } finally {
        hideLoading();
    }
}

function displayDetectionResult(result) {
    const resultDiv = document.getElementById('result-container');
    if (!resultDiv) return;
    
    const resultClass = result.prediction === 'Real' ? 'result-real' : 'result-fake';
    const confidence = (result.confidence || 75).toFixed(1);
    
    resultDiv.innerHTML = `
        <div class="${resultClass}">
            <h3>Analysis Result</h3>
            <p><strong>Prediction:</strong> ${result.prediction} News</p>
            <p><strong>Confidence:</strong> ${confidence}%</p>
            
            <div class="progress">
                <div class="progress-bar progress-real" style="width: ${result.real_probability * 100 || 50}%">
                    Real: ${((result.real_probability || 0.5) * 100).toFixed(1)}%
                </div>
                <div class="progress-bar progress-fake" style="width: ${result.fake_probability * 100 || 50}%">
                    Fake: ${((result.fake_probability || 0.5) * 100).toFixed(1)}%
                </div>
            </div>
            
            <button onclick="shareResult('${result.prediction}', ${confidence})" class="btn btn-info">
                Share Result
            </button>
        </div>
    `;
    
    resultDiv.style.display = 'block';
    resultDiv.scrollIntoView({ behavior: 'smooth' });
}

// ==================== FACT CHECK FUNCTIONS ====================
async function factCheck() {
    const claim = document.getElementById('claim')?.value;
    if (!claim) {
        showNotification('Please enter a claim to fact-check', 'warning');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/api/fact-check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ claim: claim })
        });
        
        const result = await response.json();
        displayFactCheckResult(result);
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error fact-checking claim', 'danger');
    } finally {
        hideLoading();
    }
}

function displayFactCheckResult(result) {
    const resultDiv = document.getElementById('fact-check-result');
    if (!resultDiv) return;
    
    const verdictClass = result.verdict === 'True' ? 'success' : 
                        result.verdict === 'False' ? 'danger' : 'warning';
    
    resultDiv.innerHTML = `
        <div class="alert alert-${verdictClass}">
            <h4>Verdict: ${result.verdict}</h4>
            <p><strong>Confidence:</strong> ${result.confidence}%</p>
            <p>${result.explanation || 'Analysis complete'}</p>
            
            <h5>Sources:</h5>
            <ul>
                ${result.sources ? result.sources.map(s => `<li><a href="${s.url}" target="_blank">${s.name}</a></li>`).join('') : '<li>No sources available</li>'}
            </ul>
        </div>
    `;
    
    resultDiv.style.display = 'block';
}

// ==================== CHART FUNCTIONS ====================
function createDetectionChart(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !window.Chart) return;
    
    const ctx = canvas.getContext('2d');
    
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }
    
    charts[canvasId] = new Chart(ctx, {
        type: data.type || 'doughnut',
        data: {
            labels: data.labels || ['Real News', 'Fake News'],
            datasets: [{
                data: data.values || [50, 50],
                backgroundColor: ['#28a745', '#dc3545'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            return `${label}: ${value.toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    });
}

// ==================== HISTORY FUNCTIONS ====================
function saveToHistory(result) {
    let history = JSON.parse(localStorage.getItem('detection_history') || '[]');
    history.unshift({
        timestamp: new Date().toISOString(),
        prediction: result.prediction,
        confidence: result.confidence,
        text: result.text?.substring(0, 100)
    });
    
    // Keep only last 50 items
    history = history.slice(0, 50);
    localStorage.setItem('detection_history', JSON.stringify(history));
    updateHistoryDisplay();
}

function updateHistoryDisplay() {
    const historyContainer = document.getElementById('history-container');
    if (!historyContainer) return;
    
    const history = JSON.parse(localStorage.getItem('detection_history') || '[]');
    
    if (history.length === 0) {
        historyContainer.innerHTML = '<p>No history yet. Start detecting!</p>';
        return;
    }
    
    historyContainer.innerHTML = history.map(item => `
        <div class="list-group-item">
            <div class="d-flex justify-content-between">
                <strong class="badge badge-${item.prediction === 'Real' ? 'success' : 'danger'}">
                    ${item.prediction}
                </strong>
                <small>${new Date(item.timestamp).toLocaleString()}</small>
            </div>
            <p class="mt-2">${item.text || 'No text available'}</p>
            <small>Confidence: ${item.confidence}%</small>
        </div>
    `).join('');
}

// ==================== NOTIFICATION FUNCTIONS ====================
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.maxWidth = '300px';
    notification.style.animation = 'slideIn 0.3s ease';
    notification.innerHTML = `
        <strong>${type.toUpperCase()}</strong>
        <p>${message}</p>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ==================== LOADING FUNCTIONS ====================
function showLoading() {
    const loader = document.createElement('div');
    loader.id = 'global-loader';
    loader.style.position = 'fixed';
    loader.style.top = '0';
    loader.style.left = '0';
    loader.style.width = '100%';
    loader.style.height = '100%';
    loader.style.backgroundColor = 'rgba(0,0,0,0.5)';
    loader.style.zIndex = '9998';
    loader.style.display = 'flex';
    loader.style.justifyContent = 'center';
    loader.style.alignItems = 'center';
    loader.innerHTML = '<div class="spinner"></div>';
    document.body.appendChild(loader);
}

function hideLoading() {
    const loader = document.getElementById('global-loader');
    if (loader) {
        loader.remove();
    }
}

// ==================== SHARE FUNCTIONS ====================
function shareResult(prediction, confidence) {
    const text = `I just analyzed a news article using FakeNewsDetector! Result: ${prediction} News with ${confidence}% confidence. #FakeNewsDetection`;
    
    if (navigator.share) {
        navigator.share({
            title: 'Fake News Detection Result',
            text: text,
        }).catch(console.error);
    } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Result copied to clipboard!', 'success');
        });
    }
}

// ==================== USER PREFERENCES ====================
function loadUserPreferences() {
    const theme = localStorage.getItem('theme');
    if (theme === 'dark') {
        document.body.classList.add('dark-mode');
    }
}

function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    showNotification(`Theme changed to ${isDark ? 'dark' : 'light'} mode`, 'info');
}

// ==================== UTILITY FUNCTIONS ====================
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function setupCSRFProtection() {
    const token = document.querySelector('meta[name="csrf-token"]')?.content;
    if (token) {
        fetch('/api/csrf-token', {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        }).catch(console.error);
    }
}

// ==================== EVENT LISTENERS ====================
// Listen for detection form submission
document.addEventListener('submit', function(e) {
    if (e.target.id === 'detect-form') {
        e.preventDefault();
        detectNews();
    }
    
    if (e.target.id === 'fact-check-form') {
        e.preventDefault();
        factCheck();
    }
});

// ==================== EXPORT FUNCTIONS (for debugging) ====================
window.fakeNewsDetector = {
    detectNews,
    factCheck,
    showNotification,
    toggleTheme,
    clearHistory: () => {
        localStorage.removeItem('detection_history');
        updateHistoryDisplay();
        showNotification('History cleared', 'success');
    }
};

console.log('Fake News Detector JavaScript Loaded');
console.log('Available functions:', Object.keys(window.fakeNewsDetector));