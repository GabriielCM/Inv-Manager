// script.js - Funções JavaScript para o Sistema de Gestão de Inventário

document.addEventListener('DOMContentLoaded', function() {
    // Habilitar tooltips do Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Tempo para esconder mensagens flash automaticamente após 5 segundos
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-info)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Adicionar manipuladores de eventos para inputs de busca para permitir pressionar Enter
    var searchInputs = document.querySelectorAll('input[type="text"].form-control');
    searchInputs.forEach(function(input) {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                var searchButton = document.getElementById('aplicarFiltro');
                if (searchButton) {
                    searchButton.click();
                }
            }
        });
    });
    
    // Formatar campos numéricos com separador de milhares
    function formatarNumeros() {
        var elementos = document.querySelectorAll('.numero-formatado');
        elementos.forEach(function(elemento) {
            var valor = parseFloat(elemento.innerText.replace(/[^\d,-]/g, '').replace(',', '.'));
            if (!isNaN(valor)) {
                elemento.innerText = valor.toLocaleString('pt-BR', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                });
            }
        });
    }
    
    // Chamar a função de formatação quando a página é carregada
    formatarNumeros();
});

// Função para confirmar ações de exclusão
function confirmarExclusao(mensagem) {
    return confirm(mensagem || 'Tem certeza que deseja excluir este item?');
}

// Função para aplicar filtros de busca
function aplicarFiltros(baseUrl) {
    const codigo = document.getElementById('codigoFiltro')?.value || '';
    const material = document.getElementById('materialFiltro')?.value || '';
    const apenasDiferencas = document.getElementById('apenasComDiferenca')?.checked || false;
    
    let url = baseUrl + '?';
    
    if (codigo) {
        url += 'codigo=' + encodeURIComponent(codigo) + '&';
    }
    
    if (material) {
        url += 'material=' + encodeURIComponent(material) + '&';
    }
    
    if (apenasDiferencas) {
        url += 'apenas_diferencas=true';
    }
    
    window.location.href = url;
    return false;
}

// Função para validar campos numéricos
function validarCampoNumerico(input) {
    let value = input.value;
    
    // Remover tudo, exceto números, vírgulas e pontos
    value = value.replace(/[^\d,.]/g, '');
    
    // Certificar-se de que há apenas um separador decimal
    let countDots = (value.match(/\./g) || []).length;
    let countCommas = (value.match(/,/g) || []).length;
    
    if (countDots > 1 || countCommas > 1 || (countDots >= 1 && countCommas >= 1)) {
        // Se houver mais de um separador, limpar os extras
        let firstSeparatorIndex = Math.min(
            value.indexOf('.') !== -1 ? value.indexOf('.') : Infinity,
            value.indexOf(',') !== -1 ? value.indexOf(',') : Infinity
        );
        
        if (firstSeparatorIndex !== Infinity) {
            let beforeSeparator = value.substring(0, firstSeparatorIndex);
            let separator = value.charAt(firstSeparatorIndex);
            let afterSeparator = value.substring(firstSeparatorIndex + 1).replace(/[,.]/g, '');
            value = beforeSeparator + separator + afterSeparator;
        }
    }
    
    input.value = value;
    return true;
} 