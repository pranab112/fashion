// Toast Notifications
const showToast = (message, type = 'info') => {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} animate-slide-in`;
    
    // Add icon based on type
    const icon = type === 'success' ? 'fa-check-circle' : 
                 type === 'error' ? 'fa-exclamation-circle' : 
                 type === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle';
    
    toast.innerHTML = `
        <i class="fas ${icon} mr-2"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease-in-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
};

// Mobile Menu Toggle
const initMobileMenu = () => {
    const menuButton = document.querySelector('.mobile-menu-button');
    const navbarNav = document.querySelector('.navbar-nav');
    
    if (menuButton && navbarNav) {
        menuButton.addEventListener('click', () => {
            navbarNav.classList.toggle('show');
            menuButton.querySelector('i').classList.toggle('fa-bars');
            menuButton.querySelector('i').classList.toggle('fa-times');
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!navbarNav.contains(e.target) && !menuButton.contains(e.target)) {
                navbarNav.classList.remove('show');
                menuButton.querySelector('i').classList.add('fa-bars');
                menuButton.querySelector('i').classList.remove('fa-times');
            }
        });
    }
};

// Product Image Gallery
const initProductGallery = () => {
    const mainImage = document.querySelector('[data-main-image]');
    const thumbnails = document.querySelectorAll('[data-thumbnail]');
    
    if (mainImage && thumbnails.length) {
        thumbnails.forEach(thumb => {
            thumb.addEventListener('click', () => {
                mainImage.src = thumb.dataset.full;
                thumbnails.forEach(t => t.classList.remove('ring-2', 'ring-pink-500'));
                thumb.classList.add('ring-2', 'ring-pink-500');
            });
        });
    }
};

// Quantity Input
const initQuantityInputs = () => {
    document.querySelectorAll('.quantity-input').forEach(wrapper => {
        const input = wrapper.querySelector('input');
        const decrementBtn = wrapper.querySelector('[data-decrement]');
        const incrementBtn = wrapper.querySelector('[data-increment]');
        
        if (input && decrementBtn && incrementBtn) {
            decrementBtn.addEventListener('click', () => {
                const currentValue = parseInt(input.value);
                if (currentValue > parseInt(input.min || 1)) {
                    input.value = currentValue - 1;
                    input.dispatchEvent(new Event('change'));
                }
            });
            
            incrementBtn.addEventListener('click', () => {
                const currentValue = parseInt(input.value);
                const max = parseInt(input.max);
                if (!max || currentValue < max) {
                    input.value = currentValue + 1;
                    input.dispatchEvent(new Event('change'));
                }
            });
        }
    });
};

// Form Validation
const initFormValidation = () => {
    document.querySelectorAll('form[data-validate]').forEach(form => {
        form.addEventListener('submit', (e) => {
            let isValid = true;
            
            form.querySelectorAll('[required]').forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('border-red-500');
                    
                    const errorMessage = field.dataset.errorMessage || 'This field is required';
                    let errorElement = field.nextElementSibling;
                    
                    if (!errorElement || !errorElement.classList.contains('error-message')) {
                        errorElement = document.createElement('p');
                        errorElement.className = 'text-red-500 text-sm mt-1 error-message';
                        field.parentNode.insertBefore(errorElement, field.nextSibling);
                    }
                    
                    errorElement.textContent = errorMessage;
                } else {
                    field.classList.remove('border-red-500');
                    const errorElement = field.nextElementSibling;
                    if (errorElement?.classList.contains('error-message')) {
                        errorElement.remove();
                    }
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showToast('Please fill in all required fields', 'error');
            }
        });
    });
};

// Lazy Loading Images
const initLazyLoading = () => {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    img.classList.add('fade-in');
                    observer.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img.lazy').forEach(img => imageObserver.observe(img));
    }
};

// Price Format
const formatPrice = (price, currency = '₹') => {
    return `${currency}${parseFloat(price).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
};

// Get CSRF Token
const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

// Cart Operations
const cartOperations = {
    add: async (productId, quantity = 1, size = null, color = null) => {
        try {
            const response = await fetch('/api/cart/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ 
                    product_id: productId, 
                    quantity,
                    size,
                    color
                })
            });
            
            if (!response.ok) throw new Error('Failed to add to cart');
            
            const data = await response.json();
            updateCartBadge(data.cart_count);
            showToast('Added to cart successfully', 'success');
            
            return data;
        } catch (error) {
            showToast('Failed to add to cart', 'error');
            console.error('Cart add error:', error);
        }
    },

    update: async (itemId, quantity) => {
        try {
            const response = await fetch(`/api/cart/update/${itemId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ quantity })
            });
            
            if (!response.ok) throw new Error('Failed to update cart');
            
            const data = await response.json();
            updateCartBadge(data.cart_count);
            showToast('Cart updated successfully', 'success');
            
            return data;
        } catch (error) {
            showToast('Failed to update cart', 'error');
            console.error('Cart update error:', error);
        }
    },

    remove: async (itemId) => {
        try {
            const response = await fetch(`/api/cart/remove/${itemId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            
            if (!response.ok) throw new Error('Failed to remove from cart');
            
            const data = await response.json();
            updateCartBadge(data.cart_count);
            showToast('Item removed from cart', 'success');
            
            return data;
        } catch (error) {
            showToast('Failed to remove item', 'error');
            console.error('Cart remove error:', error);
        }
    }
};

// Wishlist Operations
const wishlistOperations = {
    toggle: async (productId) => {
        try {
            const response = await fetch(`/api/wishlist/toggle/${productId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            
            if (!response.ok) {
                if (response.status === 401) {
                    showToast('Please login to add to wishlist', 'warning');
                    window.location.href = '/users/login/';
                    return;
                }
                throw new Error('Failed to update wishlist');
            }
            
            const data = await response.json();
            
            // Update wishlist button icon
            const button = document.querySelector(`[data-product-id="${productId}"]`);
            if (button) {
                const icon = button.querySelector('i');
                if (data.in_wishlist) {
                    icon.classList.remove('far');
                    icon.classList.add('fas', 'text-pink-600');
                } else {
                    icon.classList.remove('fas', 'text-pink-600');
                    icon.classList.add('far');
                }
            }
            
            showToast(data.message, 'success');
            return data;
        } catch (error) {
            showToast('Failed to update wishlist', 'error');
            console.error('Wishlist toggle error:', error);
        }
    }
};

// Update cart badge
const updateCartBadge = (count) => {
    const badges = document.querySelectorAll('.badge');
    badges.forEach(badge => {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'block' : 'none';
    });
};

// Newsletter Form
const initNewsletterForm = () => {
    const forms = document.querySelectorAll('form[action*="newsletter"]');
    forms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const emailInput = form.querySelector('input[type="email"]');
            if (!emailInput.value) {
                showToast('Please enter your email address', 'error');
                return;
            }
            
            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: new FormData(form),
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showToast('Successfully subscribed to newsletter!', 'success');
                    form.reset();
                } else {
                    throw new Error(data.message || 'Subscription failed');
                }
            } catch (error) {
                showToast(error.message, 'error');
            }
        });
    });
};

// Search Autocomplete
const initSearchAutocomplete = () => {
    const searchInput = document.querySelector('.search-form input');
    if (!searchInput) return;
    
    let debounceTimer;
    const searchResults = document.createElement('div');
    searchResults.className = 'search-results absolute top-full left-0 right-0 bg-white shadow-lg rounded-b-lg max-h-96 overflow-y-auto z-50 hidden';
    searchInput.parentElement.appendChild(searchResults);
    
    searchInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        const query = e.target.value.trim();
        
        if (query.length < 2) {
            searchResults.classList.add('hidden');
            return;
        }
        
        debounceTimer = setTimeout(async () => {
            try {
                const response = await fetch(`/api/products/search/?q=${encodeURIComponent(query)}`);
                const data = await response.json();
                
                if (data.results && data.results.length > 0) {
                    searchResults.innerHTML = data.results.map(product => `
                        <a href="${product.url}" class="flex items-center p-3 hover:bg-gray-50 border-b">
                            <img src="${product.image}" alt="${product.name}" class="w-12 h-12 object-cover rounded mr-3">
                            <div class="flex-1">
                                <div class="font-medium text-gray-900">${product.name}</div>
                                <div class="text-sm text-gray-600">${product.brand}</div>
                            </div>
                            <div class="text-pink-600 font-semibold">${formatPrice(product.price)}</div>
                        </a>
                    `).join('');
                    searchResults.classList.remove('hidden');
                } else {
                    searchResults.innerHTML = '<div class="p-4 text-center text-gray-500">No products found</div>';
                    searchResults.classList.remove('hidden');
                }
            } catch (error) {
                console.error('Search error:', error);
            }
        }, 300);
    });
    
    // Hide results when clicking outside
    document.addEventListener('click', (e) => {
        if (!searchInput.parentElement.contains(e.target)) {
            searchResults.classList.add('hidden');
        }
    });
};

// Product Quick View
const initQuickView = () => {
    document.addEventListener('click', async (e) => {
        if (e.target.closest('[data-quick-view]')) {
            e.preventDefault();
            const productId = e.target.closest('[data-quick-view]').dataset.productId;
            
            try {
                const response = await fetch(`/api/products/${productId}/quick-view/`);
                const data = await response.json();
                
                // Create and show modal with product details
                showQuickViewModal(data);
            } catch (error) {
                showToast('Failed to load product details', 'error');
            }
        }
    });
};

// Show Quick View Modal
const showQuickViewModal = (product) => {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 z-50 flex items-center justify-center p-4';
    modal.innerHTML = `
        <div class="absolute inset-0 bg-black bg-opacity-50" onclick="this.parentElement.remove()"></div>
        <div class="relative bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <button onclick="this.closest('.fixed').remove()" class="absolute top-4 right-4 text-gray-500 hover:text-gray-700">
                <i class="fas fa-times text-2xl"></i>
            </button>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8 p-8">
                <div>
                    <img src="${product.image}" alt="${product.name}" class="w-full rounded-lg">
                </div>
                <div>
                    <h2 class="text-2xl font-bold text-gray-900 mb-2">${product.name}</h2>
                    <p class="text-gray-600 mb-4">${product.brand}</p>
                    
                    <div class="mb-6">
                        ${product.sale_price ? `
                            <span class="text-3xl font-bold text-red-500">${formatPrice(product.sale_price)}</span>
                            <span class="text-xl text-gray-500 line-through ml-2">${formatPrice(product.price)}</span>
                        ` : `
                            <span class="text-3xl font-bold text-gray-900">${formatPrice(product.price)}</span>
                        `}
                    </div>
                    
                    <p class="text-gray-700 mb-6">${product.description}</p>
                    
                    <div class="flex gap-4">
                        <button onclick="cartOperations.add('${product.id}')" class="flex-1 bg-pink-600 text-white py-3 px-6 rounded-lg hover:bg-pink-700 transition duration-200">
                            Add to Cart
                        </button>
                        <button onclick="wishlistOperations.toggle('${product.id}')" class="p-3 border border-gray-300 rounded-lg hover:border-pink-600 transition duration-200">
                            <i class="far fa-heart text-gray-600 hover:text-pink-600"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
};

// Hero Slider Functionality
const initHeroSlider = () => {
    const slider = document.getElementById('heroSlider');
    if (!slider) return;

    const slides = slider.querySelectorAll('.slide');
    let currentSlideIndex = 0;
    const totalSlides = slides.length;
    let autoPlayInterval;
    let isAutoPlaying = true;

    function showSlide(index) {
        const dots = document.querySelectorAll('.slider-dot');
        
        // Stop auto-play temporarily
        if (isAutoPlaying) {
            slider.classList.remove('auto-play');
            isAutoPlaying = false;
        }
        
        // Update slide position
        const translateX = -index * 100; // 100% per slide
        slider.style.transform = `translateX(${translateX}%)`;
        
        // Update dots
        dots.forEach((dot, i) => {
            dot.classList.toggle('active', i === index);
        });
        
        currentSlideIndex = index;
        
        // Restart auto-play after manual interaction
        clearTimeout(autoPlayInterval);
        autoPlayInterval = setTimeout(() => {
            slider.classList.add('auto-play');
            isAutoPlaying = true;
        }, 5000);
    }

    function nextSlide() {
        const nextIndex = (currentSlideIndex + 1) % totalSlides;
        showSlide(nextIndex);
    }

    function previousSlide() {
        const prevIndex = (currentSlideIndex - 1 + totalSlides) % totalSlides;
        showSlide(prevIndex);
    }

    // Set up navigation buttons
    const prevBtn = document.querySelector('.slider-btn-prev');
    const nextBtn = document.querySelector('.slider-btn-next');
    
    if (prevBtn) prevBtn.addEventListener('click', previousSlide);
    if (nextBtn) nextBtn.addEventListener('click', nextSlide);

    // Set up dot navigation
    document.querySelectorAll('.slider-dot').forEach((dot, index) => {
        dot.addEventListener('click', () => showSlide(index));
    });

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') {
            previousSlide();
        } else if (e.key === 'ArrowRight') {
            nextSlide();
        }
    });

    // Touch/swipe support
    let startX = 0;
    let endX = 0;
    
    slider.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX;
    });
    
    slider.addEventListener('touchend', (e) => {
        endX = e.changedTouches[0].clientX;
        const swipeThreshold = 50;
        const diff = startX - endX;
        
        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                nextSlide();
            } else {
                previousSlide();
            }
        }
    });

    // Pause auto-play on hover
    slider.addEventListener('mouseenter', () => {
        slider.classList.remove('auto-play');
    });

    slider.addEventListener('mouseleave', () => {
        if (isAutoPlaying) {
            slider.classList.add('auto-play');
        }
    });

    // Make functions globally available
    window.heroSliderControls = {
        nextSlide,
        previousSlide,
        goToSlide: showSlide
    };
};

// Initialize all components
document.addEventListener('DOMContentLoaded', () => {
    initMobileMenu();
    initProductGallery();
    initQuantityInputs();
    initFormValidation();
    initLazyLoading();
    initNewsletterForm();
    initSearchAutocomplete();
    initQuickView();
    initHeroSlider(); // Add hero slider initialization
});

// Export utilities for use in other scripts
window.nexusUtils = {
    showToast,
    formatPrice,
    getCookie,
    cartOperations,
    wishlistOperations,
    updateCartBadge
};
