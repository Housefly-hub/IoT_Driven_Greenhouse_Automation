        // Get references to the slider and display elements
const fan_speed = document.getElementById('fan-speed');
const fan_rpm = document.getElementById('fan-rpm');

// Update the display text when the slider value changes
fan_speed.addEventListener('input', function() {
    fan_rpm.textContent = fan_speed.value;
});
