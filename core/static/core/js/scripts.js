// JavaScript for sale page (focus barcode field on load)
window.addEventListener("load", function () {
  var barcodeField = document.querySelector("input[name='barcode']");
  if (barcodeField) {
    barcodeField.focus();
  }
});
