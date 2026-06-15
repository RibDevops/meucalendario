/**
 * Calendário Dark — JS
 */

if (typeof eventoAtualId === 'undefined') var eventoAtualId = null;

document.addEventListener('DOMContentLoaded', function () {
    initFormHandlers();
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') fecharTodosModais();
    });
});

// ================================
// NAVEGAÇÃO
// ================================

function selecionarDia(ano, mes, dia) {
    window.location.href = `?ano=${ano}&mes=${mes}&dia=${dia}`;
}

// ================================
// MODAIS
// ================================

function abrirModal(id) {
    document.getElementById('modal-overlay').classList.add('active');
    document.getElementById(id).classList.add('active');
    document.body.style.overflow = 'hidden';
    setTimeout(() => {
        const el = document.getElementById(id);
        const input = el && el.querySelector('input:not([type="hidden"]):not([type="color"]), textarea, select');
        if (input) input.focus();
    }, 120);
}

function fecharModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.remove('active');
    const abertos = document.querySelectorAll('.modal.active');
    if (abertos.length === 0) {
        document.getElementById('modal-overlay').classList.remove('active');
        document.body.style.overflow = '';
        eventoAtualId = null;
    }
}

function fecharTodosModais() {
    document.querySelectorAll('.modal').forEach(m => m.classList.remove('active'));
    const overlay = document.getElementById('modal-overlay');
    if (overlay) overlay.classList.remove('active');
    document.body.style.overflow = '';
    eventoAtualId = null;
}

function fecharPorOverlay(e) {
    if (e.target === document.getElementById('modal-overlay')) fecharTodosModais();
}

// ================================
// CRIAR (WIZARD — 2 ETAPAS)
// ================================

let etapaAtual = 1;
let _dadosEventoPendente = null;

function atualizarWizardUI() {
    const recorrencia = document.getElementById('criar-recorrencia').value;
    const temEtapa3 = (recorrencia && recorrencia !== 'nenhuma');
    const totalEtapas = temEtapa3 ? 3 : 2;

    document.querySelectorAll('.wizard-etapa').forEach(el => el.classList.remove('active'));
    const etapaEl = document.getElementById(`etapa-${etapaAtual}`);
    if (etapaEl) etapaEl.classList.add('active');
    
    document.getElementById('modal-criar-titulo').textContent = `Novo evento (${etapaAtual}/${totalEtapas})`;

    document.getElementById('btn-voltar').style.display = etapaAtual > 1 ? 'block' : 'none';
    document.getElementById('btn-cancelar').style.display = etapaAtual === 1 ? 'block' : 'none';

    const btnProximo = document.getElementById('btn-proximo');
    const btnCriar = document.getElementById('btn-criar');

    if (etapaAtual < totalEtapas) {
        btnProximo.style.setProperty('display', 'block', 'important');
        btnCriar.style.setProperty('display', 'none', 'important');
    } else {
        btnProximo.style.setProperty('display', 'none', 'important');
        btnCriar.style.setProperty('display', 'block', 'important');
    }
}

function proximaEtapa() {
    if (etapaAtual === 1) {
        if (!document.getElementById('criar-titulo').value) {
            return mostrarToast('Por favor, informe o título', 'erro');
        }
        etapaAtual = 2;
        atualizarWizardUI();
        return;
    }

    if (etapaAtual === 2) {
        if (!document.getElementById('criar-data').value || !document.getElementById('criar-hora').value) {
            return mostrarToast('Data e Hora são obrigatórias', 'erro');
        }
        
        const recorrencia = document.getElementById('criar-recorrencia').value;
        if (recorrencia && recorrencia !== 'nenhuma') {
            etapaAtual = 3;
            atualizarWizardUI();
        } else {
            submitCriar(formParaJson(document.getElementById('form-criar')));
        }
        return;
    }
    
    if (etapaAtual === 3) {
        submitCriar(formParaJson(document.getElementById('form-criar')));
    }
}

function voltarEtapa() {
    if (etapaAtual > 1) {
        etapaAtual--;
        atualizarWizardUI();
    }
}

function abrirModalCriar(dataPre, horaPre) {
    const form = document.getElementById('form-criar');
    if (form) form.reset();
    setVal('criar-data', dataPre || formatarDataInput(new Date()));
    setVal('criar-hora', horaPre || '09:00');
    setVal('criar-cor', '#6366f1');
    setVal('criar-categoria', 'geral');

    const colorSelector = document.getElementById('criar-color-selector');
    if (colorSelector) {
        colorSelector.querySelectorAll('.color-option').forEach(el => el.classList.remove('active'));
        colorSelector.querySelector('[data-color="#6366f1"]').classList.add('active');
    }

    etapaAtual = 1;
    const recorrenciaSelect = document.getElementById('criar-recorrencia');
    if (recorrenciaSelect) recorrenciaSelect.value = 'nenhuma';

    atualizarWizardUI();
    abrirModal('modal-criar');
}

function submitCriar(formData) {
    _enviarCriar(formData);
}

function _enviarCriar(formData) {
    fetchJson(window.URL_CRIAR, 'POST', formData, function (data) {
        if (data.sucesso) {
            mostrarToast(data.mensagem || 'Evento criado!', 'sucesso');
            fecharTodosModais();
            setTimeout(() => window.location.reload(), 500);
        } else {
            mostrarToast(data.mensagem || 'Erro ao criar evento', 'erro');
        }
    });
}

// ================================
// DETALHE
// ================================

function abrirModalDetalhe(id) {
    eventoAtualId = id;
    fetchJson(urlComId(window.URL_DETALHES_BASE, id), 'GET', null, function (data) {
        if (!data.sucesso) return mostrarToast('Erro ao carregar evento', 'erro');
        const ev = data.evento;
        window.EVENTO_ATUAL_DATA = ev; // Salva para uso na edição/exclusão
        document.getElementById('detalhe-titulo').textContent = ev.titulo;
        const corpo = document.getElementById('detalhe-corpo');
        const dataFmt = formatarDataExibicao(ev.data);
        const catFmt = ev.categoria.charAt(0).toUpperCase() + ev.categoria.slice(1);
        corpo.innerHTML = `
            <div class="detalhe-row">
                ${iconeSvg('clock')}
                <div class="detalhe-valor">${dataFmt} às ${ev.hora}</div>
            </div>
            <div class="detalhe-row">
                ${iconeSvg('tag')}
                <div class="detalhe-valor">${catFmt}</div>
            </div>
            ${ev.responsavel ? `
            <div class="detalhe-row">
                ${iconeSvg('user')}
                <div class="detalhe-valor">${ev.responsavel}</div>
            </div>` : ''}
            ${ev.serie_id ? `<div class="detalhe-row" style="opacity: 0.6; font-size: 11px; margin-top: 8px;">Evento Recorrente</div>` : ''}
        `;
        abrirModal('modal-detalhe');
    });
}

function abrirModalEditarDoDetalhe() {
    if (!eventoAtualId) return;
    const id = eventoAtualId;
    fecharModal('modal-detalhe');
    setTimeout(() => abrirModalEditar(id), 150);
}

function abrirModalExcluirDoDetalhe() {
    if (!eventoAtualId) return;
    const id = eventoAtualId;
    fecharModal('modal-detalhe');
    setTimeout(() => abrirModalExcluir(id), 150);
}

// ================================
// EDITAR
// ================================

function abrirModalEditar(id) {
    eventoAtualId = id;
    fetchJson(urlComId(window.URL_DETALHES_BASE, id), 'GET', null, function (data) {
        if (!data.sucesso) return mostrarToast('Erro ao carregar evento', 'erro');
        const ev = data.evento;
        setVal('editar-id',          ev.id);
        setVal('editar-titulo',      ev.titulo);
        setVal('editar-data',        ev.data);
        setVal('editar-hora',        ev.hora);
        setVal('editar-responsavel', ev.responsavel || '');
        setVal('editar-categoria',   ev.categoria || 'geral');
        setVal('editar-cor',         ev.cor || '#6366f1');
        
        const opcoesSerie = document.getElementById('opcoes-serie');
        if (ev.serie_id && opcoesSerie) {
            opcoesSerie.style.display = 'block';
            const check = document.getElementById('editar-serie-check');
            if (check) check.checked = false;
        } else if (opcoesSerie) {
            opcoesSerie.style.display = 'none';
        }

        abrirModal('modal-editar');
    });
}

function submitEditar(id, formData) {
    fetchJson(urlComId(window.URL_EDITAR_BASE, id), 'POST', formData, function (data) {
        if (data.sucesso) {
            mostrarToast(data.mensagem || 'Evento atualizado!', 'sucesso');
            fecharModal('modal-editar');
            setTimeout(() => window.location.reload(), 500);
        } else {
            mostrarToast(data.mensagem || 'Erro ao salvar evento', 'erro');
        }
    });
}

// ================================
// EXCLUIR
// ================================

function abrirModalExcluir(id) {
    eventoAtualId = id;
    fetchJson(urlComId(window.URL_DETALHES_BASE, id), 'GET', null, function (data) {
        if (data.sucesso) {
            const ev = data.evento;
            const el = document.getElementById('excluir-titulo');
            if (el) el.textContent = '"' + ev.titulo + '"';
            
            const opcoesExcluirSerie = document.getElementById('opcoes-excluir-serie');
            if (ev.serie_id && opcoesExcluirSerie) {
                opcoesExcluirSerie.style.display = 'block';
                const check = document.getElementById('excluir-serie-check');
                if (check) check.checked = false;
            } else if (opcoesExcluirSerie) {
                opcoesExcluirSerie.style.display = 'none';
            }

            abrirModal('modal-excluir');
        }
    });
}

function confirmarExclusao() {
    if (!eventoAtualId) return;
    const check = document.getElementById('excluir-serie-check');
    const excluirSerie = check ? check.checked : false;
    const payload = { excluir_serie: excluirSerie };

    fetchJson(urlComId(window.URL_EXCLUIR_BASE, eventoAtualId), 'POST', payload, function (data) {
        if (data.sucesso) {
            mostrarToast(data.mensagem || 'Evento excluído!', 'sucesso');
            fecharModal('modal-excluir');
            setTimeout(() => window.location.reload(), 500);
        } else {
            mostrarToast(data.mensagem || 'Erro ao excluir', 'erro');
        }
    });
}

// ================================
// UTILITÁRIOS
// ================================

function selecionarCor(elemento, prefix) {
    // Remover classe active de todas as opções no seletor atual
    const selector = elemento.parentElement;
    selector.querySelectorAll('.color-option').forEach(el => el.classList.remove('active'));
    
    // Adicionar active na opção clicada
    elemento.classList.add('active');
    
    // Atualizar o valor do input hidden
    const cor = elemento.getAttribute('data-color');
    document.getElementById(`${prefix}-cor`).value = cor;
}

function initFormHandlers() {
    const formCriar = document.getElementById('form-criar');
    if (formCriar) {
        formCriar.addEventListener('submit', function (e) {
            e.preventDefault();
            if (etapaAtual >= 2) {
                submitCriar(formParaJson(this));
            }
        });
    }

    const formEditar = document.getElementById('form-editar');
    if (formEditar) {
        formEditar.addEventListener('submit', function (e) {
            e.preventDefault();
            const id = getVal('editar-id');
            if (id) submitEditar(id, formParaJson(this));
        });
    }
}

// ================================
// TOAST
// ================================

function mostrarToast(msg, tipo = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const icones = {
        sucesso: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>',
        erro:    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>',
        info:    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line></svg>'
    };
    const toast = document.createElement('div');
    toast.className = `toast toast-${tipo}`;
    toast.innerHTML = (icones[tipo] || icones.info) + `<span>${msg}</span>`;
    container.appendChild(toast);
    toast.offsetHeight;
    requestAnimationFrame(() => toast.classList.add('show'));
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ================================
// HELPERS
// ================================

function getCsrfToken() {
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? m[1] : '';
}

function fetchJson(url, method, body, callback) {
    const opts = {
        method,
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() }
    };
    if (body && method !== 'GET') opts.body = JSON.stringify(body);
    fetch(url, opts)
        .then(r => r.json())
        .then(callback)
        .catch(err => { console.error(err); mostrarToast('Erro de conexão', 'erro'); });
}

function formParaJson(form) {
    const json = {};
    new FormData(form).forEach((v, k) => { json[k] = v; });
    return json;
}

function urlComId(base, id) { return base.replace('/0/', `/${id}/`); }
function setVal(id, val) { const el = document.getElementById(id); if (el) el.value = val; }
function getVal(id) { const el = document.getElementById(id); return el ? el.value : null; }

function formatarDataInput(d) {
    return d.getFullYear() + '-'
        + String(d.getMonth() + 1).padStart(2, '0') + '-'
        + String(d.getDate()).padStart(2, '0');
}

function formatarDataExibicao(iso) {
    const [ano, mes, dia] = iso.split('-');
    const meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];
    return `${parseInt(dia)} de ${meses[parseInt(mes) - 1]}. de ${ano}`;
}

function iconeSvg(tipo) {
    const icons = {
        clock: '<svg class="detalhe-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>',
        user:  '<svg class="detalhe-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>',
        tag:   '<svg class="detalhe-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>',
    };
    return icons[tipo] || '';
}
