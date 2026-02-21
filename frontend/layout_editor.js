// Logic to auto-load template from URL params
// Assuming the use of a function getUrlParameter to get the template ID from the URL
const templateId = getUrlParameter('templateId');

// Load template using templateId
loadTemplate(templateId);

// Remove Apply button wiring
// ... (remove code related to Apply button)

// Add immediate apply to field property inputs
function onInputChange(event) {
    const inputField = event.target;
    applyChanges(inputField);
}

// Assuming inputFields is a collection of input fields
inputFields.forEach(input => {
    input.addEventListener('input', onInputChange);
});

// Wire Generate button to open generator.html with template ID
const generateButton = document.getElementById('generate-button');
generateButton.addEventListener('click', () => {
    window.open(`generator.html?templateId=${templateId}`, '_blank');
});
