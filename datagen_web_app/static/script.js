document.addEventListener("DOMContentLoaded", function () {
    const algorithmSelect = document.getElementById('generationAlgorithm');
    const kernelSizeGroup = document.getElementById('kernelSizeGroup');
    const imageResamplingGroup = document.getElementById('imageResamplingGroup');

    algorithmSelect.addEventListener('change', function () {
        const value = this.value;
        kernelSizeGroup.style.display = (value === "Lanczos Resampling") ? 'block' : 'none';
        imageResamplingGroup.style.display = (value === "Image-based Scaling") ? 'block' : 'none';
    });
});