var preguntas = [];
var indiceActual = 0;
var respuestasUsuario = {};

document.addEventListener("DOMContentLoaded", function() {
    fetch('/api/preguntas')
        .then(function(res) { return res.json(); })
        .then(function(data) {
            if (data.status === 'ok' && data.preguntas.length > 0) {
                preguntas = data.preguntas;
                construirSeccionesEstaticas();
                renderizarPregunta();
            } else {
                document.getElementById('txt-pregunta').innerText = "Error al cargar las preguntas.";
            }
        })
        .catch(function(err) {
            console.error(err);
            document.getElementById('txt-pregunta').innerText = "Error de conexión.";
        });
});

function construirSeccionesEstaticas() {
    var seccionesUnicas = [];
    preguntas.forEach(function(p) {
        if (seccionesUnicas.indexOf(p.seccion) === -1) {
            seccionesUnicas.push(p.seccion);
        }
    });

    var htmlSecciones = '';
    seccionesUnicas.forEach(function(sec) {
        var secCleanId = sec.replace(/[^a-zA-Z0-9]/g, '');
        htmlSecciones += '<div class="seccion-item" id="sec-' + secCleanId + '">' +
            '<div class="indicador-circulo"></div>' +
            '<span>' + sec + '</span>' +
            '</div>';
    });
    document.getElementById('lista-secciones').innerHTML = htmlSecciones;
}

function renderizarPregunta() {
    var p = preguntas[indiceActual];

    document.getElementById('txt-progreso-num').innerText = "Pregunta " + (indiceActual + 1) + " de " + preguntas.length;
    document.getElementById('txt-pregunta').innerText = p.numero + ". " + p.texto;

    var porcentaje = ((indiceActual + 1) / preguntas.length) * 100;
    document.getElementById('barra-progreso').style.width = porcentaje + "%";

    var itemsSec = document.querySelectorAll('.seccion-item');
    itemsSec.forEach(function(i) { i.classList.remove('activa'); });

    var secCleanId = p.seccion.replace(/[^a-zA-Z0-9]/g, '');
    var itemActivo = document.getElementById("sec-" + secCleanId);
    if (itemActivo) itemActivo.classList.add('activa');

    var tarjetas = document.querySelectorAll('.opcion-card');
    tarjetas.forEach(function(c) { c.classList.remove('seleccionada'); });

    if (respuestasUsuario[p.id]) {
        var opcionPrevia = respuestasUsuario[p.id].opcion;
        tarjetas.forEach(function(c) {
            if (c.innerText.trim() === opcionPrevia) {
                c.classList.add('seleccionada');
            }
        });
        document.getElementById('btn-siguiente').disabled = false;
    } else {
        document.getElementById('btn-siguiente').disabled = true;
    }

    document.getElementById('btn-anterior').disabled = (indiceActual === 0);

    var btnSig = document.getElementById('btn-siguiente');
    if (indiceActual === preguntas.length - 1) {
        btnSig.innerHTML = '<span>Ver Resultado</span> <i class="bi bi-check-lg"></i>';
    } else {
        btnSig.innerHTML = '<span>Siguiente</span> <i class="bi bi-chevron-right"></i>';
    }
}

function seleccionarOpcion(opcionTexto) {
    var p = preguntas[indiceActual];
    var puntosObtenidos = p.puntos[opcionTexto];

    respuestasUsuario[p.id] = {
        opcion: opcionTexto,
        puntos: puntosObtenidos
    };

    var tarjetas = document.querySelectorAll('.opcion-card');
    tarjetas.forEach(function(c) {
        c.classList.remove('seleccionada');
        if (c.innerText.trim() === opcionTexto) {
            c.classList.add('seleccionada');
        }
    });

    document.getElementById('btn-siguiente').disabled = false;
}

function siguientePregunta() {
    if (indiceActual < preguntas.length - 1) {
        indiceActual++;
        renderizarPregunta();
    } else {
        finalizarEvaluacion();
    }
}

function anteriorPregunta() {
    if (indiceActual > 0) {
        indiceActual--;
        renderizarPregunta();
    }
}

function finalizarEvaluacion() {
    var puntajeTotal = 0;
    Object.keys(respuestasUsuario).forEach(function(id) {
        puntajeTotal += respuestasUsuario[id].puntos;
    });

    var resultadoData = {
        puntajeTotal: puntajeTotal,
        respuestas: respuestasUsuario
    };

    localStorage.setItem('veanme_resultado', JSON.stringify(resultadoData));

    fetch('/api/guardar-resultado', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ puntaje: puntajeTotal })
    })
    .then(response => response.json())
    .then(data => {
        window.location.href = '/resultado';
    })
    .catch(error => {
        console.error("Error al guardar:", error);
        window.location.href = '/resultado';
    });
}