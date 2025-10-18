// AI Recipe Shoplist Crawler - Frontend JavaScript

class RecipeShoplistApp {
    constructor() {
        this.apiBase = '/api';
        this.currentRecipe = null;
        this.currentOptimization = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkUrlParams();
    }

    setupEventListeners() {
        // Recipe form submission
        const form = document.getElementById('recipeForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleRecipeSubmit(e));
        }

        // Demo button
        window.loadDemo = () => this.loadDemo();
    }

    checkUrlParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const demoParam = urlParams.get('demo');
        if (demoParam === 'true') {
            this.loadDemo();
        }
    }

    async handleRecipeSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const url = formData.get('url');
        
        if (!url) {
            this.showError('Please enter a recipe URL');
            return;
        }

        await this.processRecipe(url);
    }

    async processRecipe(url) {
        try {
            this.showLoading('Processing recipe and optimizing shopping...');
            this.hideResults();

            // Call the complete optimization endpoint
            const response = await fetch(`${this.apiBase}/optimize-shopping`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `recipe_url=${encodeURIComponent(url)}`
            });

            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || 'Failed to process recipe');
            }

            this.currentRecipe = result.data.recipe;
            this.currentOptimization = result.data.optimization;

            this.displayResults(result.data);
            this.hideLoading();

        } catch (error) {
            console.error('Error processing recipe:', error);
            this.showError(`Error: ${error.message}`);
            this.hideLoading();
        }
    }

    async loadDemo() {
        try {
            this.showLoading('Loading demo recipe...');

            // Load demo recipe
            const demoResponse = await fetch(`${this.apiBase}/demo`);
            const demoResult = await demoResponse.json();

            if (!demoResult.success) {
                throw new Error('Failed to load demo');
            }

            // Set demo URL in form
            const urlInput = document.getElementById('recipeUrl');
            if (urlInput) {
                urlInput.value = demoResult.data.recipe.url;
            }

            // Process the demo recipe
            await this.processRecipe(demoResult.data.recipe.url);

        } catch (error) {
            console.error('Error loading demo:', error);
            this.showError(`Demo error: ${error.message}`);
            this.hideLoading();
        }
    }

    displayResults(data) {
        const resultsSection = document.getElementById('resultsSection');
        const resultsContent = document.getElementById('resultsContent');

        if (!resultsSection || !resultsContent) return;

        const recipe = data.recipe;
        const optimization = data.optimization;
        const summary = data.summary;

        const html = `
            <!-- Recipe Information -->
            <div class="recipe-card fade-in">
                <div class="recipe-title">
                    <i class="fas fa-utensils me-2"></i>
                    ${recipe.title}
                </div>
                <div class="recipe-meta">
                    ${recipe.servings ? `<div class="meta-item"><i class="fas fa-users"></i> ${recipe.servings} servings</div>` : ''}
                    ${recipe.prep_time ? `<div class="meta-item"><i class="fas fa-clock"></i> ${recipe.prep_time}</div>` : ''}
                    ${recipe.cook_time ? `<div class="meta-item"><i class="fas fa-fire"></i> ${recipe.cook_time}</div>` : ''}
                </div>
                ${recipe.description ? `<p>${recipe.description}</p>` : ''}
            </div>

            <!-- Optimization Summary -->
            <div class="optimization-summary fade-in">
                <h4 class="mb-3">
                    <i class="fas fa-chart-line me-2"></i>
                    Optimization Results
                </h4>
                <div class="summary-stats">
                    <div class="stat-item">
                        <span class="stat-value">$${summary.total_cost.toFixed(2)}</span>
                        <span class="stat-label">Total Cost</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">${summary.stores_count}</span>
                        <span class="stat-label">Stores</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">${summary.items_found}/${summary.items_total}</span>
                        <span class="stat-label">Items Found</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">$${summary.savings.toFixed(2)}</span>
                        <span class="stat-label">Savings</span>
                    </div>
                </div>
            </div>

            <!-- Ingredients Grid -->
            <div class="mb-4">
                <h5 class="mb-3">
                    <i class="fas fa-shopping-basket me-2"></i>
                    Shopping List
                </h5>
                <div class="ingredients-grid">
                    ${this.renderIngredients(optimization.items)}
                </div>
            </div>

            <!-- Store Breakdown -->
            <div class="stores-breakdown">
                <h6 class="mb-3">
                    <i class="fas fa-store me-2"></i>
                    Store Breakdown
                </h6>
                ${this.renderStoreBreakdown(optimization.stores_breakdown)}
            </div>

            <!-- Action Buttons -->
            <div class="bill-actions">
                <button class="btn btn-success" onclick="app.generateBill('pdf')">
                    <i class="fas fa-file-pdf me-1"></i>
                    Generate PDF Bill
                </button>
                <button class="btn btn-outline-success" onclick="app.generateBill('html')">
                    <i class="fas fa-file-code me-1"></i>
                    Generate HTML Bill
                </button>
                <button class="btn btn-outline-primary" onclick="app.downloadJSON()">
                    <i class="fas fa-download me-1"></i>
                    Download JSON
                </button>
            </div>
        `;

        resultsContent.innerHTML = html;
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    renderIngredients(items) {
        return items.map(item => {
            const ingredient = item.ingredient;
            const product = item.selected_product;
            const quantityText = ingredient.quantity ? 
                `${ingredient.quantity} ${ingredient.unit || ''}`.trim() : 
                'As needed';

            if (product) {
                return `
                    <div class="ingredient-item">
                        <div class="ingredient-icon">
                            <i class="fas fa-check"></i>
                        </div>
                        <div class="ingredient-details flex-grow-1">
                            <h6>${ingredient.name}</h6>
                            <div class="ingredient-quantity">${quantityText}</div>
                            <small class="text-muted">
                                ${product.store} - ${product.title} - $${product.price.toFixed(2)}
                            </small>
                        </div>
                        <div class="text-end">
                            <strong class="text-success">$${(item.estimated_cost || 0).toFixed(2)}</strong>
                        </div>
                    </div>
                `;
            } else {
                return `
                    <div class="ingredient-item">
                        <div class="ingredient-icon bg-warning">
                            <i class="fas fa-exclamation"></i>
                        </div>
                        <div class="ingredient-details flex-grow-1">
                            <h6>${ingredient.name}</h6>
                            <div class="ingredient-quantity">${quantityText}</div>
                            <small class="text-danger">Not found in stores</small>
                        </div>
                        <div class="text-end">
                            <span class="text-muted">-</span>
                        </div>
                    </div>
                `;
            }
        }).join('');
    }

    renderStoreBreakdown(breakdown) {
        return Object.entries(breakdown).map(([store, cost]) => `
            <div class="store-item">
                <span class="store-name">
                    <i class="fas fa-${store === 'travel' ? 'car' : 'store'} me-2"></i>
                    ${store === 'travel' ? 'Travel Costs' : store.charAt(0).toUpperCase() + store.slice(1)}
                </span>
                <span class="store-cost">$${cost.toFixed(2)}</span>
            </div>
        `).join('');
    }

    async generateBill(format) {
        if (!this.currentRecipe) {
            this.showError('No recipe loaded');
            return;
        }

        try {
            this.showLoading(`Generating ${format.toUpperCase()} bill...`);

            const response = await fetch(`${this.apiBase}/generate-bill`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `recipe_url=${encodeURIComponent(this.currentRecipe.url)}&format=${format}`
            });

            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || 'Failed to generate bill');
            }

            // Download the bill
            const downloadUrl = result.data.download_url;
            window.open(downloadUrl, '_blank');

            this.showSuccess(`${format.toUpperCase()} bill generated successfully!`);
            this.hideLoading();

        } catch (error) {
            console.error('Error generating bill:', error);
            this.showError(`Error generating bill: ${error.message}`);
            this.hideLoading();
        }
    }

    async downloadJSON() {
        if (!this.currentOptimization) {
            this.showError('No optimization data available');
            return;
        }

        const data = {
            recipe: this.currentRecipe,
            optimization: this.currentOptimization,
            generated_at: new Date().toISOString()
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], {
            type: 'application/json'
        });

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `recipe_optimization_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showSuccess('JSON data downloaded successfully!');
    }

    showLoading(text = 'Loading...') {
        const loadingSection = document.getElementById('loadingSection');
        const loadingText = document.getElementById('loadingText');

        if (loadingText) {
            loadingText.textContent = text;
        }

        if (loadingSection) {
            loadingSection.style.display = 'block';
        }
    }

    hideLoading() {
        const loadingSection = document.getElementById('loadingSection');
        if (loadingSection) {
            loadingSection.style.display = 'none';
        }
    }

    showResults() {
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.style.display = 'block';
        }
    }

    hideResults() {
        const resultsSection = document.getElementById('resultsSection');
        if (resultsSection) {
            resultsSection.style.display = 'none';
        }
    }

    showError(message) {
        this.showAlert(message, 'danger');
    }

    showSuccess(message) {
        this.showAlert(message, 'success');
    }

    showAlert(message, type = 'info') {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert-message');
        existingAlerts.forEach(alert => alert.remove());

        // Create new alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show alert-message`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert after the main card
        const mainCard = document.querySelector('.card');
        if (mainCard) {
            mainCard.parentNode.insertBefore(alertDiv, mainCard.nextSibling);
        }

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new RecipeShoplistApp();
});

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-AU', {
        style: 'currency',
        currency: 'AUD'
    }).format(amount);
}

function formatTime(seconds) {
    if (seconds < 60) {
        return `${seconds.toFixed(1)}s`;
    } else {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
    }
}