document.addEventListener('DOMContentLoaded', function() {
    initializeSliders();
    initializeGenderButtons();
    initializeForm();
    
    const diseaseColors = {
        'COVID-19': '#FF6B6B',
        'Dengue': '#FFA726',
        'Influenza': '#42A5F5',
        'Malaria': '#66BB6A',
        'Pneumonia': '#AB47BC'
    };
    
    const diseaseEmojis = {
        'COVID-19': '🦠',
        'Dengue': '🦟',
        'Influenza': '🤒',
        'Malaria': '🌡️',
        'Pneumonia': '🫁'
    };
    
    // Initialize sliders
    function initializeSliders() {
        // Connect sliders with number inputs
        document.querySelectorAll('.slider, .symptom-slider').forEach(slider => {
            const inputId = slider.id.replace('Slider', '');
            const numberInput = document.getElementById(inputId);
            const valueDisplay = document.getElementById(inputId + 'Value');
            
            if (slider.classList.contains('symptom-slider')) {
                // Symptom sliders
                slider.addEventListener('input', function() {
                    const value = this.value;
                    if (valueDisplay) valueDisplay.textContent = value;
                    if (numberInput) numberInput.value = value;
                    updateSymptomColor(this, value);
                });
                
                // Initialize color
                updateSymptomColor(slider, slider.value);
            } else {
                // Regular sliders
                slider.addEventListener('input', function() {
                    const value = this.value;
                    if (numberInput) numberInput.value = value;
                });
                
                numberInput.addEventListener('input', function() {
                    const value = this.value;
                    slider.value = value;
                });
            }
        });
    }
    
    // Update symptom slider color based on value
    function updateSymptomColor(slider, value) {
        const colors = ['#e0e0e0', '#4caf50', '#ff9800', '#f44336'];
        slider.style.background = `linear-gradient(to right, ${colors[0]} 0%, ${colors[value]} ${value * 33}%)`;
    }
    
    // Initialize gender buttons
    function initializeGenderButtons() {
        const genderButtons = document.querySelectorAll('.gender-btn');
        const genderInput = document.getElementById('gender');
        
        genderButtons.forEach(button => {
            button.addEventListener('click', function() {
                const value = this.getAttribute('data-value');
                
                // Update active state
                genderButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // Update hidden input
                genderInput.value = value;
            });
        });
    }
    
    function initializeForm() {
        const form = document.getElementById('diagnosisForm');
        const resetBtn = document.getElementById('resetBtn');
        const predictBtn = document.getElementById('predictBtn');
        
        // Reset form
        resetBtn.addEventListener('click', function() {
            form.reset();
            
            // Reset all sliders to default values
            document.querySelectorAll('.slider, .symptom-slider').forEach(slider => {
                const defaultValue = slider.id.includes('Slider') ? 
                    (slider.classList.contains('symptom-slider') ? '0' : slider.getAttribute('value')) : 
                    slider.value;
                slider.value = defaultValue;
                
                // Update connected inputs
                const inputId = slider.id.replace('Slider', '');
                const numberInput = document.getElementById(inputId);
                const valueDisplay = document.getElementById(inputId + 'Value');
                
                if (numberInput) numberInput.value = defaultValue;
                if (valueDisplay) valueDisplay.textContent = defaultValue;
                
                // Update symptom colors
                if (slider.classList.contains('symptom-slider')) {
                    updateSymptomColor(slider, defaultValue);
                }
            });
            
            // Reset gender to Male
            document.querySelectorAll('.gender-btn').forEach(btn => {
                btn.classList.remove('active');
                if (btn.getAttribute('data-value') === 'Male') {
                    btn.classList.add('active');
                }
            });
            document.getElementById('gender').value = 'Male';
            
            // Reset results
            resetResults();
            
            showNotification('Form has been reset!', 'success');
        });
        
        // Form submission
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            predictDiagnosis();
        });
        
        // Predict button click
        predictBtn.addEventListener('click', function() {
            predictDiagnosis();
        });
    }
    
    // Predict diagnosis
    async function predictDiagnosis() {
        // Show loading modal
        showLoading(true);
        
        // Collect form data
        const formData = new FormData(document.getElementById('diagnosisForm'));
        const data = Object.fromEntries(formData.entries());
        
        try {
            // Send prediction request
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                displayResult(result);
                displayProbabilities(result.all_probabilities);
                showNotification('Diagnosis predicted successfully!', 'success');
            } else {
                throw new Error(result.error || 'Prediction failed');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Error: ' + error.message, 'error');
        } finally {
            // Hide loading modal
            showLoading(false);
        }
    }
    
    // Display prediction result
    function displayResult(result) {
        const resultBody = document.getElementById('resultBody');
        const severityClass = `severity-${result.severity.toLowerCase()}`;
        
        resultBody.innerHTML = `
            <div class="diagnosis-result">
                <div class="diagnosis-emoji">${result.emoji}</div>
                <h2 class="diagnosis-name" style="color: ${result.color}">
                    ${result.diagnosis}
                </h2>
                <p class="diagnosis-desc">${result.description}</p>
                <div class="confidence-badge" style="background: ${result.color}20; color: ${result.color}">
                    Confidence: ${result.confidence}%
                </div>
                <div class="severity ${severityClass}">
                    Severity: <span class="severity-badge ${severityClass}">${result.severity}</span>
                </div>
                <div class="recommendations">
                    <p><i class="fas fa-stethoscope"></i> Recommended: Consult a healthcare professional immediately</p>
                </div>
            </div>
        `;
    }
    
    // Display probability distribution
    function displayProbabilities(probabilities) {
        const probabilityBody = document.getElementById('probabilityBody');
        
        let html = '<div class="probability-list">';
        
        probabilities.forEach(item => {
            const barWidth = Math.min(item.probability, 100);
            html += `
                <div class="probability-item">
                    <div class="probability-header-row">
                        <div class="disease-name">
                            <span class="disease-emoji">${item.emoji}</span>
                            <span class="disease-label">${item.disease}</span>
                        </div>
                        <div class="probability-value">${item.probability}%</div>
                    </div>
                    <div class="probability-bar-container">
                        <div class="probability-bar" 
                             style="width: ${barWidth}%; background: ${item.color}">
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        probabilityBody.innerHTML = html;
        
        // Animate bars
        setTimeout(() => {
            document.querySelectorAll('.probability-bar').forEach(bar => {
                bar.style.transition = 'width 1s ease-in-out';
            });
        }, 100);
    }
    
    // Reset results
    function resetResults() {
        const resultBody = document.getElementById('resultBody');
        const probabilityBody = document.getElementById('probabilityBody');
        
        resultBody.innerHTML = `
            <div class="placeholder">
                <i class="fas fa-heartbeat"></i>
                <p>Enter patient data and click "Predict Diagnosis" to see results</p>
            </div>
        `;
        
        probabilityBody.innerHTML = `
            <div class="placeholder">
                <i class="fas fa-chart-pie"></i>
                <p>Prediction results will appear here</p>
            </div>
        `;
    }
    
    // Show loading modal
    function showLoading(show) {
        const modal = document.getElementById('loadingModal');
        modal.style.display = show ? 'flex' : 'none';
    }
    
    // Show notification
    function showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
        `;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#4CAF50' : '#f44336'};
            color: white;
            padding: 15px 25px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: flex;
            align-items: center;
            gap: 10px;
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        
        // Add keyframe animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        
        // Add to document
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
    
    // Add some initial animations
    setTimeout(() => {
        document.querySelectorAll('.symptom-card').forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
            card.style.animation = 'fadeInUp 0.5s ease forwards';
        });
    }, 500);
    
    // Add animation styles
    const animationStyles = document.createElement('style');
    animationStyles.textContent = `
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .symptom-card {
            opacity: 0;
        }
    `;
    document.head.appendChild(animationStyles);
});