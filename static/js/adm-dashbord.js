$(document).ready(function() {
    // Função para alternar o status de eventos, por exemplo
    $(".change-status").click(function() {
        let status = $(this).data("status");
        $(this).text(status);
    });
});
