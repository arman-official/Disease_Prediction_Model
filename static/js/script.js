document.addEventListener('DOMContentLoaded', function() {
    initializeSliders();
    initializeGenderButtons();
    initializeForm();
    
    function initializeSliders() {
        document.querySelectorAll('.slider, .symptom-slider').forEach(slider => {
            const inputId = slider.id.replace('Slider', '');
            const numberInput = document.getElementById(inputId);
            const valueDisplay = document.getElementById(inputId + 'Value');
            
            if (slider.classList.contains('symptom-slider')) {
                slider.addEventListener('input', function() {
                    const value = this.value;
                    if (valueDisplay) valueDisplay.textContent = value;
                    if (numberInput) numberInput.value = value;
                    updateSymptomText(this.id.replace('Slider', ''), value);
                });
                
                updateSymptomText(slider.id.replace('Slider', ''), slider.value);
            } else {
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
    
    function updateSymptomText(symptomId, value) {
        const textElement = document.getElementById(symptomId + 'Text');
        const texts = ['None', 'Mild', 'Moderate', 'Severe'];
        if (textElement) {
            textElement.textContent = texts[parseInt(value)] || 'None';
        }
    }
    
    function initializeGenderButtons() {
        const genderButtons = document.querySelectorAll('.gender-btn');
        const genderInput = document.getElementById('gender');
        
        genderButtons.forEach(button => {
            button.addEventListener('click', function() {
                const value = this.getAttribute('data-value');
                
                genderButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                genderInput.value = value;
            });
        });
    }
    
    function initializeForm() {
        const form = document.getElementById('diagnosisForm');
        const resetBtn = document.getElementById('resetBtn');
        const predictBtn = document.getElementById('predictBtn');
        
        resetBtn.addEventListener('click', function() {
            form.reset();
            
            document.querySelectorAll('.slider, .symptom-slider').forEach(slider => {
                const defaultValue = slider.classList.contains('symptom-slider') ? '0' : 
                    slider.id === 'ageSlider' ? '30' : slider.value;
                slider.value = defaultValue;
                
                const inputId = slider.id.replace('Slider', '');
                const numberInput = document.getElementById(inputId);
                const valueDisplay = document.getElementById(inputId + 'Value');
                
                if (numberInput) numberInput.value = defaultValue;
                if (valueDisplay) valueDisplay.textContent = defaultValue;
                
                if (slider.classList.contains('symptom-slider')) {
                    updateSymptomText(inputId, defaultValue);
                }
            });
            
            document.querySelectorAll('.gender-btn').forEach(btn => {
                btn.classList.remove('active');
                if (btn.getAttribute('data-value') === 'Male') {
                    btn.classList.add('active');
                }
            });
            document.getElementById('gender').value = 'Male';
            
            resetResults();
        });
        
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            predictDiagnosis();
        });
        
        predictBtn.addEventListener('click', function() {
            predictDiagnosis();
        });
    }
    
    async function predictDiagnosis() {
        showLoading(true);
        
        const formData = new FormData(document.getElementById('diagnosisForm'));
        const data = Object.fromEntries(formData.entries());
        
        try {
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
            } else {
                throw new Error(result.error || 'Prediction failed');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Error: ' + error.message);
        } finally {
            showLoading(false);
        }
    }
    
    function displayResult(result) {
        const resultBody = document.getElementById('resultBody');
        const severityClass = 'severity-' + result.severity.toLowerCase();
        
        resultBody.innerHTML = `
            <div class="diagnosis-result">
                <h2 class="diagnosis-name">${result.diagnosis}</h2>
                <p class="diagnosis-desc">${result.description}</p>
                <div class="confidence-badge">Confidence: ${result.confidence}%</div>
                <div class="${severityClass} severity-indicator">
                    ${result.severity} Severity
                </div>
                <div class="recommendations">
                    <ul>
                        <li>• Consult a healthcare provider</li>
                        <li>• Get appropriate medical tests</li>
                        <li>• Follow prescribed treatment</li>
                        <li>• Monitor symptoms regularly</li>
                    </ul>
                </div>
            </div>
        `;
    }
    
    function displayProbabilities(probabilities) {
        const probabilityBody = document.getElementById('probabilityBody');
        
        let html = '<div class="probability-list">';
        
        probabilities.forEach(item => {
            const barWidth = Math.min(item.probability, 100);
            html += `
                <div class="probability-item">
                    <div class="probability-header-row">
                        <div class="disease-name">
                            <span class="disease-label">${item.disease}</span>
                        </div>
                        <div class="probability-value">${item.probability}%</div>
                    </div>
                    <div class="probability-bar-container">
                        <div class="probability-bar" style="width: ${barWidth}%"></div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        probabilityBody.innerHTML = html;
        
        setTimeout(() => {
            document.querySelectorAll('.probability-bar').forEach(bar => {
                bar.style.transition = 'width 1s ease-in-out';
            });
        }, 100);
    }
    
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
    
    function showLoading(show) {
        const modal = document.getElementById('loadingModal');
        modal.style.display = show ? 'flex' : 'none';
    }
    
    function showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.innerHTML = `<span>${message}</span>`;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4CAF50;
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.15);
            z-index: 10000;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transition = 'opacity 0.3s';
            setTimeout(() => {
                if (notification.parentNode) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
    
    setTimeout(() => {
        document.querySelectorAll('.symptom-card').forEach((card, index) => {
            card.style.animationDelay = `${index * 0.05}s`;
            card.style.animation = 'fadeInUp 0.3s ease forwards';
        });
    }, 300);
});