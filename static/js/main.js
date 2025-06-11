/**
 * Arabic Sign Language Translator - Main JavaScript
 * Handles global functionality, UI interactions, and utility functions
 */

// Global variables
let currentLanguage = 'ar';
let isRTL = true;
let debugMode = false;

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    handleResponsiveDesign();
    initializeAnimations();
});

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('Initializing Arabic Sign Language Translator...');
    
    // Check for debug mode
    debugMode = new URLSearchParams(window.location.search).get('debug') === 'true';
    
    // Set up language and direction
    setupLanguageAndDirection();
    
    // Initialize UI components
    initializeUIComponents();
    
    // Set up accessibility features
    setupAccessibility();
    
    // Initialize performance monitoring
    initializePerformanceMonitoring();
    
    console.log('Application initialized successfully');
}

/**
 * Set up language and RTL direction
 */
function setupLanguageAndDirection() {
    const html = document.documentElement;
    html.setAttribute('lang', currentLanguage);
    html.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
    
    // Add RTL class to body for styling
    if (isRTL) {
        document.body.classList.add('rtl');
    }
}

/**
 * Initialize UI components
 */
function initializeUIComponents() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize popovers
    initializePopovers();
    
    // Initialize modals
    initializeModals();
    
    // Set up form enhancements
    setupFormEnhancements();
    
    // Initialize notifications
    initializeNotifications();
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            placement: isRTL ? 'left' : 'right',
            trigger: 'hover focus'
        });
    });
}

/**
 * Initialize Bootstrap popovers
 */
function initializePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl, {
            placement: isRTL ? 'left' : 'right',
            trigger: 'click'
        });
    });
}

/**
 * Initialize modal components
 */
function initializeModals() {
    // Auto-focus on modal open
    document.addEventListener('shown.bs.modal', function(event) {
        const modal = event.target;
        const autofocusElement = modal.querySelector('[autofocus]');
        if (autofocusElement) {
            autofocusElement.focus();
        }
    });
    
    // Clear form data on modal close
    document.addEventListener('hidden.bs.modal', function(event) {
        const modal = event.target;
        const forms = modal.querySelectorAll('form');
        forms.forEach(form => {
            if (form.hasAttribute('data-clear-on-close')) {
                form.reset();
                clearFormValidation(form);
            }
        });
    });
}

/**
 * Set up form enhancements
 */
function setupFormEnhancements() {
    // Add floating label effect
    setupFloatingLabels();
    
    // Add form validation
    setupFormValidation();
    
    // Add input masks
    setupInputMasks();
    
    // Add character counters
    setupCharacterCounters();
}

/**
 * Set up floating label effect
 */
function setupFloatingLabels() {
    const inputs = document.querySelectorAll('.form-floating input, .form-floating textarea');
    
    inputs.forEach(input => {
        // Check if input has value on load
        if (input.value) {
            input.classList.add('has-value');
        }
        
        // Add event listeners
        input.addEventListener('input', function() {
            if (this.value) {
                this.classList.add('has-value');
            } else {
                this.classList.remove('has-value');
            }
        });
        
        input.addEventListener('focus', function() {
            this.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.classList.remove('focused');
        });
    });
}

/**
 * Set up form validation
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
            
            form.classList.add('was-validated');
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateField(this);
                }
            });
        });
    });
}

/**
 * Validate individual form field
 */
function validateField(field) {
    const isValid = field.checkValidity();
    
    field.classList.remove('is-valid', 'is-invalid');
    field.classList.add(isValid ? 'is-valid' : 'is-invalid');
    
    // Update custom validation message
    const feedback = field.parentNode.querySelector('.invalid-feedback');
    if (feedback && !isValid) {
        feedback.textContent = getCustomValidationMessage(field);
    }
    
    return isValid;
}

/**
 * Get custom validation message in Arabic
 */
function getCustomValidationMessage(field) {
    const validity = field.validity;
    const fieldName = field.getAttribute('data-field-name') || 'هذا الحقل';
    
    if (validity.valueMissing) {
        return `${fieldName} مطلوب`;
    }
    if (validity.typeMismatch) {
        if (field.type === 'email') {
            return 'يرجى إدخال بريد إلكتروني صحيح';
        }
        if (field.type === 'url') {
            return 'يرجى إدخال رابط صحيح';
        }
    }
    if (validity.tooShort) {
        return `يجب أن يكون ${fieldName} ${field.minLength} أحرف على الأقل`;
    }
    if (validity.tooLong) {
        return `يجب أن يكون ${fieldName} ${field.maxLength} أحرف كحد أقصى`;
    }
    if (validity.rangeUnderflow) {
        return `يجب أن يكون ${fieldName} ${field.min} أو أكثر`;
    }
    if (validity.rangeOverflow) {
        return `يجب أن يكون ${fieldName} ${field.max} أو أقل`;
    }
    if (validity.patternMismatch) {
        return `${fieldName} غير صحيح`;
    }
    
    return 'يرجى إدخال قيمة صحيحة';
}

/**
 * Clear form validation
 */
function clearFormValidation(form) {
    form.classList.remove('was-validated');
    const fields = form.querySelectorAll('.is-valid, .is-invalid');
    fields.forEach(field => {
        field.classList.remove('is-valid', 'is-invalid');
    });
}

/**
 * Set up input masks
 */
function setupInputMasks() {
    // Phone number mask
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function() {
            let value = this.value.replace(/\D/g, '');
            if (value.length >= 10) {
                value = value.replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3');
            }
            this.value = value;
        });
    });
}

/**
 * Set up character counters
 */
function setupCharacterCounters() {
    const textareas = document.querySelectorAll('textarea[maxlength]');
    
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        const counter = document.createElement('small');
        counter.className = 'character-counter text-muted';
        counter.textContent = `0 / ${maxLength}`;
        
        textarea.parentNode.appendChild(counter);
        
        textarea.addEventListener('input', function() {
            const currentLength = this.value.length;
            counter.textContent = `${currentLength} / ${maxLength}`;
            
            if (currentLength > maxLength * 0.9) {
                counter.classList.add('text-warning');
            } else {
                counter.classList.remove('text-warning');
            }
            
            if (currentLength >= maxLength) {
                counter.classList.add('text-danger');
            } else {
                counter.classList.remove('text-danger');
            }
        });
    });
}

/**
 * Set up global event listeners
 */
function setupEventListeners() {
    // Handle navigation menu toggle
    setupNavigationEvents();
    
    // Handle search functionality
    setupSearchEvents();
    
    // Handle theme switching
    setupThemeEvents();
    
    // Handle keyboard shortcuts
    setupKeyboardShortcuts();
    
    // Handle window events
    setupWindowEvents();
}

/**
 * Set up navigation events
 */
function setupNavigationEvents() {
    // Mobile menu toggle
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!navbarToggler.contains(event.target) && !navbarCollapse.contains(event.target)) {
                navbarCollapse.classList.remove('show');
            }
        });
    }
    
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Set up search events
 */
function setupSearchEvents() {
    const searchInputs = document.querySelectorAll('input[type="search"]');
    
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value);
            }, 300);
        });
        
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                this.value = '';
                performSearch('');
            }
        });
    });
}

/**
 * Perform search functionality
 */
function performSearch(query) {
    if (debugMode) {
        console.log('Searching for:', query);
    }
    
    // Implement search logic here
    // This would typically make an API call or filter displayed content
}

/**
 * Set up theme events
 */
function setupThemeEvents() {
    const themeToggle = document.querySelector('#themeToggle');
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            toggleTheme();
        });
    }
    
    // Check for saved theme preference or default to 'light'
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);
}

/**
 * Toggle between light and dark themes
 */
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    applyTheme(newTheme);
}

/**
 * Apply theme
 */
function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    // Update theme toggle button if exists
    const themeToggle = document.querySelector('#themeToggle');
    if (themeToggle) {
        const icon = themeToggle.querySelector('i');
        if (icon) {
            icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        }
    }
}

/**
 * Set up keyboard shortcuts
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.modal.show');
            if (activeModal) {
                const modalInstance = bootstrap.Modal.getInstance(activeModal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }
        }
        
        // Alt + H for help
        if (e.altKey && e.key === 'h') {
            e.preventDefault();
            showHelp();
        }
    });
}

/**
 * Set up window events
 */
function setupWindowEvents() {
    // Handle window resize
    window.addEventListener('resize', debounce(function() {
        handleWindowResize();
    }, 250));
    
    // Handle scroll events
    window.addEventListener('scroll', throttle(function() {
        handleWindowScroll();
    }, 100));
    
    // Handle page visibility changes
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'visible') {
            onPageVisible();
        } else {
            onPageHidden();
        }
    });
    
    // Handle online/offline status
    window.addEventListener('online', onOnline);
    window.addEventListener('offline', onOffline);
}

/**
 * Handle window resize
 */
function handleWindowResize() {
    // Update responsive elements
    updateResponsiveElements();
    
    // Recalculate element positions if needed
    recalculatePositions();
}

/**
 * Handle window scroll
 */
function handleWindowScroll() {
    // Update navbar on scroll
    updateNavbarOnScroll();
    
    // Show/hide scroll to top button
    updateScrollToTopButton();
    
    // Lazy load images
    lazyLoadImages();
}

/**
 * Update navbar appearance on scroll
 */
function updateNavbarOnScroll() {
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        if (window.scrollY > 100) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    }
}

/**
 * Update scroll to top button
 */
function updateScrollToTopButton() {
    const scrollToTopBtn = document.querySelector('#scrollToTop');
    if (scrollToTopBtn) {
        if (window.scrollY > 300) {
            scrollToTopBtn.style.display = 'block';
        } else {
            scrollToTopBtn.style.display = 'none';
        }
    }
}

/**
 * Lazy load images
 */
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    
    images.forEach(img => {
        if (isElementInViewport(img)) {
            img.src = img.getAttribute('data-src');
            img.removeAttribute('data-src');
            img.classList.add('loaded');
        }
    });
}

/**
 * Check if element is in viewport
 */
function isElementInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Handle responsive design
 */
function handleResponsiveDesign() {
    updateResponsiveElements();
    setupIntersectionObserver();
}

/**
 * Update responsive elements
 */
function updateResponsiveElements() {
    const screenWidth = window.innerWidth;
    
    // Update mobile-specific elements
    const mobileElements = document.querySelectorAll('.mobile-only');
    const desktopElements = document.querySelectorAll('.desktop-only');
    
    if (screenWidth < 768) {
        mobileElements.forEach(el => el.style.display = 'block');
        desktopElements.forEach(el => el.style.display = 'none');
    } else {
        mobileElements.forEach(el => el.style.display = 'none');
        desktopElements.forEach(el => el.style.display = 'block');
    }
}

/**
 * Set up intersection observer for animations
 */
function setupIntersectionObserver() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    // Observe elements with animation classes
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    animatedElements.forEach(el => observer.observe(el));
}

/**
 * Initialize animations
 */
function initializeAnimations() {
    // Add entrance animations to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in-up');
    });
    
    // Initialize text animations
    initializeTextAnimations();
    
    // Initialize counter animations
    initializeCounterAnimations();
}

/**
 * Initialize text animations
 */
function initializeTextAnimations() {
    const animatedTexts = document.querySelectorAll('.animate-text');
    
    animatedTexts.forEach(element => {
        const text = element.textContent;
        element.textContent = '';
        
        for (let i = 0; i < text.length; i++) {
            setTimeout(() => {
                element.textContent += text[i];
            }, i * 50);
        }
    });
}

/**
 * Initialize counter animations
 */
function initializeCounterAnimations() {
    const counters = document.querySelectorAll('.counter');
    
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = parseInt(counter.getAttribute('data-duration')) || 2000;
        
        animateCounter(counter, 0, target, duration);
    });
}

/**
 * Animate counter
 */
function animateCounter(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        element.textContent = Math.floor(current);
        
        if (current >= end) {
            element.textContent = end;
            clearInterval(timer);
        }
    }, 16);
}

/**
 * Set up accessibility features
 */
function setupAccessibility() {
    // Skip to main content link
    setupSkipLink();
    
    // Focus management
    setupFocusManagement();
    
    // Keyboard navigation
    setupKeyboardNavigation();
    
    // Screen reader announcements
    setupScreenReaderAnnouncements();
}

/**
 * Set up skip to main content link
 */
function setupSkipLink() {
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.className = 'skip-link sr-only-focusable';
    skipLink.textContent = 'تخطى إلى المحتوى الرئيسي';
    
    document.body.insertBefore(skipLink, document.body.firstChild);
}

/**
 * Set up focus management
 */
function setupFocusManagement() {
    // Focus trap in modals
    const modals = document.querySelectorAll('.modal');
    
    modals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            trapFocus(this);
        });
        
        modal.addEventListener('hidden.bs.modal', function() {
            releaseFocus();
        });
    });
}

/**
 * Trap focus within element
 */
function trapFocus(element) {
    const focusableElements = element.querySelectorAll(
        'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select'
    );
    
    const firstFocusableElement = focusableElements[0];
    const lastFocusableElement = focusableElements[focusableElements.length - 1];
    
    element.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            if (e.shiftKey) {
                if (document.activeElement === firstFocusableElement) {
                    lastFocusableElement.focus();
                    e.preventDefault();
                }
            } else {
                if (document.activeElement === lastFocusableElement) {
                    firstFocusableElement.focus();
                    e.preventDefault();
                }
            }
        }
    });
    
    firstFocusableElement.focus();
}

/**
 * Release focus trap
 */
function releaseFocus() {
    // Focus is automatically managed by Bootstrap modal
}

/**
 * Set up keyboard navigation
 */
function setupKeyboardNavigation() {
    // Arrow key navigation for cards/lists
    const navigableContainers = document.querySelectorAll('.keyboard-navigable');
    
    navigableContainers.forEach(container => {
        const items = container.querySelectorAll('.navigable-item');
        let currentIndex = 0;
        
        container.addEventListener('keydown', function(e) {
            switch (e.key) {
                case 'ArrowRight':
                case 'ArrowDown':
                    e.preventDefault();
                    currentIndex = (currentIndex + 1) % items.length;
                    items[currentIndex].focus();
                    break;
                    
                case 'ArrowLeft':
                case 'ArrowUp':
                    e.preventDefault();
                    currentIndex = (currentIndex - 1 + items.length) % items.length;
                    items[currentIndex].focus();
                    break;
                    
                case 'Home':
                    e.preventDefault();
                    currentIndex = 0;
                    items[currentIndex].focus();
                    break;
                    
                case 'End':
                    e.preventDefault();
                    currentIndex = items.length - 1;
                    items[currentIndex].focus();
                    break;
            }
        });
    });
}

/**
 * Set up screen reader announcements
 */
function setupScreenReaderAnnouncements() {
    // Create aria-live region for announcements
    const announcer = document.createElement('div');
    announcer.setAttribute('aria-live', 'polite');
    announcer.setAttribute('aria-atomic', 'true');
    announcer.className = 'sr-only';
    announcer.id = 'announcer';
    
    document.body.appendChild(announcer);
}

/**
 * Announce to screen readers
 */
function announceToScreenReader(message) {
    const announcer = document.getElementById('announcer');
    if (announcer) {
        announcer.textContent = message;
        
        // Clear after a delay
        setTimeout(() => {
            announcer.textContent = '';
        }, 1000);
    }
}

/**
 * Initialize performance monitoring
 */
function initializePerformanceMonitoring() {
    // Monitor page load performance
    window.addEventListener('load', function() {
        measurePageLoadPerformance();
    });
    
    // Monitor resource loading
    observeResourceLoading();
    
    // Monitor user interactions
    monitorUserInteractions();
}

/**
 * Measure page load performance
 */
function measurePageLoadPerformance() {
    if ('performance' in window) {
        const timing = performance.timing;
        const loadTime = timing.loadEventEnd - timing.navigationStart;
        
        if (debugMode) {
            console.log(`Page load time: ${loadTime}ms`);
        }
        
        // Send performance data to analytics (if implemented)
        trackPerformance('page_load', loadTime);
    }
}

/**
 * Observe resource loading
 */
function observeResourceLoading() {
    if ('PerformanceObserver' in window) {
        const observer = new PerformanceObserver((list) => {
            list.getEntries().forEach((entry) => {
                if (debugMode) {
                    console.log(`Resource: ${entry.name}, Duration: ${entry.duration}ms`);
                }
            });
        });
        
        observer.observe({ entryTypes: ['resource'] });
    }
}

/**
 * Monitor user interactions
 */
function monitorUserInteractions() {
    let interactionCount = 0;
    
    ['click', 'touch', 'keydown'].forEach(eventType => {
        document.addEventListener(eventType, function() {
            interactionCount++;
            
            if (debugMode && interactionCount % 10 === 0) {
                console.log(`User interactions: ${interactionCount}`);
            }
        });
    });
}

/**
 * Track performance metric
 */
function trackPerformance(metric, value) {
    // Implement analytics tracking here
    if (debugMode) {
        console.log(`Performance metric - ${metric}: ${value}`);
    }
}

/**
 * Initialize notifications system
 */
function initializeNotifications() {
    // Create notifications container
    const container = document.createElement('div');
    container.id = 'notifications-container';
    container.className = 'notifications-container';
    document.body.appendChild(container);
}

/**
 * Show notification
 */
function showNotification(message, type = 'info', duration = 5000) {
    const container = document.getElementById('notifications-container');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, duration);
    
    // Announce to screen readers
    announceToScreenReader(message);
}

/**
 * Get notification icon based on type
 */
function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    
    return icons[type] || icons.info;
}

/**
 * Page visibility handlers
 */
function onPageVisible() {
    if (debugMode) {
        console.log('Page became visible');
    }
    // Resume any paused operations
}

function onPageHidden() {
    if (debugMode) {
        console.log('Page became hidden');
    }
    // Pause non-essential operations
}

/**
 * Online/offline handlers
 */
function onOnline() {
    showNotification('تم استعادة الاتصال بالإنترنت', 'success');
    // Resume online operations
}

function onOffline() {
    showNotification('تم فقدان الاتصال بالإنترنت', 'warning');
    // Switch to offline mode
}

/**
 * Show help dialog
 */
function showHelp() {
    const helpModal = document.querySelector('#helpModal');
    if (helpModal) {
        const modal = new bootstrap.Modal(helpModal);
        modal.show();
    } else {
        showNotification('تعليمات الاستخدام متاحة في القائمة الرئيسية', 'info');
    }
}

/**
 * Utility functions
 */

/**
 * Debounce function
 */
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

/**
 * Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Format number with Arabic digits
 */
function formatArabicNumber(number) {
    const arabicDigits = '٠١٢٣٤٥٦٧٨٩';
    return number.toString().replace(/\d/g, (digit) => arabicDigits[digit]);
}

/**
 * Format date in Arabic
 */
function formatArabicDate(date) {
    const arabicMonths = [
        'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
        'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
    ];
    
    const day = date.getDate();
    const month = arabicMonths[date.getMonth()];
    const year = date.getFullYear();
    
    return `${day} ${month} ${year}`;
}

/**
 * Recalculate positions (placeholder for responsive adjustments)
 */
function recalculatePositions() {
    // Implement position calculations if needed
}

/**
 * Export global functions for use in other modules
 */
window.ArabicSignLanguage = {
    showNotification,
    announceToScreenReader,
    formatArabicNumber,
    formatArabicDate,
    debounce,
    throttle,
    isElementInViewport
};

// Log successful initialization
console.log('Arabic Sign Language Translator main.js loaded successfully');
