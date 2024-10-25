document.getElementById('upload-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Evita o envio padrão do formulário

    const formData = new FormData(this);

    fetch('/upload_planilha', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.link) {
            // Exibe o link de download e oculta o botão de envio
            document.getElementById('download-link').style.display = 'block';
            document.getElementById('status').innerText = "Planilha gerada com sucesso!";
        } else {
            document.getElementById('status').innerText = "Erro ao gerar a planilha.";
        }
    })
    .catch(error => {
        document.getElementById('status').innerText = "Erro ao gerar a planilha.";
        console.error('Erro:', error);
    });
});
