let menuVisible = false;
//Función que oculta o muestra el menu
function mostrarOcultarMenu(){
    if(menuVisible){
        document.getElementById("nav").classList ="";
        menuVisible = false;
    }else{
        document.getElementById("nav").classList ="responsive";
        menuVisible = true;
    }
}
function seleccionar(){
    //oculto el menu una vez que selecciono una opcion
    document.getElementById("nav").classList = "";
    menuVisible = false;
}

// Usar localStorage para mantener el carrito entre páginas
let carrito = JSON.parse(localStorage.getItem('carrito')) || [];
let total = parseFloat(localStorage.getItem('total')) || 0;

function actualizarCarrito() {
    const carritoItems = document.getElementById('carrito-items');
    const totalElement = document.getElementById('total');
    const cantidadElement = document.querySelector('.carrito-cantidad');
    
    if (carritoItems) {
        carritoItems.innerHTML = '';
        carrito.forEach((item, index) => {
            const carritoItem = document.createElement('div');
            carritoItem.className = 'carrito-item';
            carritoItem.innerHTML = `
                <span>${item.nombre} - Bs. ${item.precio.toFixed(2)}</span>
                <button onclick="eliminarDelCarrito(${index})">
                    <i class="fa-solid fa-trash"></i>
                </button>
            `;
            carritoItems.appendChild(carritoItem);
        });
    }
    
    if (totalElement) {
        totalElement.textContent = total.toFixed(2);
    }
    
    if (cantidadElement) {
        cantidadElement.textContent = carrito.length;
    }
    
    // Guardar en localStorage
    localStorage.setItem('carrito', JSON.stringify(carrito));
    localStorage.setItem('total', total.toString());
}

function agregarAlCarrito(nombre, precio) {
    carrito.push({ nombre, precio });
    total += precio;
    actualizarCarrito();
    
    // Crear y mostrar el mensaje de confirmación
    const mensaje = document.createElement('div');
    mensaje.className = 'mensaje-confirmacion';
    mensaje.innerHTML = `
        <div class="mensaje-contenido">
            <i class="fa-solid fa-check"></i>
            ${nombre} agregado al carrito
        </div>
    `;
    document.body.appendChild(mensaje);

    // Eliminar el mensaje después de 2 segundos
    setTimeout(() => {
        mensaje.remove();
    }, 2000);
}

function eliminarDelCarrito(index) {
    total -= carrito[index].precio;
    carrito.splice(index, 1);
    actualizarCarrito();
}

function toggleCarrito() {
    const carritoContainer = document.getElementById('carrito-container');
    carritoContainer.classList.toggle('mostrar');
}

function generarBoleta() {
    try {
        let doc;
        
        // Verificar e inicializar jsPDF
        if (typeof window.jspdf !== 'undefined') {
            window.jspdf = window.jspdf.jsPDF;
            doc = new window.jspdf();
        } else if (typeof jsPDF !== 'undefined') {
            doc = new jsPDF();
        } else {
            alert('Error: La librería jsPDF no está cargada correctamente');
            return;
        }
        
        // Encabezado
        doc.setFontSize(22);
        doc.text('SALTEÑERIA CHIKIS', 105, 20, { align: 'center' });
        
        doc.setFontSize(14);
        doc.text('BOLETA DE VENTA', 105, 30, { align: 'center' });
        
        // Fecha
        doc.setFontSize(12);
        doc.text('Fecha: ' + new Date().toLocaleDateString(), 20, 40);
        
        // Encabezados de columnas
        doc.text('Producto', 20, 50);
        doc.text('Precio (Bs.)', 160, 50);
        
        // Línea separadora
        doc.line(20, 55, 190, 55);
        
        // Detalles de los items
        let y = 65;
        
        if (carrito.length === 0) {
            doc.text('No hay items en el carrito', 20, y);
        } else {
            carrito.forEach(item => {
                doc.text(item.nombre, 20, y);
                doc.text(item.precio.toFixed(2), 160, y);
                y += 10;
            });
            
            // Línea separadora antes del total
            doc.line(20, y + 5, 190, y + 5);
            
            // Total
            doc.text(`Total: Bs. ${total.toFixed(2)}`, 160, y + 15);
        }
        
        // Agregar teléfono y mensaje de agradecimiento
        doc.setFontSize(12);
        doc.text('¡Gracias por su compra!', 105, y + 35, { align: 'center' });
        doc.text('Teléfono: 78073688', 105, y + 45, { align: 'center' });
        
        // Guardar PDF
        doc.save('boleta-saltenas-chikis.pdf');
    } catch (error) {
        console.error('Error al generar la boleta:', error);
        alert('Hubo un error al generar la boleta. Por favor, intente nuevamente. Error: ' + error.message);
    }
}

function realizarPedido() {
    if (carrito.length === 0) {
        alert('El carrito está vacío. Agregue productos antes de realizar el pedido.');
        return;
    }
    
    // Crear mensaje de WhatsApp
    let mensaje = "¡Hola! Quisiera hacer un pedido:\n\n";
    carrito.forEach(item => {
        mensaje += `- ${item.nombre}: Bs. ${item.precio.toFixed(2)}\n`;
    });
    mensaje += `\nTotal: Bs. ${total.toFixed(2)}`;
    
    // Número de WhatsApp
    const telefono = "78073688";
    
    // Crear enlace de WhatsApp
    const url = `https://wa.me/${telefono}?text=${encodeURIComponent(mensaje)}`;
    
    try {
        window.open(url, '_blank');
    } catch (error) {
        console.error('Error al abrir WhatsApp:', error);
        alert('Hubo un error al abrir WhatsApp. Por favor, intente nuevamente.');
    }
}

// Actualizar carrito al cargar la página
document.addEventListener('DOMContentLoaded', actualizarCarrito);
// Header scroll effect
(function() {
  var header = document.getElementById('main-header');
  if (!header) return;
  window.addEventListener('scroll', function() {
    header.classList.toggle('scrolled', window.scrollY > 40);
  }, { passive: true });
})();
/* ─────────────────────────────────────────────
   HEADER — Efecto scroll (añadir al existing)
───────────────────────────────────────────── */
(function initHeaderScroll() {
  var header = document.getElementById('main-header');
  if (!header) return;
  window.addEventListener('scroll', function () {
    header.classList.toggle('scrolled', window.scrollY > 40);
  }, { passive: true });
})();


/* ─────────────────────────────────────────────
   VIDEO — Intersection Observer (autoplay/pause)
   Lógica:
   · Entra al viewport  → reproduce en mute
   · Sale del viewport  → pausa y resetea overlay
   · Click en overlay   → reproduce/pausa manual
───────────────────────────────────────────── */
(function initVideoObserver() {
  var video   = document.getElementById('presentacion-video');
  var overlay = document.getElementById('phonePlayOverlay');
  var trigBtn = document.getElementById('videoPlayBtn');

  if (!video) return;

  /* Quita el overlay al iniciar reproducción */
  function hideOverlay() {
    if (overlay) overlay.classList.add('hidden');
  }

  /* Muestra el overlay al pausar */
  function showOverlay() {
    if (overlay) overlay.classList.remove('hidden');
  }

  /* Reproducir desde el botón lateral de texto */
  if (trigBtn) {
    trigBtn.addEventListener('click', function () {
      video.scrollIntoView({ behavior: 'smooth', block: 'center' });
      setTimeout(function () {
        video.play().catch(function () {});
        hideOverlay();
      }, 600);
    });
  }

  /* Click en el overlay del teléfono */
  if (overlay) {
    overlay.addEventListener('click', function () {
      if (video.paused) {
        video.play().catch(function () {});
        hideOverlay();
      } else {
        video.pause();
        showOverlay();
      }
    });
  }

  /* Intersection Observer — umbral del 40 % visible */
  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          /* Entró en pantalla → reproducir (muted garantizado) */
          video.muted = true;
          video.play().then(function () {
            hideOverlay();
          }).catch(function () {
            /* Autoplay bloqueado — dejar overlay visible */
          });
        } else {
          /* Salió de pantalla → pausar */
          if (!video.paused) {
            video.pause();
            showOverlay();
          }
        }
      });
    },
    { threshold: 0.40 }
  );

  observer.observe(video);
})();