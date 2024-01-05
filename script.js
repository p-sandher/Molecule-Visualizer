
$(document).ready(function() {
    // Add element form - sends form , returns an alert message
    $('#elementFormSubmit').click(function() {
        var formData = $('form[name="elementForm"]').serialize();
        $.ajax({
            type: "POST",
            url: "/elementForm",
            data: formData,
            success: function(response) {
                alert(response);
                window.location.href = 'update.html';
            },
            error: function(jqXHR, text, errorStatus) {
                alert("Error. Could not upload element.");
                console.log(text, errorStatus);
            }
        });
      });
    //   SDF File Form - sends file, returns alert
    $('#sdfFileSubmit').click(function() {
        var formData = $('form[name="sdfFileForm"]')
        var fileData = new FormData();
        fileData.append('filename', $('input[type=file]')[0].files[0]);
        $.ajax({
            type: "POST",
            url: "/sdfFileForm",
            data: fileData,
            processData: false,
            contentType: false,
            success: function(response) {
                alert(response);
                
            },
            error: function(jqXHR, text, errorStatus) {
                alert("Error. Could not upload file.");
                console.log(text, errorStatus);
            }
        });
    });
    
    // Molecule Name Form - sends molecule name, returns alert
    $('#molNameSubmit').click(function() {
      var formData = $('form[name="molNameForm"]').serialize();
      $.ajax({
          type: "POST",
          url: "/molNameForm",
          data: formData,
          success: function(response) {
              alert(response);
          },
          error: function(jqXHR, text, errorStatus) {
            alert("Error. Could not upload molecule.");
              console.log(text, errorStatus);
          }
      });
    });

    // Element Delete form - sends element name, returns alert
    $('#elementDelFormSubmit').click(function() {
        var dropdownVal = $('#elementDropdown').val()
        $.ajax({
            type: "POST",
            url: "/elementDelForm",
            data: dropdownVal,
            success: function(response) {
                alert(response);
                window.location.href = 'update.html';
            },
            error: function(jqXHR, text, errorText) {
                alert("Error. Could not delete element.");
                console.log(text, errorText);
            }
        });
      });
      
    //   Molecule Form - sends which molecule to display, returns SVG
      $('#moleculeForm').submit(function(event) {
        event.preventDefault();
        var selectedMol = $('button[name="mol"]:focus').val();
    
        $.ajax({
            type: "POST",
            url: "/moleculeForm",
            data: {mol: selectedMol},
            dataType: 'text',
            success: function(response) {
                // console.log(len(response))
                if(response){
                    
                    $('#molSVGImg').html('');
                    $('#molSVGImg').html(response);
                }
            },
            error: function(jqXHR, text, errorText) {
                alert("Error. Could not load molecule.");
                console.log(text, error);
            }
        });
      });
      /*
      $('#moleculeRotationFormSubmit').click(function() {
        var formData = $('form[name="rotateMoleculeForm"]').serialize();
        var formData = {
            'ROTATION_XANGLE': $('#ROTATION_XANGLE').val(), 
            'ROTATION_YANGLE': $('#ROTATION_YANGLE').val(), 
            'ROTATION_ZANGLE': $('#ROTATION_ZANGLE').val(), 
        };
        $.ajax({
            type: "POST",
            url: "/rotateMoleculeForm",
            data: formData,
            success: function(response) {
                alert(response);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(textStatus, errorThrown);
            }
        });
      });*/

      $('#moleculeRotationFormSubmit').click(function() {
        var formData = $('form[name="rotateMoleculeForm"]').serialize();
        var formData = {
            'ROTATION_ANGLE': $('#ROTATION_ANGLE').val(), 
            
        };
        var dropdownVal = $('#rotateDropdown').val()
        $.ajax({
            type: "POST",
            url: "/rotateMoleculeForm",
            data: {fData: formData, dropdownV: dropdownVal},
            dataType: 'text',
            success: function(response) {
                if(response){
                    $('#rotateSVGImg').html('');
                    $('#rotateSVGImg').html(response);
                    alert("Molecule is now rotated.");

                }
            },
            error: function(jqXHR, text, errorText) {
                alert("Molecule is not rotated. Make sure to select a molecule and fill in form");
                console.log(text, errorText);
            }
        });
      });

});
