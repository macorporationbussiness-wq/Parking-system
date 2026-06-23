// Smart Parking System - Main JavaScript File
// O(1) Operations with Hash Table Technology

$(document).ready(function() {
    initializeSystem();
    console.log('🚗 Smart Parking System Initialized - Hash Table Ready');
});

/**
 * Initialize all system components
 */
function initializeSystem() {
    initAnimations();
    initFormValidations();
    initRealTimeUpdates();
    initInteractiveElements();
    initPerformanceMonitoring();
}

// ===== ANIMATIONS & UI ENHANCEMENTS =====
function initAnimations() {
    // Card hover animations
    $('.card').hover(
        function() {
            $(this).addClass('shadow-lg animate__animated');
            $(this).css('transform', 'translateY(-5px)');
        },
        function() {
            $(this).removeClass('shadow-lg animate__animated');
            $(this).css('transform', 'translateY(0)');
        }
    );

    // Button loading states
    $('form').on('submit', function() {
        const submitBtn = $(this).find('button[type="submit"]');
        if (submitBtn.length && !submitBtn.hasClass('no-loading')) {
            const originalText = submitBtn.html();
            submitBtn.prop('disabled', true).html(
                '<i class="fas fa-spinner fa-spin me-2"></i>Processing...'
            );
            
            // Restore button after 5 seconds (safety timeout)
            setTimeout(() => {
                submitBtn.prop('disabled', false).html(originalText);
            }, 5000);
        }
    });

    // Auto-scroll animations
    $(window).on('scroll', function() {
        $('.animate-on-scroll').each(function() {
            const element = $(this);
            const position = element.offset().top;
            const scrollPosition = $(window).scrollTop() + $(window).height();
            
            if (position < scrollPosition - 50) {
                element.addClass('animate__animated animate__fadeInUp');
            }
        });
    });

    // Input focus animations
    $('.form-control, .form-select').on('focus', function() {
        $(this).parent().addClass('input-group-focus');
    }).on('blur', function() {
        $(this).parent().removeClass('input-group-focus');
    });
}

// ===== FORM VALIDATIONS =====
function initFormValidations() {
    // Registration number validation and auto-format
    $('input[name="registration_number"]').on('input', function() {
        const value = $(this).val().toUpperCase().replace(/[^A-Z0-9]/g, '');
        $(this).val(value);
        
        validateRegistrationNumber(value, $(this));
    });

    // Contact number validation
    $('input[name="contact_number"]').on('input', function() {
        const value = $(this).val().replace(/[^0-9]/g, '');
        $(this).val(value);
        validateContactNumber(value, $(this));
    });

    // Slot number validation
    $('input[name="slot_number"]').on('input', function() {
        const value = parseInt($(this).val());
        validateSlotNumber(value, $(this));
    });

    // Real-time search validation
    $('input[name="query"]').on('input', debounce(function() {
        const searchType = $('#search_type').val();
        const query = $(this).val().trim();
        
        if (query.length >= 2) {
            performRealTimeSearch(query, searchType);
        }
    }, 500));
}

function validateRegistrationNumber(value, element) {
    if (value.length >= 3) {
        element.addClass('is-valid').removeClass('is-invalid');
        return true;
    } else if (value.length > 0) {
        element.addClass('is-invalid').removeClass('is-valid');
        return false;
    } else {
        element.removeClass('is-valid is-invalid');
        return false;
    }
}

function validateContactNumber(value, element) {
    if (value.length === 10 || value.length === 0) {
        element.addClass('is-valid').removeClass('is-invalid');
        return true;
    } else if (value.length > 0) {
        element.addClass('is-invalid').removeClass('is-valid');
        return false;
    } else {
        element.removeClass('is-valid is-invalid');
        return false;
    }
}

function validateSlotNumber(value, element) {
    if (value >= 1 && value <= 100) {
        element.addClass('is-valid').removeClass('is-invalid');
        return true;
    } else if (!isNaN(value)) {
        element.addClass('is-invalid').removeClass('is-valid');
        return false;
    } else {
        element.removeClass('is-valid is-invalid');
        return false;
    }
}

// ===== REAL-TIME UPDATES =====
function initRealTimeUpdates() {
    // Update statistics every 20 seconds
    setInterval(updateParkingStatistics, 20000);
    
    // Update real-time clock
    setInterval(updateRealTimeClock, 1000);
    
    // Initial updates
    updateParkingStatistics();
    updateRealTimeClock();
}

function updateParkingStatistics() {
    const startTime = performance.now();
    
    $.ajax({
        url: '/api/statistics',
        method: 'GET',
        success: function(data) {
            if (data.success) {
                updateStatisticsDisplay(data.data);
                logPerformance('Statistics Update', startTime);
            }
        },
        error: function(xhr, status, error) {
            console.error('❌ Error fetching statistics:', error);
            showNotification('Failed to update statistics', 'error');
        }
    });
}

function updateStatisticsDisplay(stats) {
    // Update all statistic elements on the page
    const elements = {
        'total-slots': stats.total_slots,
        'occupied-slots': stats.occupied_slots,
        'free-slots': stats.free_slots,
        'hash-entries': stats.hash_table_entries,
        'utilization-percentage': stats.utilization_percentage + '%'
    };

    Object.keys(elements).forEach(id => {
        const element = $(`#${id}`);
        if (element.length) {
            const currentValue = element.text();
            const newValue = elements[id];
            
            if (currentValue !== newValue.toString()) {
                element.fadeOut(200, function() {
                    $(this).text(newValue).fadeIn(200);
                });
            }
        }
    });

    // Update progress bars if any
    $('.progress-bar').each(function() {
        const utilization = stats.utilization_percentage;
        $(this).css('width', utilization + '%')
               .attr('aria-valuenow', utilization)
               .text(utilization + '%');
    });
}

function updateRealTimeClock() {
    const now = new Date();
    const timeString = now.toLocaleString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    }).replace(/,/g, '');
    
    $('#current-time').text(timeString);
}

// ===== INTERACTIVE ELEMENTS =====
function initInteractiveElements() {
    // Initialize Bootstrap components
    $('[data-bs-toggle="tooltip"]').tooltip({
        trigger: 'hover',
        placement: 'top'
    });

    $('[data-bs-toggle="popover"]').popover();

    // Auto-dismiss alerts
    $('.alert-auto-dismiss').delay(5000).fadeOut(400, function() {
        $(this).alert('close');
    });

    // Smooth scrolling
    $('a[href^="#"]').on('click', function(event) {
        event.preventDefault();
        const target = $(this.getAttribute('href'));
        if (target.length) {
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 70
            }, 1000);
        }
    });

    // Refresh buttons
    $('.btn-refresh').on('click', function(e) {
        e.preventDefault();
        const btn = $(this);
        const originalHtml = btn.html();
        
        btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-2"></i>Refreshing...');
        
        setTimeout(() => {
            window.location.reload();
        }, 1000);
    });

    // Dynamic search type updates
    $('#search_type').on('change', function() {
        updateSearchPlaceholder($(this).val());
    });
}

function updateSearchPlaceholder(searchType) {
    const input = $('input[name="query"]');
    const labels = {
        'registration': 'Enter registration number (e.g., ABC123)',
        'slot': 'Enter slot number (1-100)',
        'contact': 'Enter 10-digit contact number'
    };
    
    input.attr('placeholder', labels[searchType] || 'Enter search term...');
    
    // Clear and focus
    input.val('').focus();
}

// ===== REAL-TIME SEARCH =====
function performRealTimeSearch(query, searchType) {
    const startTime = performance.now();
    
    $.ajax({
        url: `/api/search?type=${searchType}&query=${encodeURIComponent(query)}`,
        method: 'GET',
        success: function(data) {
            displayRealTimeSearchResults(data, searchType);
            logPerformance('Real-time Search', startTime);
        },
        error: function(xhr, status, error) {
            console.error('❌ Search error:', error);
        }
    });
}

function displayRealTimeSearchResults(data, searchType) {
    const resultsContainer = $('#searchResults');
    if (!resultsContainer.length) return;

    if (data.success) {
        resultsContainer.html(`
            <div class="alert alert-success animate__animated animate__fadeIn">
                <div class="d-flex align-items-center">
                    <i class="fas fa-check-circle me-3 fa-lg"></i>
                    <div>
                        <strong>Vehicle Found!</strong><br>
                        ${data.data.registration_number} in Slot ${data.data.slot_number}
                    </div>
                </div>
            </div>
        `).slideDown();
    } else {
        resultsContainer.html(`
            <div class="alert alert-warning animate__animated animate__fadeIn">
                <div class="d-flex align-items-center">
                    <i class="fas fa-search me-3 fa-lg"></i>
                    <div>
                        <strong>No results found</strong><br>
                        ${data.message}
                    </div>
                </div>
            </div>
        `).slideDown();
    }
}

// ===== NOTIFICATION SYSTEM =====
function showNotification(message, type = 'info', duration = 5000) {
    const alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    }[type] || 'alert-info';

    const icon = {
        'success': 'fa-check-circle',
        'error': 'fa-exclamation-circle',
        'warning': 'fa-exclamation-triangle',
        'info': 'fa-info-circle'
    }[type] || 'fa-info-circle';

    // Remove existing notifications
    $('.custom-notification').remove();

    const notification = $(`
        <div class="alert ${alertClass} custom-notification alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 9999; min-width: 300px; max-width: 400px;" 
             role="alert">
            <div class="d-flex align-items-center">
                <i class="fas ${icon} me-3 fa-lg"></i>
                <div class="flex-grow-1">${message}</div>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        </div>
    `);

    $('body').append(notification);
    
    // Auto remove after duration
    setTimeout(() => {
        notification.alert('close');
    }, duration);

    return notification;
}

// ===== PERFORMANCE MONITORING =====
function initPerformanceMonitoring() {
    // Log page load performance
    window.addEventListener('load', function() {
        const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
        console.log(`⚡ Page loaded in ${loadTime}ms`);
        
        if (loadTime > 3000) {
            console.warn('⚠️ Page load time is high - Consider optimization');
        }
    });

    // Monitor hash table operations
    $(document).on('ajaxSuccess', function(event, xhr, settings) {
        if (settings.url.includes('/api/')) {
            const operation = settings.url.split('/api/')[1];
            const responseTime = xhr.getResponseHeader('X-Response-Time');
            if (responseTime) {
                console.log(`🎯 ${operation} API response: ${responseTime}ms`);
            }
        }
    });
}

function logPerformance(operation, startTime) {
    const endTime = performance.now();
    const duration = endTime - startTime;
    
    console.log(`⏱️ ${operation} completed in ${duration.toFixed(2)}ms`);
    
    if (duration > 1000) {
        console.warn(`🚨 ${operation} took ${duration.toFixed(2)}ms - Performance issue detected`);
        showNotification(`Slow operation: ${operation}`, 'warning', 3000);
    } else if (duration > 500) {
        console.info(`⚠️ ${operation} took ${duration.toFixed(2)}ms - Consider optimization`);
    }
}

// ===== UTILITY FUNCTIONS =====
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

function formatDuration(hours) {
    if (hours < 1) {
        const minutes = Math.round(hours * 60);
        return minutes + ' minute' + (minutes !== 1 ? 's' : '');
    } else if (hours < 24) {
        return hours.toFixed(1) + ' hour' + (hours !== 1 ? 's' : '');
    } else {
        const days = (hours / 24).toFixed(1);
        return days + ' day' + (days !== 1 ? 's' : '');
    }
}

function formatVehicleType(vehicleType) {
    const icons = {
        'Car': 'fas fa-car',
        'SUV': 'fas fa-truck',
        'Motorcycle': 'fas fa-motorcycle',
        'Bike': 'fas fa-bicycle',
        'Truck': 'fas fa-truck-moving',
        'Van': 'fas fa-shuttle-van',
        'Electric': 'fas fa-bolt'
    };
    
    return icons[vehicleType] || 'fas fa-vehicle';
}

// ===== API FUNCTIONS =====
const ParkingAPI = {
    searchVehicle: function(query, type = 'registration') {
        return $.ajax({
            url: `/api/search?type=${type}&query=${encodeURIComponent(query)}`,
            method: 'GET'
        });
    },

    allocateSlot: function(vehicleData) {
        const startTime = performance.now();
        return $.ajax({
            url: '/api/allocate',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(vehicleData)
        }).always(() => {
            logPerformance('Slot Allocation', startTime);
        });
    },

    removeVehicle: function(registrationNumber) {
        const startTime = performance.now();
        return $.ajax({
            url: '/api/remove',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                registration_number: registrationNumber
            })
        }).always(() => {
            logPerformance('Vehicle Removal', startTime);
        });
    },

    getStatistics: function() {
        return $.ajax({
            url: '/api/statistics',
            method: 'GET'
        });
    },

    getSlots: function() {
        return $.ajax({
            url: '/api/slots',
            method: 'GET'
        });
    }
};

// ===== ERROR HANDLING =====
$(document).ajaxError(function(event, xhr, settings, error) {
    console.error('❌ AJAX Error:', {
        url: settings.url,
        method: settings.method,
        status: xhr.status,
        error: error
    });
    
    let userMessage = 'Network error occurred. Please try again.';
    
    if (xhr.status === 0) {
        userMessage = 'Network connection lost. Please check your internet connection.';
    } else if (xhr.status >= 500) {
        userMessage = 'Server error occurred. Our team has been notified.';
    }
    
    showNotification(userMessage, 'error');
});

// Global error handler
window.addEventListener('error', function(e) {
    console.error('🚨 Global Error:', e.error);
    showNotification('A system error occurred', 'error');
});

// Unhandled promise rejection handler
window.addEventListener('unhandledrejection', function(e) {
    console.error('🚨 Unhandled Promise Rejection:', e.reason);
    e.preventDefault();
});

// ===== EXPORT FUNCTIONS FOR GLOBAL USE =====
window.ParkingSystem = {
    // Utility functions
    showNotification,
    formatDuration,
    formatVehicleType,
    debounce,
    
    // API functions
    API: ParkingAPI,
    
    // Validation functions
    validateRegistrationNumber,
    validateContactNumber,
    validateSlotNumber,
    
    // Performance
    logPerformance,
    
    // System info
    version: '2.0.0',
    hashTableEnabled: true,
    performanceMode: true
};

// ===== INITIALIZATION COMPLETE =====
console.log(`
🎯 Smart Parking System JavaScript Loaded Successfully!
📍 Version: ${window.ParkingSystem.version}
⚡ Performance Mode: ${window.ParkingSystem.performanceMode}
🚗 Hash Table Technology: ${window.ParkingSystem.hashTableEnabled}
📊 Real-time Updates: Enabled
✅ All systems operational
`);

// Service Worker registration for offline capability (future enhancement)
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
        .then(registration => {
            console.log('🔧 Service Worker registered:', registration);
        })
        .catch(error => {
            console.log('🔧 Service Worker registration failed:', error);
        });
}