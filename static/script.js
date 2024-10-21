document.getElementById('generateBtn').addEventListener('click', function() {
    document.getElementById('inputArea').style.display = 'block';
});

document.getElementById('submitBtn').addEventListener('click', function() {
    const empresas = document.getElementById('empresaInput').value;
    document.getElementById('status').innerText = "Gerando planilha, por favor aguarde...";

    fetch('/gerar_planilha', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ empresas: empresas })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('status').innerHTML = `<a href="${data.link}" download>Baixar Planilha</a>`;
    })
    .catch(error => {
        document.getElementById('status').innerText = "Erro ao gerar a planilha.";
    });
});
