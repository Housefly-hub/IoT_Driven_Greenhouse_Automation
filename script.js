        // Get references to the slider and display elements
const fan_speed = document.getElementById('fan-speed');
const fan_rpm = document.getElementById('fan-rpm');
const fan_animation = document.getElementById('fan-animation');

// Update the display text when the slider value changes
fan_speed.addEventListener('input', function () {
    const value = fan_speed.value;
    fan_rpm.textContent = fan_speed.value;

    const percentage = (value / 1000) * 100;
    if (percentage <= 10) {
        fan_animation.style.animationDuration = '1s';
    }
    else if (percentage <= 20) {
        fan_animation.style.animationDuration = '0.9s';
    }
    else if (percentage <= 30) {
        fan_animation.style.animationDuration = '0.8s';
    }
    else if (percentage <= 40) {
        fan_animation.style.animationDuration = '0.7s';
    }
    else if (percentage <= 50) {
        fan_animation.style.animationDuration = '0.6s';
    }
    else if (percentage <= 60) {
        fan_animation.style.animationDuration = '0.5s';
    }
    else if (percentage <= 70) {
        fan_animation.style.animationDuration = '0.4s';
    }
    else {
        fan_animation.style.animationDuration = '0.3s';
    }
    
});

function toggle() {
    const lightIntensity = document.getElementById("light-intensity");
    const toggleButton = document.getElementById("toggle-button");
    const lightToggle = document.getElementById("light-svg");
    if (toggleButton.value === 'OFF') {
        toggleButton.value = 'ON';
        toggleButton.innerText = 'OFF'
        toggleButton.style.color = 'Red';
        lightIntensity.innerHTML = '50';
        lightToggle.src= './images/light_off.svg'
    }
    else {
        toggleButton.value = 'OFF';
        toggleButton.innerText = 'ON';
        toggleButton.style.color = 'Green';
        lightIntensity.innerHTML = '0'
        lightToggle.src='./images/light_on.svg'
    }
}
