// Builder JavaScript for MiabeSite

class SiteBuilder {
    constructor() {
        this.currentSiteId = null;
        this.currentStep = 1;
        this.siteData = {
            template: null,
            content: {},
            style: {},
            settings: {}
        };
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadFromStorage();
        this.updateProgress();
    }
    
    bindEvents() {
        // Navigation
        document.querySelectorAll('.wizard-next').forEach(btn => {
            btn.addEventListener('click', () => this.nextStep());
        });
        
        document.querySelectorAll('.wizard-prev').forEach(btn => {
            btn.addEventListener('click', () => this.previousStep());
        });
        
        // Template selection
        document.querySelectorAll('.template-card').forEach(card => {
            card.addEventListener('click', () => this.selectTemplate(card));
        });
        
        // Content editing
        document.querySelectorAll('.editable').forEach(element => {
            element.addEventListener('blur', () => this.saveContent());
        });
        
        // Style controls
        document.querySelectorAll('.style-control').forEach(control => {
            control.addEventListener('change', () => this.updateStyle());
        });
        
        // Auto-save
        this.setupAutoSave();
    }
    
    selectTemplate(card) {
        // Remove selected class from all cards
        document.querySelectorAll('.template-card').forEach(c => {
            c.classList.remove('selected');
        });
        
        // Add selected class to clicked card
        card.classList.add('selected');
        
        const templateId = card.dataset.templateId;
        this.siteData.template = templateId;
        
        this.saveToStorage();
        this.showNotification('Template sélectionné avec succès', 'success');
    }
    
    nextStep() {
        if (this.validateCurrentStep()) {
            this.currentStep++;
            this.updateProgress();
            this.saveToStorage();
            this.navigateToStep(this.currentStep);
        }
    }
    
    previousStep() {
        this.currentStep--;
        this.updateProgress();
        this.saveToStorage();
        this.navigateToStep(this.currentStep);
    }
    
    navigateToStep(step) {
        const url = `/builder/${this.currentSiteId}/step${step}`;
        window.location.href = url;
    }
    
    validateCurrentStep() {
        switch (this.currentStep) {
            case 1:
                if (!this.siteData.template) {
                    this.showNotification('Veuillez sélectionner un template', 'warning');
                    return false;
                }
                break;
            case 2:
                if (!this.validateContent()) {
                    this.showNotification('Veuillez remplir tous les champs obligatoires', 'warning');
                    return false;
                }
                break;
        }
        return true;
    }
    
    validateContent() {
        // Basic content validation
        const requiredFields = document.querySelectorAll('[data-required="true"]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    }
    
    updateProgress() {
        const progressBar = document.querySelector('.progress-bar');
        if (progressBar) {
            const progress = (this.currentStep / 4) * 100;
            progressBar.style.width = `${progress}%`;
        }
        
        // Update step icons
        document.querySelectorAll('.step-icon').forEach((icon, index) => {
            const stepNumber = index + 1;
            if (stepNumber <= this.currentStep) {
                icon.classList.add('bg-primary', 'text-white');
                icon.classList.remove('bg-light', 'text-muted');
            } else {
                icon.classList.remove('bg-primary', 'text-white');
                icon.classList.add('bg-light', 'text-muted');
            }
        });
    }
    
    async saveContent() {
        if (!this.currentSiteId) return;
        
        const content = this.collectContent();
        
        try {
            const response = await window.MiabeSite.ajaxRequest(
                `/api/sites/${this.currentSiteId}/content`,
                {
                    method: 'POST',
                    body: JSON.stringify(content)
                }
            );
            
            if (response.success) {
                this.showNotification('Contenu sauvegardé', 'success');
            }
        } catch (error) {
            console.error('Error saving content:', error);
        }
    }
    
    collectContent() {
        const content = {};
        
        document.querySelectorAll('.editable').forEach(element => {
            const key = element.dataset.field;
            if (key) {
                content[key] = element.value || element.innerHTML;
            }
        });
        
        return content;
    }
    
    updateStyle() {
        const style = {};
        
        document.querySelectorAll('.style-control').forEach(control => {
            const property = control.dataset.property;
            if (property) {
                style[property] = control.value;
            }
        });
        
        this.siteData.style = style;
        this.applyStyle(style);
        this.saveToStorage();
    }
    
    applyStyle(style) {
        const preview = document.getElementById('live-preview');
        if (preview) {
            Object.entries(style).forEach(([property, value]) => {
                preview.style[property] = value;
            });
        }
    }
    
    setupAutoSave() {
        // Auto-save content every 30 seconds
        setInterval(() => {
            if (this.currentStep === 2) {
                this.saveContent();
            }
        }, 30000);
        
        // Auto-save on page unload
        window.addEventListener('beforeunload', (e) => {
            if (this.hasUnsavedChanges()) {
                e.preventDefault();
                e.returnValue = 'Vous avez des modifications non sauvegardées. Êtes-vous sûr de vouloir quitter ?';
            }
        });
    }
    
    hasUnsavedChanges() {
        // Implement logic to check for unsaved changes
        return false;
    }
    
    saveToStorage() {
        window.MiabeSite.storage.set(`site_builder_${this.currentSiteId}`, {
            currentStep: this.currentStep,
            siteData: this.siteData
        });
    }
    
    loadFromStorage() {
        const saved = window.MiabeSite.storage.get(`site_builder_${this.currentSiteId}`);
        if (saved) {
            this.currentStep = saved.currentStep || 1;
            this.siteData = { ...this.siteData, ...saved.siteData };
        }
    }
    
    showNotification(message, type = 'info') {
        window.MiabeSite.showNotification(message, type);
    }
    
    // Image upload handler
    async uploadImage(file, callback) {
        const formData = new FormData();
        formData.append('image', file);
        
        try {
            const response = await fetch(`/api/sites/${this.currentSiteId}/upload`, {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                callback(data.url);
            } else {
                throw new Error(data.error || 'Erreur lors du téléchargement');
            }
        } catch (error) {
            this.showNotification(error.message, 'danger');
        }
    }
    
    // Preview site
    previewSite() {
        if (this.currentSiteId) {
            window.open(`/preview/${this.currentSiteId}`, '_blank');
        }
    }
    
    // Publish site
    async publishSite() {
        if (!this.currentSiteId) return;
        
        try {
            const response = await window.MiabeSite.ajaxRequest(
                `/builder/${this.currentSiteId}/publish`,
                {
                    method: 'POST'
                }
            );
            
            if (response.success) {
                this.showNotification('Site publié avec succès!', 'success');
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 2000);
            }
        } catch (error) {
            console.error('Error publishing site:', error);
        }
    }
}

// Initialize builder when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.siteBuilder = new SiteBuilder();
    
    // Handle image uploads
    const imageUploads = document.querySelectorAll('.image-upload');
    imageUploads.forEach(upload => {
        upload.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                window.siteBuilder.uploadImage(file, (url) => {
                    const preview = this.parentElement.querySelector('.image-preview');
                    if (preview) {
                        preview.src = url;
                        preview.style.display = 'block';
                    }
                });
            }
        });
    });
    
    // Color picker initialization
    const colorPickers = document.querySelectorAll('.color-picker');
    colorPickers.forEach(picker => {
        picker.addEventListener('change', function() {
            const target = document.querySelector(this.dataset.target);
            if (target) {
                target.style.color = this.value;
            }
        });
    });
    
    // Font selector
    const fontSelectors = document.querySelectorAll('.font-selector');
    fontSelectors.forEach(selector => {
        selector.addEventListener('change', function() {
            const target = document.querySelector(this.dataset.target);
            if (target) {
                target.style.fontFamily = this.value;
            }
        });
    });
});