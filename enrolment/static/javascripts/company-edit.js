(function() {
  var destinationsOther = document.getElementById('id_classification-export_destinations_other');
  var destinationsOtherParent = destinationsOther.parentElement;
  var destinations = document.getElementById('id_classification-export_destinations');

  function hideDestinationsOther() {
    destinationsOtherParent.style.display = 'none';
  }

  function showDestinationsOther() {
    destinationsOtherParent.style.display = 'list-item';
  }

  function hideDestinationOtherLabel() {
    destinationsOtherParent.getElementsByTagName('label')[0].style.display = 'none';
  }

  function handleDestinationOtherChange(event) {
    if (event.target.checked) {
      showDestinationsOther();
    } else {
      hideDestinationsOther()
      destinationsOther.value = '';
    }
  }

  hideDestinationsOther();
  hideDestinationOtherLabel();
  destinations.lastChild.addEventListener('change', handleDestinationOtherChange);
})();