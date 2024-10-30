# Gerador de Planilhas de Empresas com Flask

## Descrição
Este projeto é uma aplicação em Flask que permite aos usuários buscar informações de empresas, como nome completo, telefone e endereço, utilizando a API do Google Places. As informações coletadas são organizadas e exportadas em uma planilha Excel formatada, facilitando o controle e análise de dados de empresas.

## Funcionalidades
- **Busca de Dados de Empresas**: Insira o nome de uma empresa para buscar informações detalhadas como endereço e número de telefone, utilizando a integração com a API do Google Places.
- **Geração de Planilhas Excel**: As informações coletadas são automaticamente organizadas em uma planilha Excel para fácil acesso e análise.
- **Interface Intuitiva**: Interface simples e amigável com formulário de entrada para os nomes das empresas, permitindo uma experiência de uso fluida e direta.

## Tecnologias Utilizadas
- **Flask**: Framework web em Python para desenvolvimento da aplicação e criação da interface.
- **Google Places API**: API utilizada para buscar e coletar dados de empresas de maneira automatizada.
- **Pandas e OpenPyXL**: Bibliotecas Python para manipulação e geração de planilhas Excel.
- **HTML, CSS e JavaScript**: Para desenvolvimento da interface web.

## Estrutura do Projeto
- `app.py`: Script principal da aplicação em Flask.
- `planilha.xlsx` e `planilha_atualizada.xlsx`: Exemplos de arquivos de planilhas geradas.
- `README.md`: Documentação do projeto.
- `static/`: Contém arquivos estáticos, como `logo.png`, `script.js` e `styles.css`.
- `templates/index.html`: Template HTML para a interface de usuário.

## Como Usar
1. Clone o repositório:
   ```bash
   git clone https://github.com/lukiin-z/HISAI.git
   cd HISAI
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure sua chave de API do Google Places: No arquivo `app.py`, insira sua chave de API do Google Places para permitir o funcionamento das buscas de dados das empresas. Certifique-se de que sua chave de API esteja ativa e com as permissões necessárias para acessar os dados.
4. Inicie a aplicação:
   ```bash
   python app.py
   ```
5. Acesse a aplicação no navegador: Abra o navegador e vá para `http://localhost:5000` para utilizar a interface do projeto.

## Notas
- **Custos de API**: O uso da API do Google Places pode gerar custos, dependendo do número de requisições. Certifique-se de revisar as políticas de uso e custos da API.
- **Limitações**: A precisão e disponibilidade dos dados dependem das informações fornecidas pela Google Places API.

## Contribuição
Contribuições são bem-vindas! Sinta-se à vontade para abrir *issues* ou enviar *pull requests* com melhorias, correções de bugs ou novas funcionalidades.
