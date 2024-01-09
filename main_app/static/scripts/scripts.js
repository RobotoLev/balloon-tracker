$(document).ready(function() {
    $('.order-done').bind('click', function(){
        if (confirm('Вы уверены, что шарик доставлен?')) {
            order_id = $(this).data("order");
            if (order_id > 0) {
                var csrftoken = getCookie('csrftoken');

                $.ajax({
                    url: '/order-done/' + order_id,
                    method: 'POST',
                    dataType: 'html',
                    data: {'csrfmiddlewaretoken': csrftoken},
                    success: function(data){
                        location.reload();
                    }
                });
            }
        }
    });

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
