// LUNA ATELIER — App JS
(function(){
'use strict';

// ---- Touch Carousel ----
function initCarousels(){
  document.querySelectorAll('.pdp-carousel').forEach(function(wrap){
    var track = wrap.querySelector('.track');
    if(!track) return;
    var slides = track.children;
    if(slides.length < 2) return;

    var idx = 0, startX = 0, currentX = 0, dragging = false;

    function goTo(i){
      idx = ((i % slides.length) + slides.length) % slides.length;
      track.style.transform = 'translateX(-' + (idx * 100) + '%)';
      var dots = wrap.querySelectorAll('.pdp-dots span');
      dots.forEach(function(d,j){ d.classList.toggle('active',j===idx); });
    }

    function slide(dir){ goTo(idx + dir); }

    // Arrows
    var prev = wrap.querySelector('.pdp-arrow-prev');
    var next = wrap.querySelector('.pdp-arrow-next');
    if(prev) prev.addEventListener('click',function(e){e.stopPropagation();slide(-1);});
    if(next) next.addEventListener('click',function(e){e.stopPropagation();slide(1);});

    // Touch
    track.addEventListener('touchstart',function(e){
      startX = e.touches[0].clientX;
      currentX = startX;
      dragging = true;
      track.style.transition = 'none';
    }, {passive:true});

    track.addEventListener('touchmove',function(e){
      if(!dragging) return;
      currentX = e.touches[0].clientX;
      var diff = currentX - startX;
      var pct = -idx * 100 + (diff / track.offsetWidth * 100);
      track.style.transform = 'translateX(' + pct + '%)';
    }, {passive:true});

    track.addEventListener('touchend',function(){
      if(!dragging) return;
      dragging = false;
      track.style.transition = 'transform .35s cubic-bezier(.25,.46,.45,.94)';
      var diff = currentX - startX;
      if(Math.abs(diff) > track.offsetWidth * 0.2){
        slide(diff < 0 ? 1 : -1);
      } else {
        goTo(idx);
      }
    }, {passive:true});

    // Mouse drag (desktop)
    track.addEventListener('mousedown',function(e){
      startX = e.clientX; currentX = startX; dragging = true;
      track.style.transition = 'none';
    });
    track.addEventListener('mousemove',function(e){
      if(!dragging) return;
      currentX = e.clientX;
      var diff = currentX - startX;
      track.style.transform = 'translateX(' + (-idx * 100 + diff/track.offsetWidth*100) + '%)';
    });
    track.addEventListener('mouseup',function(){
      if(!dragging) return;
      dragging = false;
      track.style.transition = 'transform .35s cubic-bezier(.25,.46,.45,.94)';
      var diff = currentX - startX;
      if(Math.abs(diff) > track.offsetWidth * 0.2){ slide(diff < 0 ? 1 : -1); }
      else { goTo(idx); }
    });
    track.addEventListener('mouseleave',function(){
      if(!dragging) return;
      dragging = false;
      track.style.transition = 'transform .35s cubic-bezier(.25,.46,.45,.94)';
      goTo(idx);
    });
  });
}

// ---- Qty Stepper ----
function initQty(){
  document.querySelectorAll('.qty-bar').forEach(function(bar){
    var val = bar.querySelector('.val');
    var dec = bar.querySelector('.qty-dec');
    var inc = bar.querySelector('.qty-inc');
    if(!val || !dec || !inc) return;
    dec.addEventListener('click',function(){
      var v = parseInt(val.textContent) || 1;
      if(v > 1) val.textContent = v - 1;
    });
    inc.addEventListener('click',function(){
      var v = parseInt(val.textContent) || 1;
      val.textContent = v + 1;
    });
  });
}

// ---- Size Select ----
function initSize(){
  document.querySelectorAll('.size-grid').forEach(function(grid){
    grid.addEventListener('click',function(e){
      var btn = e.target.closest('.size-btn');
      if(!btn) return;
      grid.querySelectorAll('.size-btn').forEach(function(b){ b.classList.remove('active'); });
      btn.classList.add('active');
      var hidden = grid.parentElement.querySelector('input[name="size"]');
      if(hidden) hidden.value = btn.textContent.trim();
    });
  });
}

// ---- Swatch Select ----
function initSwatches(){
  document.querySelectorAll('.swatch-row').forEach(function(row){
    row.addEventListener('click',function(e){
      var sw = e.target.closest('.swatch-circle');
      if(!sw || sw.classList.contains('active')) return;
      row.querySelectorAll('.swatch-circle').forEach(function(s){ s.classList.remove('active'); });
      sw.classList.add('active');
      var hidden = row.parentElement.querySelector('input[name="color"]');
      if(hidden) hidden.value = sw.getAttribute('data-color') || '';
    });
  });
}

// ---- Order Form: single/multi mode ----
function initOrderForm(){
  var form = document.getElementById('orderForm');
  if(!form) return;

  var modeRadios = form.querySelectorAll('input[name="order_mode"]');
  var singleSection = document.getElementById('singleModeFields');
  var multiSection = document.getElementById('multiModeFields');
  var swatchList = document.getElementById('swatchList');
  var itemsField = document.getElementById('itemsField');
  var totalQty = document.getElementById('totalQty');

  if(modeRadios.length) modeRadios.forEach(function(r){
    r.addEventListener('change',function(){
      if(this.value === 'single'){
        if(singleSection) singleSection.style.display = 'block';
        if(multiSection) multiSection.style.display = 'none';
      } else {
        if(singleSection) singleSection.style.display = 'none';
        if(multiSection) multiSection.style.display = 'block';
      }
    });
  });
}

// ---- Confirm Receipt ----
function initConfirm(){
  document.querySelectorAll('.confirm-form').forEach(function(f){
    f.addEventListener('submit',function(e){
      if(!confirm('确认收货后订单将标记为已完成，确定吗？')) e.preventDefault();
    });
  });
}

// ---- Init on DOM ready ----
document.addEventListener('DOMContentLoaded',function(){
  initCarousels();
  initQty();
  initSize();
  initSwatches();
  initOrderForm();
  initConfirm();
});

})();
