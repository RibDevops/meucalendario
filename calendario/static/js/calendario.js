/**
 * Calendário - Sistema de Agendamento
 * JavaScript para interatividade do calendário
 */

// Variáveis globais
let eventoAtualId = null;
let calendarioData = {
    ano: new Date().getFullYear(),
    mes: new Date().getMonth() + 1,
    dia: new Date().getDate()
};

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    inicializarEventListeners();
    inicializarTooltips();
    inicializarAtalhosTeclado();
});

// ================================
// INICIALIZAÇÃO
// ================================

function inicializarEventListeners() {
    // Delegação de eventos para botões de editar/excluir
    document.addEventListener('click', function(e) {
        const btnEditar = e.target.closest('.btn-editar-evento');
        const btnExcluir = e.target.closest('.btn-excluir-evento');
        
        if (btnEditar) {
            e.preventDefault();
            const id = btnEditar.dataset.id;
            abrirModalEditar(id);
        }
        
        if (btnExcluir) {
            e.preventDefault();
            const id = btnExcluir.dataset.id;
            abrirModalExcluir(id);
        }
    });
}

function inicializarTooltips() {
    // Tooltips são CSS-only via :hover
}

function inicializarAtalhosTeclado() {
    document.addEventListener('keydown', function(e) {
        // ESC fecha modais
        if (e.key === 'Escape') {
            fecharTodosModais();
        }
        
        // Ctrl+N novo evento
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            abrirModalCriar();
        }
    });
}

// ================================
// UTILIDADES
// ================================

function getCsrfToken() {
    const cookie = document.cookie.match(/csrftoken=([^;]+)/);
    return cookie ? cookie[1] : '';
}

function formatarData(data) {
    const d = new Date(data);
    return d.toLocaleDateString('pt-BR', {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });
}

function formatarHora(hora) {
    return hora.substring(0, 5);
}

// ================================
// MODAIS - ABERTURA E FECHAMENTO
// ================================

function abrirModal(modalId) {
    const overlay = document.getElementById('modal-overlay');
    const modal = document.getElementById(modalId);
    
    if (overlay && modal) {
        overlay.classList.add('active');
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Focar no primeiro input
        setTimeout(() => {
            const primeiroInput = modal.querySelector('input:not([type="hidden"]), textarea, select');
            if (primeiroInput) primeiroInput.focus();
        }, 100);
    }
}

function fecharModal(modalId) {
    const overlay = document.getElementById('modal-overlay');
    const modal = document.getElementById(modalId);
    
    if (overlay && modal) {
        modal.classList.remove('active');
        
        // Verificar se há mais modais abertos
        const modaisAbertos = document.querySelectorAll('.modal.active');
        if (modaisAbertos.length === 0) {
            overlay.classList.remove('active');
            document.body.style.overflow = '';
        }
        
        eventoAtualId = null;
    }
}

function fecharTodosModais() {
    const overlay = document.getElementById('modal-overlay');
    const modais = document.querySelectorAll('.modal');
    
    modais.forEach(modal => modal.classList.remove('active'));
    if (overlay) overlay.classList.remove('active');
    document.body.style.overflow = '';
    eventoAtualId = null;
}

// ================================
// CRIAR EVENTO
// ================================

function abrirModalCriar(dataPredefinida, horaPredefinida) {
    // Limpar formulário
    const form = document.getElementById('form-criar');
    if (form) form.reset();
    
    // Definir valores padrão
    const hoje = new Date();
    const data = dataPredefinida || formatarDataInput(hoje);
    const hora = horaPredefinida || '09:00';
    
    const campoData = document.getElementById('criar-data');
    const campoHora = document.getElementById('criar-hora');
    
    if (campoData) campoData.value = data;
    if (campoHora) campoHora.value = hora;
    
    abrirModal('modal-criar');
}

function submitCriar(formData) {
    const url = window.URL_CRIAR || '/evento/criar/';
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.sucesso) {
            mostrarToast(data.mensagem || 'Evento criado com sucesso!', 'sucesso');
            fecharModal('modal-criar');
            setTimeout(() => recarregarPagina(), 600);
        } else {
            mostrarToast(data.mensagem || 'Erro ao criar evento', 'erro');
            if (data.erros) {
                mostrarErrosFormulario('form-criar', data.erros);
            }
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        mostrarToast('Erro de conexão ao criar evento', 'erro');
    });
}

// ================================
// EDITAR EVENTO
// ================================

function abrirModalEditar(id) {
    eventoAtualId = id;
    const urlBase = window.URL_DETALHES_BASE || '/evento/0/';
    const url = urlBase.replace('0', id);
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                preencherFormularioEdicao(data.evento);
                abrirModal('modal-editar');
            } else {
                mostrarToast(data.mensagem || 'Erro ao carregar evento', 'erro');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            mostrarToast('Erro de conexão ao carregar evento', 'erro');
        });
}

function preencherFormularioEdicao(evento) {
    const campos = {
        'editar-id': evento.id,
        'editar-titulo': evento.titulo,
        'editar-data': evento.data,
        'editar-hora': evento.hora,
        'editar-duracao': evento.duracao_minutos,
        'editar-tipo': evento.tipo,
        'editar-descricao': evento.descricao || '',
        'editar-local': evento.local || '',
        'editar-responsavel': evento.responsavel || '',
        'editar-email': evento.email || '',
        'editar-telefone': evento.telefone || '',
        'editar-cor': evento.cor || '#111827',
        'editar-notas': evento.notas || ''
    };
    
    Object.entries(campos).forEach(([id, valor]) => {
        const campo = document.getElementById(id);
        if (campo) campo.value = valor;
    });
}

function submitEditar(id, formData) {
    const urlBase = window.URL_EDITAR_BASE || '/evento/0/editar/';
    const url = urlBase.replace('0', id);
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.sucesso) {
            mostrarToast(data.mensagem || 'Evento atualizado com sucesso!', 'sucesso');
            fecharModal('modal-editar');
            setTimeout(() => recarregarPagina(), 600);
        } else {
            mostrarToast(data.mensagem || 'Erro ao atualizar evento', 'erro');
            if (data.erros) {
                mostrarErrosFormulario('form-editar', data.erros);
            }
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        mostrarToast('Erro de conexão ao atualizar evento', 'erro');
    });
}

// ================================
// EXCLUIR EVENTO
// ================================

function abrirModalExcluir(id) {
    eventoAtualId = id;
    const urlBase = window.URL_DETALHES_BASE || '/evento/0/';
    const url = urlBase.replace('0', id);
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                const tituloEl = document.getElementById('excluir-titulo');
                if (tituloEl) tituloEl.textContent = `"${data.evento.titulo}"`;
                abrirModal('modal-excluir');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
        });
}

function confirmarExclusao() {
    if (!eventoAtualId) return;
    
    const urlBase = window.URL_EXCLUIR_BASE || '/evento/0/excluir/';
    const url = urlBase.replace('0', eventoAtualId);
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.sucesso) {
            mostrarToast(data.mensagem || 'Evento excluído com sucesso!', 'sucesso');
            fecharModal('modal-excluir');
            setTimeout(() => recarregarPagina(), 600);
        } else {
            mostrarToast(data.mensagem || 'Erro ao excluir evento', 'erro');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        mostrarToast('Erro de conexão ao excluir evento', 'erro');
    });
}

function excluirEventoAtual() {
    fecharModal('modal-editar');
    setTimeout(() => {
        if (eventoAtualId) {
            abrirModalExcluir(eventoAtualId);
        }
    }, 200);
}

// ================================
// QUICK ADD
// ================================

function abrirModalQuickAdd(data, hora) {
    const form = document.getElementById('form-quick-add');
    if (form) form.reset();
    
    const campoData = document.getElementById('quick-data');
    const campoHora = document.getElementById('quick-hora');
    const display = document.getElementById('quick-data-display');
    
    if (campoData) campoData.value = data;
    if (campoHora) campoHora.value = hora;
    
    if (display) {
        const dataObj = new Date(data + 'T00:00:00');
        const opcoes = { weekday: 'long', day: 'numeric', month: 'long' };
        display.textContent = dataObj.toLocaleDateString('pt-BR', opcoes) + ' às ' + hora;
    }
    
    abrirModal('modal-quick-add');
}

function submitQuickAdd(formData) {
    const url = window.URL_QUICK_ADD || '/evento/quick-add/';
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.sucesso) {
            mostrarToast(data.mensagem || 'Agendado com sucesso!', 'sucesso');
            fecharModal('modal-quick-add');
            setTimeout(() => recarregarPagina(), 600);
        } else {
            mostrarToast(data.mensagem || 'Erro ao agendar', 'erro');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        mostrarToast('Erro de conexão ao agendar', 'erro');
    });
}

// ================================
// FORMULÁRIOS
// ================================

function initFormHandlers() {
    // Form Criar
    const formCriar = document.getElementById('form-criar');
    if (formCriar) {
        formCriar.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = formDataParaJson(this);
            submitCriar(formData);
        });
    }
    
    // Form Editar
    const formEditar = document.getElementById('form-editar');
    if (formEditar) {
        formEditar.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = formDataParaJson(this);
            const id = document.getElementById('editar-id')?.value;
            if (id) submitEditar(id, formData);
        });
    }
    
    // Form Quick Add
    const formQuick = document.getElementById('form-quick-add');
    if (formQuick) {
        formQuick.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = formDataParaJson(this);
            submitQuickAdd(formData);
        });
    }
}

function formDataParaJson(form) {
    const formData = new FormData(form);
    const jsonData = {};
    formData.forEach((value, key) => {
        jsonData[key] = value;
    });
    return jsonData;
}

function mostrarErrosFormulario(formId, erros) {
    // Limpar erros anteriores
    const form = document.getElementById(formId);
    if (!form) return;
    
    form.querySelectorAll('.erro-campo').forEach(el => el.remove());
    form.querySelectorAll('.input-erro').forEach(el => el.classList.remove('input-erro'));
    
    // Mostrar novos erros
    Object.entries(erros).forEach(([campo, mensagem]) => {
        const input = form.querySelector(`[name="${campo}"]`);
        if (input) {
            input.classList.add('input-erro');
            const erroEl = document.createElement('span');
            erroEl.className = 'erro-campo';
            erroEl.textContent = mensagem;
            input.parentNode.appendChild(erroEl);
        }
    });
}

// ================================
// NAVEGAÇÃO
// ================================

function selecionarDia(ano, mes, dia) {
    window.location.href = `?ano=${ano}&mes=${mes}&dia=${dia}`;
}

function navegarMes(direcao) {
    let { ano, mes } = calendarioData;
    mes += direcao;
    if (mes > 12) { mes = 1; ano++; }
    if (mes < 1) { mes = 12; ano--; }
    window.location.href = `?ano=${ano}&mes=${mes}&dia=1`;
}

function toggleView(view) {
    document.querySelectorAll('.btn-toggle').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === view);
    });
}

// ================================
// TOAST NOTIFICATIONS
// ================================

function mostrarToast(mensagem, tipo = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const icones = {
        sucesso: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>',
        erro: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>',
        info: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${tipo}`;
    toast.innerHTML = `${icones[tipo] || icones.info}<span>${mensagem}</span>`;
    
    container.appendChild(toast);
    
    // Trigger reflow
    toast.offsetHeight;
    
    requestAnimationFrame(() => {
        toast.classList.add('show');
    });
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ================================
// UTILITÁRIOS
// ================================

function formatarDataInput(date) {
    const ano = date.getFullYear();
    const mes = String(date.getMonth() + 1).padStart(2, '0');
    const dia = String(date.getDate()).padStart(2, '0');
    return `${ano}-${mes}-${dia}`;
}

function recarregarPagina() {
    window.location.reload();
}

function atualizarEstatisticas() {
    // Contadores atualizados via template
}

// ================================
// API - EVENTOS JSON
// ================================

function carregarEventosJSON(ano, mes) {
    const url = `/eventos/json/?ano=${ano}&mes=${mes}`;
    
    return fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.sucesso) {
                return data.eventos;
            }
            return [];
        })
        .catch(error => {
            console.error('Erro ao carregar eventos:', error);
            return [];
        });
}

// Inicializar handlers de formulário quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', initFormHandlers);
