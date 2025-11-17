// JavaScript for PDF Viewer Modal
let currentDay = 1;

function openPDF(day) {
    currentDay = day;
    document.getElementById('pdfFrame').src = `pdfs/Day${day}.pdf`;
    document.getElementById('pdfViewer').style.display = 'flex';
}

function closePDF() {
    document.getElementById('pdfViewer').style.display = 'none';
    document.getElementById('pdfFrame').src = "";
}

function nextPDF() {
    if (currentDay < 21) {
        currentDay++;
        document.getElementById('pdfFrame').src = `pdfs/Day${currentDay}.pdf`;
    }
}

function previousPDF() {
    if (currentDay > 1) {
        currentDay--;
        document.getElementById('pdfFrame').src = `pdfs/Day${currentDay}.pdf`;
    }
}

// Update each PDF link to open in the modal
document.querySelectorAll('.pdf-link').forEach((link, index) => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        openPDF(index + 1);
    });
});
