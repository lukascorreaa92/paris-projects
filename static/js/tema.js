// ============================================================
// Tema claro / escuro
// ============================================================

// 1) Roda assim que o arquivo carrega (ainda no <head>), ANTES de a página
//    aparecer. Assim ela já nasce com o tema certo, sem "piscar" branco.
(function () {
    let salvo = null;
    try {
        salvo = localStorage.getItem("tema");  // "claro", "escuro" ou null
    } catch (erro) {
        // alguns navegadores bloqueiam o localStorage; seguimos sem ele
    }

    // Sem escolha salva? Usa a preferência do sistema operacional.
    const sistemaEscuro = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const tema = salvo || (sistemaEscuro ? "escuro" : "claro");

    document.documentElement.setAttribute("data-tema", tema);
})();

// 2) Chamada pelo botão: troca o tema e guarda a escolha.
function alternarTema() {
    const atual = document.documentElement.getAttribute("data-tema");
    const novo = atual === "escuro" ? "claro" : "escuro";

    document.documentElement.setAttribute("data-tema", novo);
    try {
        localStorage.setItem("tema", novo);
    } catch (erro) {}
}
