function myFunc(){
        document.getElementById('form-submit').click();
    }

function preventModal(){
    var input = document.getElementById("modal_confirm");
    input.addEventListener("keyup", function(event) {
      if (event.keyCode == 13 || event.which == 13) {
        event.preventDefault();
        console.log('The enter key was pressed');
      }
    });
}

function myFunction(){
    var input = document.getElementById("myInput");
    input.addEventListener("keyup", function(event) {
      if (event.keyCode == 13 || event.which == 13) {
        event.preventDefault();
        document.getElementById("enter-modal").click();
      }
    });
}