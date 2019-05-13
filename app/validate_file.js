$(document).ready(function(){
    $('#validateFileBtn').click(function (){
        var user_output_file = $('.user_output_file').val();
        var dataString = 'user_output_file='+ user_output_file +'';
        $.ajax({
            method: 'POST',
            url: '/validate_file',
            data: dataString,
            contentType: 'application/x-www-form-urlencoded',
            success: function(data) {
                if (data === 'ok') {
                    alert('File ' + user_output_file + ' does not exist.\nYou can continue to the next step.');
                } else if (data === 'empty') {
                    alert('Error!\nPlease input a file name.');
                } else {
                    alert('Error!\nFile ' + user_output_file + ' already exists.\nPlease choose another file name.');
                }
            },
        });
    });
});
